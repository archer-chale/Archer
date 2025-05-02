"""
Alpaca broker component responsible for managing trade and order update streams.
"""
import threading
import os
import json
from typing import List, Set
import time # Added for sleep in stop

from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed
from alpaca.data.models import Trade
from alpaca.trading.stream import TradingStream
from alpaca.trading.models import TradeUpdate

# Import Redis utilities from the custom wrapper
from main.utils.redis import (
    RedisPublisher, RedisSubscriber, CHANNELS, REDIS_HOST_DOCKER, REDIS_PORT, REDIS_DB
)
from ..bots.SCALE_T.common.logging_config import get_logger
from ..bots.SCALE_T.common.constants import ENV_FILE, TRADING_TYPE_TO_KEY_NAME, TradingType
from .constants import MessageType, StreamType # Keep internal constants if needed elsewhere

class AlpacaBroker:
    """Main broker class for managing Alpaca market data and order streams."""

    def __init__(self):
        """Initialize the broker with thread tracking, logging, and Redis connections."""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing AlpacaBroker")

        self._running = False
        self._price_producer_thread = None
        self._order_producer_thread = None
        self._broker_registration_thread = None # Thread for registering tickers

        # Stream configuration
        self._price_stream = None
        self._order_stream = None
        self._subscribed_symbols: Set[str] = set()
        self._api_key = None
        self._secret_key = None
        self._trading_type = None

        # Redis configuration
        self._redis_publisher = None
        self._redis_subscriber = None
        self._redis_host = os.environ.get("REDIS_HOST", REDIS_HOST_DOCKER)
        self._redis_port = int(os.environ.get("REDIS_PORT", REDIS_PORT))
        self._redis_db = int(os.environ.get("REDIS_DB", REDIS_DB))
        self._registration_channel = CHANNELS.BROKER_REGISTRATION

        # Initialize Redis connections
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis Publisher and Subscriber."""
        try:
            self._redis_publisher = RedisPublisher(
                host=self._redis_host, port=self._redis_port, db=self._redis_db
            )
            assert self._redis_publisher.connection.connection.ping() == True, "Failed to ping Redis publisher"
            self.logger.info(f"Redis Publisher connected to {self._redis_host}:{self._redis_port}")

            self._redis_subscriber = RedisSubscriber(
                host=self._redis_host, port=self._redis_port, db=self._redis_db
            )
            assert self._redis_subscriber.connection.connection.ping() == True, "Failed to ping Redis subscriber"
            self.logger.info(f"Redis Subscriber connected to {self._redis_host}:{self._redis_port}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self._redis_publisher = None
            self._redis_subscriber = None

    def configure_api_keys(self, trading_type: TradingType = TradingType.PAPER):
        """Configure API keys based on trading type."""
        key_id_name = TRADING_TYPE_TO_KEY_NAME[trading_type]["KEY_ID_NAME"]
        secret_key_name = TRADING_TYPE_TO_KEY_NAME[trading_type]["SECRET_KEY_NAME"]

        self._api_key = os.environ.get(key_id_name)
        self._secret_key = os.environ.get(secret_key_name)
        self._trading_type = trading_type

        if not self._api_key or not self._secret_key:
            self.logger.error(f"Missing API keys for {trading_type.value} trading. Key ID: {key_id_name}, Secret Key: {secret_key_name}")
            raise ValueError(f"Missing API keys for {trading_type.value} trading")
        self.logger.info(f"API keys configured for {trading_type.value} trading")

    def _publish_to_redis(self, channel_name: str, data: dict):
        """Publish data to a specific Redis channel name using the custom publisher."""
        if not self._redis_publisher:
            self.logger.warning("Redis publisher not connected. Cannot publish message.")
            return

        try:
            # Use the standard publish method, assuming it handles dicts and channel names
            self._redis_publisher.publish(channel_name, data, sender="alpaca_broker")
            self.logger.debug(f"Published to {channel_name}: {data}")
        except Exception as e: # Catch potential errors from the custom publisher
            self.logger.error(f"Failed to publish to Redis channel {channel_name}: {e}")

    async def price_handler(self, data: Trade):
        self.handle_price_update({"price": str(data.price), "symbol": data.symbol, "timestamp": str(data.timestamp)})

    def handle_price_update(self, price_data):
        """Handle incoming price updates and publish to the dynamic ticker channel."""
        self.logger.debug(f"Handling price update: {price_data}")
        ticker = price_data.get("symbol")
        if not ticker:
            self.logger.warning("Price update missing symbol, cannot publish to Redis.")
            return

        channel_name = CHANNELS.get_ticker_channel(ticker)
        message_data = {
            "type": "price",
            "timestamp": price_data.get("timestamp", str(time.time())), # Add timestamp if missing
            "price": price_data.get("price"),
            "volume": price_data.get("volume"), # Include volume if available
            "symbol": ticker # Explicitly include symbol in payload
        }
        if self._redis_publisher:
            self._publish_to_redis(channel_name, message_data)
        else:
            self.logger.warning("Redis publisher not connected. Cannot publish price update.")

    def handle_order_update(self, trade_update: TradeUpdate):
        """Handle incoming order updates and publish to the dynamic ticker channel."""
        self.logger.debug(f"Handling order update: {trade_update}")
        ticker = trade_update.order.symbol
        if not ticker:
            self.logger.warning("Order update missing symbol, cannot publish to Redis.")
            return

        channel_name = CHANNELS.get_ticker_channel(ticker)
        # Convert TradeUpdate object to a dictionary suitable for the schema
        order_data_dict = {
             "event": trade_update.event,
             "execution_id": str(trade_update.execution_id) if trade_update.execution_id else None,
             "order": {
                 "id": str(trade_update.order.id),
                 "client_order_id": trade_update.order.client_order_id,
                 "created_at": str(trade_update.order.created_at),
                 "updated_at": str(trade_update.order.updated_at),
                 "submitted_at": str(trade_update.order.submitted_at),
                 "filled_at": str(trade_update.order.filled_at) if trade_update.order.filled_at else None,
                 "expired_at": str(trade_update.order.expired_at) if trade_update.order.expired_at else None,
                 "canceled_at": str(trade_update.order.canceled_at) if trade_update.order.canceled_at else None,
                 "failed_at": str(trade_update.order.failed_at) if trade_update.order.failed_at else None,
                 "replaced_at": str(trade_update.order.replaced_at) if trade_update.order.replaced_at else None,
                 "replaced_by": str(trade_update.order.replaced_by) if trade_update.order.replaced_by else None,
                 "replaces": str(trade_update.order.replaces) if trade_update.order.replaces else None,
                 "asset_id": str(trade_update.order.asset_id),
                 "symbol": trade_update.order.symbol,
                 "asset_class": trade_update.order.asset_class.value,
                 "notional": str(trade_update.order.notional) if trade_update.order.notional else None,
                 "qty": str(trade_update.order.qty) if trade_update.order.qty else None,
                 "filled_qty": str(trade_update.order.filled_qty),
                 "filled_avg_price": str(trade_update.order.filled_avg_price) if trade_update.order.filled_avg_price else None,
                 "order_class": trade_update.order.order_class.value,
                 "order_type": trade_update.order.order_type.value,
                 "side": trade_update.order.side.value,
                 "time_in_force": trade_update.order.time_in_force.value,
                 "limit_price": str(trade_update.order.limit_price) if trade_update.order.limit_price else None,
                 "stop_price": str(trade_update.order.stop_price) if trade_update.order.stop_price else None,
                 "status": trade_update.order.status.value,
                 "extended_hours": trade_update.order.extended_hours,
                 "legs": None,
                 "trail_percent": str(trade_update.order.trail_percent) if trade_update.order.trail_percent else None,
                 "trail_price": str(trade_update.order.trail_price) if trade_update.order.trail_price else None,
                 "hwm": str(trade_update.order.hwm) if trade_update.order.hwm else None,
                 "source": "alpaca"
             },
             "timestamp": str(trade_update.timestamp),
             "position_qty": str(trade_update.position_qty) if trade_update.position_qty else None,
             "price": str(trade_update.price) if trade_update.price else None,
             "qty": str(trade_update.qty) if trade_update.qty else None,
         }
        message_data = {
            "type": "order",
            "timestamp": str(trade_update.timestamp),
            "symbol": ticker, # Explicitly include symbol
            "order_data": order_data_dict
        }
        self._publish_to_redis(channel_name, message_data)

    # --- Alpaca Stream Producers ---
    def _run_price_producer_thread(self):
        """Run the price update producer thread."""
        try:
            self._price_stream = StockDataStream(
                api_key=self._api_key,
                secret_key=self._secret_key,
                feed=DataFeed.IEX # IEX | SIP 
            )

            self.logger.info(f"Price producer subscribing to: {list(self._subscribed_symbols)}")
            self._price_stream.subscribe_trades(
                self.price_handler,
                *list(self._subscribed_symbols)
            )
            self._price_stream.run() # This blocks until stop() is called or an error occurs

        except Exception as e:
            self.logger.error(f"Error in price producer: {e}")
        finally:
            self.logger.info("Price producer thread finished.")


    def _run_order_producer_thread(self):
        """Run the order update producer thread."""
        try:
            self._order_stream = TradingStream(
                api_key=self._api_key,
                secret_key=self._secret_key,
                paper=self._trading_type == TradingType.PAPER
            )

            async def order_handler(data: TradeUpdate):
                self.handle_order_update(data)

            self.logger.info("Order producer subscribing to trade updates.")
            self._order_stream.subscribe_trade_updates(order_handler)
            self._order_stream.run() # This blocks until stop() is called or an error occurs

        except Exception as e:
            self.logger.error(f"Error in order producer: {e}")
        finally:
            self.logger.info("Order producer thread finished.")

    def handle_registration_message(self, message):
        """Handle incoming registration messages from Redis."""
        self.logger.debug(f"Received registration message: {message}")
        print(f"running: {self._running}, price producer thread: {self._price_producer_thread}, price stream: {self._price_stream}")
        if self._running and self._price_producer_thread and self._price_producer_thread.is_alive() and self._price_stream:
            try:
                data = message.get('data', '{}')
                symbol = data.get('ticker')
                action = data.get('action')
                if action == "subscribe":
                    self.subscribe_symbol(symbol)
                elif action == "unsubscribe":
                    self.unsubscribe_symbol(symbol)
                else:
                    self.logger.warning(f"Unknown action in registration message: {action}")
                    return
            except Exception as e:
                self.logger.error(f"Error handling registration message: {e}")
                return
        else:
            self.logger.warning("Price producer thread not running or not alive. Dumping message.")

        

    # --- Symbol Subscription Management ---
    def subscribe_symbol(self, symbol: str):
        """Subscribe to price updates for given symbols."""
        symbol = symbol.upper()
        if symbol in self._subscribed_symbols:
            self.logger.debug(f"Symbol {symbol} already subscribed.")
            return
        
        self._subscribed_symbols.add(symbol)
        self.logger.info(f"Subscribed to price updates for: {symbol}. Current: {self._subscribed_symbols}")
        # Restart price producer thread if running to include new symbols
        if self._running and self._price_stream:
            self._price_stream.subscribe_trades(
                self.price_handler,
                symbol
            )
            self.logger.info(f"Subscribed to price updates for: {symbol} in Alpaca stream.")
        else:
            self.logger.info("Price producer not running, will subscribe when started.")


    def unsubscribe_symbol(self, symbol: str):
        """Unsubscribe from price updates for given symbols."""
        removed_symbol = symbol.upper() if symbol in self._subscribed_symbols else None
        if not removed_symbol:
            self.logger.debug(f"Symbol: {symbol} not currently subscribed or invalid.")
            return

        print(f"Is it in subscribed symbols? {removed_symbol}")
        print(f"Before removing symbol from subscribed symbols: {self._subscribed_symbols}")
        res = self._subscribed_symbols.discard(removed_symbol)
        print("Removing symbol from subscribed symbols:", removed_symbol, res)
        print(f"After removing symbol from subscribed symbols: {self._subscribed_symbols}")
        self.logger.info(f"Removed subscriptions for: {removed_symbol}. Current: {self._subscribed_symbols}")

        # Restart price producer thread if running to remove symbols
        if self._running and self._price_stream:
            self._price_stream.unsubscribe_trades(removed_symbol)
            self.logger.info(f"Unsubscribed from price updates for: {removed_symbol}")
        else:
            self.logger.info("Price producer not running, will unsubscribe when started.")

    # --- Start/Stop ---
    def start(self):
        """Start the broker's producer threads and Redis subscriber."""
        if not self._running:
            if not self._api_key or not self._secret_key:
                raise ValueError("API keys must be configured before starting")

            if not self._redis_publisher or not self._redis_subscriber:
                self.logger.error("Cannot start broker without Redis connections.")
                return

            self._running = True
            self.logger.info("Starting producer threads and Redis subscriber")

            # Start price producer (will only run if symbols are subscribed later)
            self._price_producer_thread = threading.Thread(target=self._run_price_producer_thread, daemon=True)
            self._price_producer_thread.start()
            self.logger.info("Price producer thread started (will wait for subscriptions).")


            # Start order producer
            self._order_producer_thread = threading.Thread(target=self._run_order_producer_thread, daemon=True)
            self._order_producer_thread.start()
            self.logger.info("Order producer started")

            try:
                if self._broker_registration_thread and self._broker_registration_thread.is_alive():
                    self.logger.info("Redis subscriber already running. Skipping")
                    return
                self._redis_subscriber.subscribe(self._registration_channel, self.handle_registration_message)
                self._broker_registration_thread = threading.Thread(target=self._redis_subscriber.start_listening, daemon=True)
                self._broker_registration_thread.start()
                self.logger.info(f"Redis subscriber started listening on {self._registration_channel}, worker thread started.")
            except Exception as e:
                 self.logger.error(f"Failed to start Redis subscriber: {e}")
                 self.stop() # Stop everything if subscriber fails to start


    def stop(self):
        """Stop the broker's producer threads and Redis subscriber."""
        if self._running:
            self._running = False # Signal threads to stop. Which threads tho? TODO
            self.logger.info("Stopping broker...")

            if self._redis_subscriber:
                try:
                    self._redis_subscriber.close() # Close connection first
                    self.logger.info("Redis subscriber connection closed.")
                except Exception as e:
                    self.logger.error(f"Error closing Redis subscriber connection: {e}")
            if self._broker_registration_thread and self._broker_registration_thread.is_alive():
                self._redis_subscriber.stop_listening() # Stop listening for messages
                self.logger.info("Redis subscriber stopped listening for messages.")
                self._broker_registration_thread.join(timeout=1.0) # Join after closing connection
                if self._broker_registration_thread.is_alive():
                    self.logger.warning("Redis subscriber thread did not exit cleanly.")
                else:
                    self.logger.info("Redis subscriber thread stopped.")

            # Close Alpaca streams
            price_stream_to_close = self._price_stream
            order_stream_to_close = self._order_stream
            self._price_stream = None # Set to None immediately
            self._order_stream = None # Set to None immediately

            if price_stream_to_close:
                try:
                    price_stream_to_close.close()
                    self.logger.info("Price stream closed.")
                except Exception as e:
                    self.logger.error(f"Error closing price stream: {e}")

            if order_stream_to_close:
                try:
                    order_stream_to_close.close()
                    self.logger.info("Order stream closed.")
                except Exception as e:
                    self.logger.error(f"Error closing order stream: {e}")

            # Join Alpaca producer threads
            if self._price_producer_thread and self._price_producer_thread.is_alive():
                self._price_producer_thread.join(timeout=1.0)
                if self._price_producer_thread.is_alive():
                    self.logger.warning("Price producer thread did not exit cleanly.")
                else:
                    self.logger.info("Price producer thread stopped.")

            if self._order_producer_thread and self._order_producer_thread.is_alive():
                self._order_producer_thread.join(timeout=1.0)
                if self._order_producer_thread.is_alive():
                    self.logger.warning("Order producer thread did not exit cleanly.")
                else:
                    self.logger.info("Order producer thread stopped.")

            # Close Redis publisher connection
            if self._redis_publisher:
                try:
                    self._redis_publisher.close()
                    self.logger.info("Redis publisher connection closed.")
                except Exception as e:
                    self.logger.error(f"Error closing Redis publisher connection: {e}")

            self.logger.info("Broker stopped.")

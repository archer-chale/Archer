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
from main.utils.redis import RedisPublisher, RedisSubscriber, CHANNELS

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
        self._price_producer = None
        self._order_producer = None
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
        self._redis_host = os.environ.get("REDIS_HOST", "localhost")
        self._redis_port = int(os.environ.get("REDIS_PORT", 6379))
        self._redis_db = int(os.environ.get("REDIS_DB", 0))
        self._registration_channel = CHANNELS.BROKER_REGISTRATION

        # Initialize Redis connections
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis Publisher and Subscriber."""
        try:
            self._redis_publisher = RedisPublisher(
                host=self._redis_host, port=self._redis_port, db=self._redis_db
            )
            self._redis_publisher.ping()
            self.logger.info(f"Redis Publisher connected to {self._redis_host}:{self._redis_port}")

            self._redis_subscriber = RedisSubscriber(
                host=self._redis_host, port=self._redis_port, db=self._redis_db
            )
            self._redis_subscriber.ping()
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
        self._publish_to_redis(channel_name, message_data)

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
                 "commission": str(trade_update.order.commission) if trade_update.order.commission else None,
                 "source": trade_update.order.source
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
    def _run_price_producer(self):
        """Run the price update producer thread."""
        if not self._subscribed_symbols:
            self.logger.info("No symbols subscribed for price updates. Price producer not starting.")
            return
        try:
            self._price_stream = StockDataStream(
                api_key=self._api_key,
                secret_key=self._secret_key,
                feed=DataFeed.SIP
            )

            async def price_handler(data: Trade):
                self.handle_price_update({"price": str(data.price), "symbol": data.symbol, "timestamp": str(data.timestamp)})

            self.logger.info(f"Price producer subscribing to: {list(self._subscribed_symbols)}")
            self._price_stream.subscribe_trades(
                price_handler,
                *list(self._subscribed_symbols)
            )
            self._price_stream.run() # This blocks until stop() is called or an error occurs

        except Exception as e:
            self.logger.error(f"Error in price producer: {e}")
        finally:
            self.logger.info("Price producer thread finished.")


    def _run_order_producer(self):
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


    # --- Redis Subscription Handler (Step 3.5.2) ---
    def handle_registration_message(self, message):
        """Handle incoming registration messages from Redis."""
        try:
            # Assuming message['data'] is the JSON payload from the wrapper
            payload = message.get('data', '{}')
            sender = payload.get('sender', 'unknown')
            action = payload.get('action')
            ticker = payload.get('ticker')

            self.logger.info(f"Received registration request from {sender}: Action={action}, Ticker={ticker}")

            if not action or not ticker:
                self.logger.warning("Invalid registration message received (missing action or ticker).")
                return

            if action == "subscribe":
                self.subscribe_symbols([ticker]) # Pass ticker as a list
            elif action == "unsubscribe":
                self.unsubscribe_symbols([ticker]) # Pass ticker as a list
            else:
                self.logger.warning(f"Unknown action in registration message: {action}")

        except json.JSONDecodeError as e:
             self.logger.error(f"Failed to decode registration message data: {e} - Raw Data: {message.get('data')}")
        except Exception as e:
            self.logger.error(f"Error handling registration message: {e} - Message: {message}")

    # --- Symbol Subscription Management ---
    def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to price updates for given symbols."""
        new_symbols = set(s.upper() for s in symbols if isinstance(s, str)) - self._subscribed_symbols
        if not new_symbols:
            self.logger.debug(f"Symbols {symbols} already subscribed or invalid.")
            return

        self._subscribed_symbols.update(new_symbols)
        self.logger.info(f"Added subscriptions for: {new_symbols}. Current: {self._subscribed_symbols}")

        # Restart price producer thread if running to include new symbols
        if self._running:
            self._restart_price_producer()


    def unsubscribe_symbols(self, symbols: List[str]):
        """Unsubscribe from price updates for given symbols."""
        removed_symbols = self._subscribed_symbols.intersection(s.upper() for s in symbols if isinstance(s, str))
        if not removed_symbols:
            self.logger.debug(f"Symbols {symbols} not currently subscribed or invalid.")
            return

        self._subscribed_symbols.difference_update(removed_symbols)
        self.logger.info(f"Removed subscriptions for: {removed_symbols}. Current: {self._subscribed_symbols}")

        # Restart price producer thread if running to remove symbols
        if self._running:
            self._restart_price_producer()

    def _restart_price_producer(self):
        """Stops and starts the price producer thread safely."""
        self.logger.info("Attempting to restart price producer...")
        # Stop existing thread and stream if they exist
        if self._price_stream:
            try:
                self._price_stream.close()
                self.logger.info("Closed existing price stream.")
            except Exception as e:
                self.logger.error(f"Error closing price stream during restart: {e}")
            self._price_stream = None # Set to None after closing
        if self._price_producer and self._price_producer.is_alive():
            self._price_producer.join(timeout=0.5)
            if self._price_producer.is_alive():
                 self.logger.warning("Price producer thread did not exit cleanly during restart.")
            else:
                 self.logger.info("Existing price producer thread joined.")
        self._price_producer = None

        # Start new thread only if there are symbols and broker is running
        if self._running and self._subscribed_symbols:
            self._price_producer = threading.Thread(target=self._run_price_producer)
            self._price_producer.daemon = True
            self._price_producer.start()
            self.logger.info(f"Restarted price producer for symbols: {self._subscribed_symbols}")
        elif self._running:
             self.logger.info("No symbols subscribed, price producer not restarted.")


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
            self._price_producer = threading.Thread(target=self._run_price_producer)
            self._price_producer.daemon = True
            self._price_producer.start()
            self.logger.info("Price producer thread started (will wait for subscriptions).")


            # Start order producer
            self._order_producer = threading.Thread(target=self._run_order_producer)
            self._order_producer.daemon = True
            self._order_producer.start()
            self.logger.info("Order producer started")

            # Start Redis subscriber (Step 3.5.3 & 3.5.4)
            try:
                # Use the channel value directly
                if self._broker_registration_thread and self._broker_registration_thread.is_alive():
                    # If the thread is already alive, we assume the subscriber is running
                    # and skip starting it again
                    self.logger.info("Redis subscriber already running. Skipping")
                    return
                self._redis_subscriber.subscribe(self._registration_channel, self.handle_registration_message)
                self._broker_registration_thread = threading.Thread(target=self._redis_subscriber.start_listening)
                self._broker_registration_thread.daemon = True
                self._broker_registration_thread.start()
                self.logger.info(f"Redis subscriber started listening on {self._registration_channel}")
            except Exception as e:
                 self.logger.error(f"Failed to start Redis subscriber: {e}")
                 self.stop() # Stop everything if subscriber fails to start


    def stop(self):
        """Stop the broker's producer threads and Redis subscriber."""
        if self._running:
            self._running = False # Signal threads to stop
            self.logger.info("Stopping broker...")

            # Stop Redis subscriber first (Step 3.5.5)
            if self._redis_subscriber:
                try:
                    self._redis_subscriber.close() # Close connection first
                    self.logger.info("Redis subscriber connection closed.")
                except Exception as e:
                    self.logger.error(f"Error closing Redis subscriber connection: {e}")
            if self._broker_registration_thread and self._broker_registration_thread.is_alive():
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
            if self._price_producer and self._price_producer.is_alive():
                self._price_producer.join(timeout=1.0)
                if self._price_producer.is_alive():
                    self.logger.warning("Price producer thread did not exit cleanly.")
                else:
                    self.logger.info("Price producer thread stopped.")

            if self._order_producer and self._order_producer.is_alive():
                self._order_producer.join(timeout=1.0)
                if self._order_producer.is_alive():
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

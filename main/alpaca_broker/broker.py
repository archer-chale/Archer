"""
Alpaca broker component responsible for managing trade and order update streams.
"""
import threading
import os
from typing import List, Set
# Removed dotenv import

from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed
from alpaca.data.models import Trade
from alpaca.trading.stream import TradingStream
from alpaca.trading.models import TradeUpdate

from ..bots.SCALE_T.common.logging_config import get_logger
from ..bots.SCALE_T.common.constants import ENV_FILE, TRADING_TYPE_TO_KEY_NAME, TradingType
from .constants import MessageType, StreamType

class AlpacaBroker:
    """Main broker class for managing Alpaca market data and order streams."""
    
    def __init__(self):
        """Initialize the broker with thread tracking and logging."""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing AlpacaBroker")
        
        # Removed load_dotenv call
        
        self._running = False
        self._price_producer = None
        self._order_producer = None
        
        # Stream configuration
        self._price_stream = None
        self._order_stream = None
        self._subscribed_symbols: Set[str] = set()
        self._api_key = None
        self._secret_key = None
        self._trading_type = None
        
    def configure_api_keys(self, trading_type: TradingType = TradingType.PAPER):
        """Configure API keys based on trading type."""
        key_id_name = TRADING_TYPE_TO_KEY_NAME[trading_type]["KEY_ID_NAME"]
        secret_key_name = TRADING_TYPE_TO_KEY_NAME[trading_type]["SECRET_KEY_NAME"]
        
        self._api_key = os.environ.get(key_id_name)
        self._secret_key = os.environ.get(secret_key_name)
        self._trading_type = trading_type
        
        if not self._api_key or not self._secret_key:
            raise ValueError(f"Missing API keys for {trading_type.value} trading")
        
        self.logger.info(f"API keys configured for {trading_type.value} trading")
        
    def handle_price_update(self, price_data):
        """Handle incoming price updates."""
        self.logger.debug(f"Handling price update: {price_data}")
        
    def handle_order_update(self, trade_update: TradeUpdate):
        """Handle incoming order updates."""
        self.logger.debug(f"Handling order update: {trade_update}")
        
    def _run_price_producer(self):
        """Run the price update producer thread."""
        try:
            self._price_stream = StockDataStream(
                api_key=self._api_key,
                secret_key=self._secret_key,
                feed=DataFeed.SIP
            )
            
            async def price_handler(data: Trade):
                self.handle_price_update({"price": data.price, "symbol": data.symbol})
            
            if self._subscribed_symbols:
                self._price_stream.subscribe_trades(
                    price_handler,
                    *list(self._subscribed_symbols)
                )
                self._price_stream.run()
            
        except Exception as e:
            self.logger.error(f"Error in price producer: {e}")
            self._running = False

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
            
            self._order_stream.subscribe_trade_updates(order_handler)
            self._order_stream.run()
            
        except Exception as e:
            self.logger.error(f"Error in order producer: {e}")
            self._running = False
            
    def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to price updates for given symbols."""
        new_symbols = set(symbols) - self._subscribed_symbols
        if not new_symbols:
            return
            
        self._subscribed_symbols.update(new_symbols)
        self.logger.info(f"Added subscriptions for: {new_symbols}")
        
        # Restart stream if running to include new symbols
        if self._running and self._price_stream:
            self.logger.info("Restarting price stream with updated symbols")
            self._price_stream.close()
            self._price_stream = None
            self._run_price_producer()
            
    def unsubscribe_symbols(self, symbols: List[str]):
        """Unsubscribe from price updates for given symbols."""
        removed_symbols = self._subscribed_symbols.intersection(symbols)
        if not removed_symbols:
            return
            
        self._subscribed_symbols.difference_update(removed_symbols)
        self.logger.info(f"Removed subscriptions for: {removed_symbols}")
        
        # Restart stream if running to remove symbols
        if self._running and self._price_stream:
            self.logger.info("Restarting price stream with updated symbols")
            self._price_stream.close()
            self._price_stream = None
            self._run_price_producer()
    
    def start(self):
        """Start the broker's producer threads."""
        if not self._running:
            if not self._api_key or not self._secret_key:
                raise ValueError("API keys must be configured before starting")
                
            self._running = True
            self.logger.info("Starting producer threads")
            
            # Start price producer if we have symbols to watch
            if self._subscribed_symbols:
                self._price_producer = threading.Thread(target=self._run_price_producer)
                self._price_producer.daemon = True
                self._price_producer.start()
                self.logger.info(f"Price producer started for symbols: {self._subscribed_symbols}")
            
            # Start order producer
            self._order_producer = threading.Thread(target=self._run_order_producer)
            self._order_producer.daemon = True
            self._order_producer.start()
            self.logger.info("Order producer started")
            
    def stop(self):
        """Stop the broker's producer threads."""
        if self._running:
            self._running = False
            
            # Close streams
            if self._price_stream:
                temp_price_stream = self._price_stream
                self._price_stream = None
                temp_price_stream.close()
            
            if self._order_stream:
                temp_order_stream = self._order_stream
                self._order_stream = None
                temp_order_stream.close()
            
            # Join threads
            if self._price_producer and self._price_producer.is_alive():
                self._price_producer.join(timeout=1.0)
                
            if self._order_producer and self._order_producer.is_alive():
                self._order_producer.join(timeout=1.0)
                
            self.logger.info("Producer threads stopped")

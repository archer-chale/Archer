"""Tests for the Alpaca Broker component."""
import unittest
import os
from unittest.mock import patch, MagicMock, ANY

from main.alpaca_broker.broker import AlpacaBroker
from main.alpaca_broker.constants import MessageType, StreamType
from main.bots.SCALE_T.common.constants import TradingType
from alpaca.trading.models import TradeUpdate

class TestAlpacaBroker(unittest.TestCase):
    """Test cases for the AlpacaBroker class."""
    
    @patch('main.alpaca_broker.broker.get_logger')
    def setUp(self, mock_logger):
        """Set up test fixtures before each test method."""
        self.mock_logger = MagicMock()
        mock_logger.return_value = self.mock_logger
        self.broker = AlpacaBroker()
    
    def test_initialization(self):
        """Test broker initialization creates required attributes."""
        self.assertFalse(self.broker._running)
        self.assertIsNone(self.broker._price_producer)
        self.assertIsNone(self.broker._order_producer)
        self.assertEqual(self.broker._subscribed_symbols, set())
        self.assertIsNone(self.broker._trading_type)
    
    @patch.dict(os.environ, {
        'PAPER_ALPACA_API_KEY_ID': 'test_key',
        'PAPER_ALPACA_API_SECRET_KEY': 'test_secret'
    })
    def test_configure_api_keys_paper(self):
        """Test API key configuration for paper trading."""
        self.broker.configure_api_keys(TradingType.PAPER)
        self.assertEqual(self.broker._api_key, 'test_key')
        self.assertEqual(self.broker._secret_key, 'test_secret')
        self.assertEqual(self.broker._trading_type, TradingType.PAPER)
        self.mock_logger.info.assert_called_with('API keys configured for paper trading')
    
    def test_configure_api_keys_missing(self):
        """Test API key configuration with missing keys."""
        with self.assertRaises(ValueError):
            self.broker.configure_api_keys(TradingType.PAPER)
    
    def test_subscribe_symbols(self):
        """Test subscribing to symbols."""
        symbols = ['AAPL', 'MSFT']
        self.broker.subscribe_symbols(symbols)
        self.assertEqual(self.broker._subscribed_symbols, set(symbols))
        self.mock_logger.info.assert_called_with(ANY)
        call_args = self.mock_logger.info.call_args[0][0]
        self.assertTrue('AAPL' in call_args and 'MSFT' in call_args)
    
    def test_unsubscribe_symbols(self):
        """Test unsubscribing from symbols."""
        symbols = ['AAPL', 'MSFT']
        self.broker.subscribe_symbols(symbols)
        self.broker.unsubscribe_symbols(['AAPL'])
        self.assertEqual(self.broker._subscribed_symbols, {'MSFT'})
        self.mock_logger.info.assert_called_with("Removed subscriptions for: {'AAPL'}")
    
    def test_start_without_api_keys(self):
        """Test starting broker without configured API keys."""
        with self.assertRaises(ValueError):
            self.broker.start()
    
    @patch('main.alpaca_broker.broker.StockDataStream')
    @patch('main.alpaca_broker.broker.TradingStream')
    @patch.dict(os.environ, {
        'PAPER_ALPACA_API_KEY_ID': 'test_key',
        'PAPER_ALPACA_API_SECRET_KEY': 'test_secret'
    })
    def test_start_with_both_producers(self, mock_trading_stream, mock_stock_stream):
        """Test starting broker with both producers."""
        mock_price_instance = MagicMock()
        mock_order_instance = MagicMock()
        mock_stock_stream.return_value = mock_price_instance
        mock_trading_stream.return_value = mock_order_instance
        
        # Configure and start
        symbols = ['AAPL', 'MSFT']
        self.broker.configure_api_keys(TradingType.PAPER)
        self.broker.subscribe_symbols(symbols)
        self.broker.start()
        
        # Verify both producers started
        self.assertTrue(self.broker._running)
        self.assertIsNotNone(self.broker._price_producer)
        self.assertIsNotNone(self.broker._order_producer)
        
        # Verify stream setup
        mock_price_instance.subscribe_trades.assert_called_once()
        mock_order_instance.subscribe_trade_updates.assert_called_once()
        
        # Verify logging
        self.mock_logger.info.assert_any_call("Starting producer threads")
        self.mock_logger.info.assert_any_call("Order producer started")
    
    @patch('main.alpaca_broker.broker.TradingStream')
    def test_handle_order_update(self, mock_trading_stream):
        """Test order update handling."""
        mock_trade_update = MagicMock(spec=TradeUpdate)
        self.broker.handle_order_update(mock_trade_update)
        self.mock_logger.debug.assert_called_with(f"Handling order update: {mock_trade_update}")

    def test_stop_cleans_up_streams(self):
        """Test that stop() properly cleans up both streams."""
        # Setup mock streams
        mock_price_stream = MagicMock()
        mock_order_stream = MagicMock()
        self.broker._price_stream = mock_price_stream
        self.broker._order_stream = mock_order_stream
        self.broker._running = True
        
        # Stop the broker
        self.broker.stop()
        
        # Verify streams were closed
        mock_price_stream.close.assert_called_once()
        mock_order_stream.close.assert_called_once()
        
        # Verify cleanup
        self.assertFalse(self.broker._running)
        self.assertIsNone(self.broker._price_stream)
        self.assertIsNone(self.broker._order_stream)

if __name__ == '__main__':
    unittest.main()

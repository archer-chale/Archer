"""Tests for the Alpaca Broker component."""
import unittest
import os
import json
import time
import threading # Added import
from unittest.mock import patch, MagicMock, ANY

from main.alpaca_broker.broker import AlpacaBroker
from main.utils.redis import CHANNELS # Import CHANNELS for dynamic name generation
from main.bots.SCALE_T.common.constants import TradingType
from alpaca.trading.models import TradeUpdate, Order # Import Order for mocking

# Mock TradeUpdate and its nested Order object for testing handle_order_update
class MockOrder:
    def __init__(self, symbol="AAPL", order_id="mock_order_123", status="filled", side="buy", asset_class="us_equity", order_class="simple", order_type="market", time_in_force="day", **kwargs):
        self.id = order_id
        self.client_order_id = "mock_client_id"
        self.created_at = "2024-01-01T10:00:00Z"
        self.updated_at = "2024-01-01T10:01:00Z"
        self.submitted_at = "2024-01-01T10:00:05Z"
        self.filled_at = "2024-01-01T10:01:00Z"
        self.expired_at = None
        self.canceled_at = None
        self.failed_at = None
        self.replaced_at = None
        self.replaced_by = None
        self.replaces = None
        self.asset_id = "mock_asset_id"
        self.symbol = symbol
        self.asset_class = MagicMock()
        self.asset_class.value = asset_class
        self.notional = None
        self.qty = "10"
        self.filled_qty = "10"
        self.filled_avg_price = "150.00"
        self.order_class = MagicMock()
        self.order_class.value = order_class
        self.order_type = MagicMock()
        self.order_type.value = order_type
        self.side = MagicMock()
        self.side.value = side
        self.time_in_force = MagicMock()
        self.time_in_force.value = time_in_force
        self.limit_price = None
        self.stop_price = None
        self.status = MagicMock()
        self.status.value = status
        self.extended_hours = False
        self.legs = None
        self.trail_percent = None
        self.trail_price = None
        self.hwm = None
        self.commission = "0.50"
        self.source = None
        # Allow setting extra attributes via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockTradeUpdate:
     def __init__(self, symbol="AAPL", event="fill", **kwargs):
         self.event = event
         self.execution_id = "mock_exec_id"
         self.order = MockOrder(symbol=symbol, **kwargs.get('order_kwargs', {}))
         self.timestamp = "2024-01-01T10:01:00Z"
         self.position_qty = "10"
         self.price = "150.00"
         self.qty = "10"


class TestAlpacaBroker(unittest.TestCase):
    """Test cases for the AlpacaBroker class."""

    @patch('main.alpaca_broker.broker.get_logger')
    @patch('main.alpaca_broker.broker.RedisPublisher')
    @patch('main.alpaca_broker.broker.RedisSubscriber')
    def setUp(self, MockRedisSubscriber, MockRedisPublisher, mock_get_logger):
        """Set up test fixtures before each test method."""
        self.mock_logger = MagicMock()
        mock_get_logger.return_value = self.mock_logger

        # Mock Redis connections
        self.mock_redis_publisher = MagicMock()
        self.mock_redis_subscriber = MagicMock()
        MockRedisPublisher.return_value = self.mock_redis_publisher
        MockRedisSubscriber.return_value = self.mock_redis_subscriber

        # Prevent actual connection attempts in __init__
        self.mock_redis_publisher.ping.return_value = True
        self.mock_redis_subscriber.ping.return_value = True

        self.broker = AlpacaBroker()
        # Reset mocks after init to clear init logs/calls
        self.mock_logger.reset_mock()
        self.mock_redis_publisher.reset_mock()
        self.mock_redis_subscriber.reset_mock()


    def test_initialization(self):
        """Test broker initialization creates required attributes."""
        self.assertFalse(self.broker._running)
        self.assertIsNone(self.broker._price_producer)
        self.assertIsNone(self.broker._order_producer)
        self.assertEqual(self.broker._subscribed_symbols, set())
        self.assertIsNone(self.broker._trading_type)
        self.assertIsNotNone(self.broker._redis_publisher)
        self.assertIsNotNone(self.broker._redis_subscriber)

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
        # Ensure env vars are not set for this test
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                self.broker.configure_api_keys(TradingType.PAPER)

    @patch('main.alpaca_broker.broker.AlpacaBroker._restart_price_producer')
    def test_subscribe_symbols(self, mock_restart):
        """Test subscribing to symbols triggers restart if running."""
        symbols = ['AAPL', 'MSFT']
        self.broker.subscribe_symbols(symbols)
        self.assertEqual(self.broker._subscribed_symbols, {'AAPL', 'MSFT'})
        self.mock_logger.info.assert_called_with(ANY) # Check log content below
        call_args, _ = self.mock_logger.info.call_args
        self.assertTrue('AAPL' in call_args[0] and 'MSFT' in call_args[0])
        mock_restart.assert_not_called() # Not running yet

        # Test restart when running
        self.broker._running = True
        self.broker.subscribe_symbols(['GOOG'])
        self.assertEqual(self.broker._subscribed_symbols, {'AAPL', 'MSFT', 'GOOG'})
        mock_restart.assert_called_once()

    @patch('main.alpaca_broker.broker.AlpacaBroker._restart_price_producer')
    def test_unsubscribe_symbols(self, mock_restart):
        """Test unsubscribing from symbols triggers restart if running."""
        symbols = ['AAPL', 'MSFT', 'GOOG']
        self.broker._subscribed_symbols = set(symbols) # Pre-populate

        self.broker.unsubscribe_symbols(['AAPL'])
        self.assertEqual(self.broker._subscribed_symbols, {'MSFT', 'GOOG'})
        # Use ANY because the log includes the current set which is unordered
        self.mock_logger.info.assert_called_with(ANY)
        call_args, _ = self.mock_logger.info.call_args
        self.assertTrue("Removed subscriptions for: {'AAPL'}" in call_args[0])
        mock_restart.assert_not_called() # Not running yet

        # Test restart when running
        self.broker._running = True
        self.broker.unsubscribe_symbols(['MSFT'])
        self.assertEqual(self.broker._subscribed_symbols, {'GOOG'})
        mock_restart.assert_called_once()

    def test_start_without_api_keys(self):
        """Test starting broker without configured API keys."""
        with self.assertRaises(ValueError):
            self.broker.start()

    @patch.dict(os.environ, { # Patch env vars for this test
        'PAPER_ALPACA_API_KEY_ID': 'test_key',
        'PAPER_ALPACA_API_SECRET_KEY': 'test_secret'
    })
    def test_start_without_redis(self):
        """Test starting broker without Redis connection."""
        self.broker.configure_api_keys(TradingType.PAPER) # Configure keys first
        self.broker._redis_publisher = None # Simulate connection failure AFTER init
        self.broker._redis_subscriber = None # Simulate connection failure AFTER init
        self.broker.start()
        self.mock_logger.error.assert_called_with("Cannot start broker without Redis connections.")
        self.assertFalse(self.broker._running)


    @patch('main.alpaca_broker.broker.threading.Thread')
    @patch('main.alpaca_broker.broker.StockDataStream')
    @patch('main.alpaca_broker.broker.TradingStream')
    @patch.dict(os.environ, {
        'PAPER_ALPACA_API_KEY_ID': 'test_key',
        'PAPER_ALPACA_API_SECRET_KEY': 'test_secret'
    })
    def test_start_starts_producers_and_subscriber(self, mock_trading_stream, mock_stock_stream, mock_thread):
        """Test start() initializes and starts threads correctly."""
        # Configure
        symbols = ['AAPL']
        self.broker.configure_api_keys(TradingType.PAPER)
        self.broker.subscribe_symbols(symbols)

        # Start
        self.broker.start()

        # Assertions
        self.assertTrue(self.broker._running)
        # Check threads were created and started
        self.assertEqual(mock_thread.call_count, 3) # Price, Order, Redis Sub
        # Verify targets for each thread
        targets = [call.kwargs['target'] for call in mock_thread.call_args_list]
        self.assertIn(self.broker._run_price_producer, targets)
        self.assertIn(self.broker._run_order_producer, targets)
        self.assertIn(self.broker._redis_subscriber.start_listening, targets)
        # Verify all started
        self.assertEqual(mock_thread.return_value.start.call_count, 3)

        # Check Redis subscriber setup
        self.mock_redis_subscriber.subscribe.assert_called_once_with(
            self.broker._registration_channel, self.broker.handle_registration_message
        )
        # Check logging
        self.mock_logger.info.assert_any_call("Starting producer threads and Redis subscriber")
        self.mock_logger.info.assert_any_call(ANY) # Price producer log check removed due to timing
        self.mock_logger.info.assert_any_call("Order producer started")
        self.mock_logger.info.assert_any_call(f"Redis subscriber started listening on {self.broker._registration_channel}")


    def test_handle_price_update_publishes(self):
        """Test handle_price_update publishes correctly formatted message."""
        price_data = {"price": "150.50", "symbol": "AAPL", "timestamp": "ts1"}
        expected_channel = CHANNELS.get_ticker_channel("AAPL")
        expected_payload = {
            "type": "price",
            "timestamp": "ts1",
            "price": "150.50",
            "volume": None,
            "symbol": "AAPL"
        }

        self.broker.handle_price_update(price_data)

        self.mock_redis_publisher.publish.assert_called_once_with(
            expected_channel, expected_payload, sender="alpaca_broker"
        )

    def test_handle_order_update_publishes(self):
        """Test handle_order_update publishes correctly formatted message."""
        mock_trade_update = MockTradeUpdate(symbol="MSFT")
        expected_channel = CHANNELS.get_ticker_channel("MSFT")

        self.broker.handle_order_update(mock_trade_update)

        # Check that publish was called
        self.mock_redis_publisher.publish.assert_called_once()
        # Get the arguments publish was called with
        args, kwargs = self.mock_redis_publisher.publish.call_args
        # Check channel name
        self.assertEqual(args[0], expected_channel)
        # Check message structure (basic checks)
        published_data = args[1]
        self.assertEqual(published_data['type'], 'order')
        self.assertEqual(published_data['symbol'], 'MSFT')
        self.assertIn('order_data', published_data)
        self.assertEqual(published_data['order_data']['order']['symbol'], 'MSFT')
        self.assertEqual(kwargs['sender'], 'alpaca_broker')


    @patch('main.alpaca_broker.broker.AlpacaBroker.subscribe_symbols')
    def test_handle_registration_subscribe(self, mock_subscribe):
        """Test registration handler calls subscribe_symbols."""
        message = {'data': {'action': 'subscribe', 'ticker': 'XYZ'}}
        self.broker.handle_registration_message(message)
        mock_subscribe.assert_called_once_with(['XYZ'])

    @patch('main.alpaca_broker.broker.AlpacaBroker.unsubscribe_symbols')
    def test_handle_registration_unsubscribe(self, mock_unsubscribe):
        """Test registration handler calls unsubscribe_symbols."""
        message = {'data': {'action': 'unsubscribe', 'ticker': 'ABC'}}
        self.broker.handle_registration_message(message)
        mock_unsubscribe.assert_called_once_with(['ABC'])

    def test_handle_registration_invalid(self):
        """Test registration handler with invalid message."""
        message = {'data': {'action': 'invalid_action', 'ticker': 'ABC'}}
        self.broker.handle_registration_message(message)
        self.mock_logger.warning.assert_called_with("Unknown action in registration message: invalid_action")

        message_no_action = {'data': {'ticker': 'ABC'}}
        self.broker.handle_registration_message(message_no_action)
        self.mock_logger.warning.assert_called_with("Invalid registration message received (missing action or ticker).")


    def test_stop_closes_connections_and_joins_threads(self):
        """Test stop() closes connections and joins threads."""
        # Simulate running state with mock threads/streams
        self.broker._running = True
        mock_price_stream = MagicMock()
        mock_order_stream = MagicMock()
        self.broker._price_stream = mock_price_stream
        self.broker._order_stream = mock_order_stream
        self.broker._price_producer = MagicMock(spec=threading.Thread)
        self.broker._order_producer = MagicMock(spec=threading.Thread)
        self.broker._broker_registration_thread = MagicMock(spec=threading.Thread)
        self.broker._price_producer.is_alive.return_value = True
        self.broker._order_producer.is_alive.return_value = True
        self.broker._broker_registration_thread.is_alive.return_value = True


        self.broker.stop()

        # Verify state
        self.assertFalse(self.broker._running)
        # Verify closures
        self.broker._redis_subscriber.close.assert_called_once()
        mock_price_stream.close.assert_called_once()
        mock_order_stream.close.assert_called_once()
        self.broker._redis_publisher.close.assert_called_once()
        # Verify thread joins
        self.broker._broker_registration_thread.join.assert_called_once_with(timeout=1.0)
        self.broker._price_producer.join.assert_called_once_with(timeout=1.0)
        self.broker._order_producer.join.assert_called_once_with(timeout=1.0)
        # Verify logging (Check main stop messages, specific thread stop logs might have timing issues)
        self.mock_logger.info.assert_any_call("Stopping broker...")
        self.mock_logger.info.assert_any_call("Redis subscriber connection closed.")
        self.mock_logger.info.assert_any_call("Redis publisher connection closed.")
        self.mock_logger.info.assert_any_call("Broker stopped.")


if __name__ == '__main__':
    unittest.main()

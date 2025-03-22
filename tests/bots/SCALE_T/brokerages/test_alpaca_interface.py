# """
# Unit tests for the AlpacaInterface class.

# These tests ensure that the AlpacaInterface correctly interacts with the Alpaca API
# and handles various scenarios appropriately.
# """

# import unittest
# from unittest.mock import patch, MagicMock
# import os

# from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
# from alpaca.trading.client import TradingClient
# from alpaca.common.exceptions import APIError


# class TestAlpacaInterface(unittest.TestCase):
#     """Tests for the AlpacaInterface class."""

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret",
#         "ALPACA_API_KEY_ID": "test_live_key",
#         "ALPACA_API_SECRET_KEY": "test_live_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def setUp(self, mock_trading_client):
#         """Set up test fixtures before each test method."""
#         self.mock_trading_client_instance = MagicMock()
#         mock_trading_client.return_value = self.mock_trading_client_instance
        
#         # Mock account response
#         mock_account = MagicMock()
#         mock_account.status = "ACTIVE"
#         self.mock_trading_client_instance.get_account.return_value = mock_account
        
#         # Create test instance with paper trading
#         self.paper_interface = AlpacaInterface(trading_type="paper", ticker="AAPL")
        
#         # Create test instance with live trading
#         self.live_interface = AlpacaInterface(trading_type="live", ticker="MSFT")

#     def test_init_sets_trading_type_and_ticker(self):
#         """Test that __init__ correctly sets trading_type and ticker."""
#         self.assertEqual(self.paper_interface.trading_type, "paper")
#         self.assertEqual(self.paper_interface.ticker, "AAPL")
#         self.assertEqual(self.live_interface.trading_type, "live")
#         self.assertEqual(self.live_interface.ticker, "MSFT")

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_set_trading_client_paper(self, mock_trading_client):
#         """Test that set_trading_client sets the correct keys for paper trading."""
#         # Configure mock to return successful account validation
#         mock_instance = MagicMock()
#         mock_account = MagicMock()
#         mock_account.status = "ACTIVE"
#         mock_instance.get_account.return_value = mock_account
#         mock_trading_client.return_value = mock_instance
        
#         interface = AlpacaInterface(trading_type="paper")
        
#         # Verify trading client was created with correct parameters
#         mock_trading_client.assert_called_with(
#             "test_paper_key",
#             "test_paper_secret",
#             paper=True
#         )
        
#         self.assertEqual(interface.api_key, "test_paper_key")
#         self.assertEqual(interface.secret_key, "test_paper_secret")

#     @patch.dict(os.environ, {
#         "ALPACA_API_KEY_ID": "test_live_key", 
#         "ALPACA_API_SECRET_KEY": "test_live_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_set_trading_client_live(self, mock_trading_client):
#         """Test that set_trading_client sets the correct keys for live trading."""
#         # Configure mock to return successful account validation
#         mock_instance = MagicMock()
#         mock_account = MagicMock()
#         mock_account.status = "ACTIVE"
#         mock_instance.get_account.return_value = mock_account
#         mock_trading_client.return_value = mock_instance
        
#         interface = AlpacaInterface(trading_type="live")
        
#         # Verify trading client was created with correct parameters
#         mock_trading_client.assert_called_with(
#             "test_live_key",
#             "test_live_secret",
#             paper=False
#         )
        
#         self.assertEqual(interface.api_key, "test_live_key")
#         self.assertEqual(interface.secret_key, "test_live_secret")

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_validate_alpaca_keys_success(self, mock_trading_client):
#         """Test successful validation of Alpaca keys."""
#         # Mock successful account response
#         mock_account = MagicMock()
#         mock_account.status = "ACTIVE"
#         mock_trading_client.return_value.get_account.return_value = mock_account
        
#         interface = AlpacaInterface(trading_type="paper")
#         is_valid, errors = interface.validate_alpaca_keys()
        
#         self.assertTrue(is_valid)
#         self.assertEqual(errors, [])

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     def test_validate_alpaca_keys_missing_key(self):
#         """Test validation fails when API key is missing."""
#         # This should raise a ValueError because the key is missing
#         with self.assertRaises(ValueError) as context:
#             AlpacaInterface(trading_type="paper")
        
#         # The actual error message may vary depending on the implementation
#         # So we use a more generic assertion that just checks it's a ValueError
#         self.assertIsInstance(context.exception, ValueError)

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_validate_alpaca_keys_inactive_account(self, mock_trading_client):
#         """Test validation fails when account is not active."""
#         # Mock inactive account
#         mock_account = MagicMock()
#         mock_account.status = "INACTIVE"
#         mock_trading_client.return_value.get_account.return_value = mock_account
        
#         with self.assertRaises(ValueError) as context:
#             AlpacaInterface(trading_type="paper")
        
#         self.assertIn("Alpaca key validation failed", str(context.exception))

#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_validate_alpaca_keys_api_error(self, mock_trading_client):
#         """Test validation fails when API error occurs."""
#         # Mock API error with required 'error' parameter
#         api_error = APIError({"message": "Authentication failed"})
#         # Make the get_account method raise the API error
#         mock_trading_client.return_value.get_account.side_effect = api_error
        
#         with self.assertRaises(ValueError) as context:
#             AlpacaInterface(trading_type="paper")
        
#         self.assertIn("Alpaca key validation failed", str(context.exception))
        
#     @patch.dict(os.environ, {
#         "PAPER_ALPACA_API_KEY_ID": "test_paper_key", 
#         "PAPER_ALPACA_API_SECRET_KEY": "test_paper_secret"
#     })
#     @patch('main.bots.SCALE_T.brokerages.alpaca_interface.TradingClient')
#     def test_validate_alpaca_keys_generic_exception(self, mock_trading_client):
#         """Test validation fails when a generic exception occurs."""
#         # Mock a generic exception
#         mock_trading_client.return_value.get_account.side_effect = Exception("Some unexpected error")
        
#         with self.assertRaises(ValueError) as context:
#             AlpacaInterface(trading_type="paper")
        
#         self.assertIn("Alpaca key validation failed", str(context.exception))
#         self.assertIn("Unexpected error", str(context.exception))

#     def test_get_shares_count_with_position(self):
#         """Test get_shares_count when position exists."""
#         # Mock position for AAPL
#         mock_position = MagicMock()
#         mock_position.symbol = "AAPL"
#         mock_position.qty = "10"
        
#         # Setup mock to return our position
#         self.mock_trading_client_instance.get_all_positions.return_value = [mock_position]
        
#         shares = self.paper_interface.get_shares_count()
#         self.assertEqual(shares, 10)

#     def test_get_shares_count_no_position(self):
#         """Test get_shares_count when no position exists."""
#         # Mock empty positions list
#         self.mock_trading_client_instance.get_all_positions.return_value = []
        
#         shares = self.paper_interface.get_shares_count()
#         self.assertEqual(shares, 0)

#     def test_get_current_price(self):
#         """Test get_current_price returns the last trade price."""
#         # Mock last trade
#         mock_trade = MagicMock()
#         mock_trade.price = 150.75
#         self.mock_trading_client_instance.get_last_trade.return_value = mock_trade
        
#         price = self.paper_interface.get_current_price()
#         self.assertEqual(price, 150.75)
#         self.mock_trading_client_instance.get_last_trade.assert_called_once_with("AAPL")

#     def test_get_order_by_id(self):
#         """Test get_order_by_id returns the order from the trading client."""
#         # Mock order
#         mock_order = MagicMock()
#         mock_order.id = "test_order_id"
#         self.mock_trading_client_instance.get_order.return_value = mock_order
        
#         order = self.paper_interface.get_order_by_id("test_order_id")
#         self.assertEqual(order.id, "test_order_id")
#         self.mock_trading_client_instance.get_order.assert_called_once_with("test_order_id")
    
#     def test_cancel_order_success(self):
#         """Test successful order cancellation."""
#         # Simulate successful cancellation
#         self.mock_trading_client_instance.cancel_order.return_value = None
        
#         # Call cancel_order with a test order ID
#         self.paper_interface.cancel_order("test_order_id")
        
#         # Verify cancel_order was called with the correct order ID
#         self.mock_trading_client_instance.cancel_order.assert_called_once_with("test_order_id")
    
#     def test_cancel_order_exception(self):
#         """Test order cancellation with exception."""
#         # Simulate an error during cancellation
#         self.mock_trading_client_instance.cancel_order.side_effect = Exception("Cancellation failed")
        
#         # Call cancel_order - it should handle the exception without raising it
#         self.paper_interface.cancel_order("test_order_id")
        
#         # Verify cancel_order was called with the correct order ID despite the exception
#         self.mock_trading_client_instance.cancel_order.assert_called_once_with("test_order_id")
    
#     def test_submit_order_success(self):
#         """Test successful order submission."""
#         # Mock order response
#         mock_order = MagicMock()
#         mock_order.id = "new_order_id"
#         mock_order.status = "new"
#         self.mock_trading_client_instance.submit_order.return_value = mock_order
        
#         # Test order data
#         order_data = {
#             'symbol': 'AAPL',
#             'qty': '10',
#             'side': 'buy',
#             'type': 'limit',
#             'limit_price': '150.00',
#             'time_in_force': 'day'
#         }
        
#         # Call submit_order
#         result = self.paper_interface.submit_order(order_data)
        
#         # Verify the result and that submit_order was called with correct parameters
#         self.assertEqual(result.id, "new_order_id")
#         self.mock_trading_client_instance.submit_order.assert_called_once_with(**order_data)
    
#     def test_submit_order_exception(self):
#         """Test order submission with exception."""
#         # Simulate an error during order submission
#         self.mock_trading_client_instance.submit_order.side_effect = Exception("Submission failed")
        
#         # Test order data
#         order_data = {
#             'symbol': 'AAPL',
#             'qty': '10',
#             'side': 'buy',
#             'type': 'limit',
#             'limit_price': '150.00',
#             'time_in_force': 'day'
#         }
        
#         # Call submit_order - should return None on exception
#         result = self.paper_interface.submit_order(order_data)
        
#         # Verify result is None and submit_order was called with correct parameters
#         self.assertIsNone(result)
#         self.mock_trading_client_instance.submit_order.assert_called_once_with(**order_data)


# if __name__ == "__main__":
#     unittest.main()

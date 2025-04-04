import unittest
from unittest.mock import patch, Mock, MagicMock
import threading

# Import the run_engine function from engine.py
from main.bots.SCALE_T.engine import run_engine


class TestEngine(unittest.TestCase):
    """Test cases for the SCALE_T engine module."""

    @patch('main.bots.SCALE_T.engine.CSVService')
    @patch('main.bots.SCALE_T.engine.AlpacaInterface')
    @patch('main.bots.SCALE_T.engine.DecisionMaker')
    def test_run_engine_initialization(self, mock_decision_maker, mock_alpaca_interface, mock_csv_service):
        """Test that the run_engine function correctly initializes the components."""
        # Configure mocks
        mock_csv_service_instance = Mock()
        mock_csv_service.return_value = mock_csv_service_instance
        
        mock_alpaca_interface_instance = Mock()
        mock_alpaca_interface.return_value = mock_alpaca_interface_instance
        
        mock_decision_maker_instance = Mock()
        mock_decision_maker.return_value = mock_decision_maker_instance
        
        # Override consume_actions to avoid infinite loop
        def side_effect():
            raise Exception("Test completed")
            
        mock_decision_maker_instance.consume_actions.side_effect = side_effect
        
        # Call the run_engine function with test parameters
        with self.assertRaises(Exception) as context:
            run_engine(ticker="AAPL", trading_type="paper")
            
        self.assertIn("Test completed", str(context.exception))
            
        # Verify component initialization
        mock_csv_service.assert_called_once_with(ticker="AAPL", trading_type="paper")
        mock_alpaca_interface.assert_called_once_with(trading_type="paper", ticker="AAPL")
        mock_decision_maker.assert_called_once_with(
            csv_service=mock_csv_service_instance, 
            alpaca_interface=mock_alpaca_interface_instance
        )
        
        # Verify methods called on decision maker
        mock_decision_maker_instance.launch_action_producer_threads.assert_called_once()
        mock_decision_maker_instance.consume_actions.assert_called_once()

    @patch('main.bots.SCALE_T.engine.CSVService')
    @patch('main.bots.SCALE_T.engine.AlpacaInterface')
    @patch('main.bots.SCALE_T.engine.DecisionMaker')
    def test_run_engine_live_trading(self, mock_decision_maker, mock_alpaca_interface, mock_csv_service):
        """Test that the run_engine function correctly handles live trading."""
        # Configure mocks
        mock_csv_service_instance = Mock()
        mock_csv_service.return_value = mock_csv_service_instance
        
        mock_alpaca_interface_instance = Mock()
        mock_alpaca_interface.return_value = mock_alpaca_interface_instance
        
        mock_decision_maker_instance = Mock()
        mock_decision_maker.return_value = mock_decision_maker_instance
        
        # Override consume_actions to avoid infinite loop
        def side_effect():
            raise Exception("Test completed")
            
        mock_decision_maker_instance.consume_actions.side_effect = side_effect
        
        # Call the run_engine function with live trading
        with self.assertRaises(Exception) as context:
            run_engine(ticker="MSFT", trading_type="live")
            
        self.assertIn("Test completed", str(context.exception))
            
        # Verify component initialization with live trading parameters
        mock_csv_service.assert_called_once_with(ticker="MSFT", trading_type="live")
        mock_alpaca_interface.assert_called_once_with(trading_type="live", ticker="MSFT")


if __name__ == "__main__":
    unittest.main()

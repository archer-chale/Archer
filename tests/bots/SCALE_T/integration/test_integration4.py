import unittest
from unittest.mock import Mock, patch
import os
import threading
import time
import pytest

from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.trading.decision_maker import DecisionMaker
from main.bots.SCALE_T.common.logging_config import get_logger
from main.bots.SCALE_T.common.constants import TradingType
from main.bots.SCALE_T.trading.constants import MessageType

from alpaca.trading.enums import OrderStatus, OrderSide


class TestScaleTFractionalOrders(unittest.TestCase):
    """Integration tests for the SCALE_T bot with fractional order placements."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for each test."""
        # Create a temporary directory
        cls.csv_file_path = os.path.join("data", "SCALE_T", "ticker_data", TradingType.PAPER.value, "TEST.csv")
        os.makedirs(os.path.dirname(cls.csv_file_path), exist_ok=True)

        cls.logger = get_logger("FractionalOrderTest")
        cls.logger.setLevel("DEBUG")
        cls.logger.info("Setting up test fixtures for fractional order tests.")
        
        # Generate CSV data with fractional target shares
        header = "index,buy_price,sell_price,target_shares,held_shares,pending_order_id,spc,unrealized_profit,last_action,profit"
        data = [header]
        sell_price = 100.0
        for i in range(10):
            buy_price = round(sell_price * 0.995, 2)
            # Setting fractional target shares (e.g., 1.5 shares)
            row = f"{i},{buy_price},{sell_price},1.5,0,None,N,0.0,,0.0"
            data.append(row)
            sell_price = buy_price

        # Write CSV data to file
        with open(cls.csv_file_path, 'w', newline='') as csvfile:
            for row in data:
                csvfile.write(row + '\n')

        # Mock AlpacaInterface
        cls.alpaca_interface = Mock(spec=AlpacaInterface)
        cls.alpaca_interface.ticker = "TEST"
        cls.alpaca_interface.trading_type = TradingType.PAPER

        # Mock AlpacaInterface initialization methods
        cls.mock_initial_price = 101.0
        cls.alpaca_interface.get_current_price.return_value = cls.mock_initial_price
        cls.mock_shares_count = 0
        cls.alpaca_interface.get_shares_count.return_value = cls.mock_shares_count

        # Instantiate CSVService and DecisionMaker
        cls.csv_service = CSVService("TEST", TradingType.PAPER)
        cls.decision_maker = DecisionMaker(
            csv_service=cls.csv_service, alpaca_interface=cls.alpaca_interface
        )

        # Create and start the consumer thread
        cls.decision_maker.publisher = Mock()
        cls.consumer_thread = threading.Thread(target=cls._consume_actions_thread)
        cls.consumer_thread.daemon = True  # Allow the thread to exit when the main thread exits
        cls.consumer_thread.start()
        cls.logger.info("Test fixtures set up.")

    @classmethod
    def _consume_actions_thread(cls):
        """Continuously consume actions from the queue."""
        while True:
            cls.decision_maker.consume_actions()
            time.sleep(0.1)  # Short delay to prevent busy-waiting

    @classmethod
    def tearDownClass(cls):
        """Clean up after each test."""
        cls.logger.info("Cleaning up test fixtures.")
        if os.path.exists(cls.csv_file_path):
            os.remove(cls.csv_file_path)
        cls.logger.info("Test fixtures cleaned up.")

    @pytest.mark.order(401)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_fractional_buy_order_filled(self, mock_input, mock_send_notification):
        """Test a fractional buy order that is placed and filled."""
        self.logger.info("Starting fractional buy order test")
        
        # Mock the order for the placed order
        mock_placed_order = Mock()
        mock_placed_order.id = "test_fractional_buy_id"
        mock_placed_order.limit_price = 99.50  # This will be ignored for market orders with fractional shares
        mock_placed_order.side = 'buy'
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.filled_qty = '0'
        mock_placed_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price that matches the first row (99.50)
        price_update_buy = {'type': 'price_update', 'data': 99.50}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[1], 99.50)
        self.assertEqual(args[2], 1)  # Gotta do whole shares before fractional so 1 instead of 1.5

        # Update the mock order to be filled
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.filled_qty = '1'  # Fractional fill
        mock_placed_order.filled_avg_price = '99.50'

        # Update mock share count to match the filled order
        self.alpaca_interface.get_shares_count.return_value = 1  # Fractional shares

        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_placed_order
        mock_order_update.event = 'fill'

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)

        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(float(row['held_shares']), 1)  # Should have 1.5 shares now
        self.assertEqual(row['pending_order_id'], 'None')  # Order should be cleared
        
        # Verify there's no unrealized profit yet since price hasn't changed
        self.assertEqual(float(row['unrealized_profit']), 0.0)
        
        self.logger.info("Fractional buy order test completed successfully")

    @pytest.mark.order(402)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_fractional_sell_order_filled(self, mock_input, mock_send_notification):
        """Test a fractional sell order that is placed and filled."""
        self.logger.info("Starting fractional sell order test")
        
        # We should have 1.5 shares from the previous test
        # Update current price to trigger a sell
        self.alpaca_interface.get_current_price.return_value = 100.0
        
        # Mock the sell order
        mock_placed_order = Mock()
        mock_placed_order.id = "test_fractional_sell_id"
        mock_placed_order.limit_price = 100.0
        mock_placed_order.side = 'sell'
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.filled_qty = '0'
        mock_placed_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a sell order with a high price that matches the sell_price
        price_update_sell = {'type': 'price_update', 'data': 100.0}
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.SELL)
        self.assertEqual(args[1], 100.0)
        self.assertEqual(args[2], 1)  # Fractional quantity

        # Update the mock order to be filled
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.filled_qty = '1'  # Fractional fill
        mock_placed_order.filled_avg_price = '100.0'

        # Update mock share count to match the filled order (should be 0 now)
        self.alpaca_interface.get_shares_count.return_value = 0

        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_placed_order
        mock_order_update.event = 'fill'

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)

        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(float(row['held_shares']), 0.0)  # Should have 0 shares now
        self.assertEqual(row['pending_order_id'], 'None')  # Order should be cleared
        
        # Calculate expected profit: (sell_price - buy_price) * quantity
        expected_profit = (100.0 - 99.5) * 1
        self.assertEqual(float(row['profit']), expected_profit)
        
        self.logger.info("Fractional sell order test completed successfully")


# TO RUN: pytest -s tests/bots/SCALE_T/integration/test_integration4.py

import unittest
from unittest.mock import Mock, patch
import tempfile
import os
import csv
import threading
import time
import pytest

from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.trading.decision_maker import DecisionMaker
from alpaca.trading.enums import OrderStatus, OrderSide
from main.bots.SCALE_T.common.logging_config import get_logger
from main.bots.SCALE_T.common.constants import TradingType
from main.bots.SCALE_T.trading.constants import MessageType

"""
    Testing: 
        1. whole shares
        2. 
"""
class TestScaleTIntegrationMocked(unittest.TestCase):
    """Integration tests for the SCALE_T bot with mocked components."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for each test."""
        # Create a temporary directory
        cls.csv_file_path = os.path.join("data", "SCALE_T", "ticker_data", TradingType.PAPER.value, "TEST.csv")
        os.makedirs(os.path.dirname(cls.csv_file_path), exist_ok=True)

        cls.logger = get_logger("IntegrationTest")
        cls.logger.setLevel("DEBUG")
        cls.logger.info("Setting up test fixtures for each test.")
        cls.list_of_tests_done = []
        # Generate CSV data
        header = "index,buy_price,sell_price,target_shares,held_shares,pending_order_id,spc,unrealized_profit,last_action,profit"
        data = [header]
        sell_price = 100.0
        for i in range(50):
            buy_price = round(sell_price * 0.995, 2)
            row = f"{i},{buy_price},{sell_price},1,0,None,N,0.0,,0.0"
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

    @pytest.mark.order(1)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_buy_order_no_fill_cancel(self, mock_input, mock_send_notification):
        """Test a buy order that is placed but not filled, then canceled (price increase)."""

        # Mock the order ID for the placed order, and its status
        self.logger.info("Starting test 1")
        self.list_of_tests_done.append(1)
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.limit_price = 99.26  # Set the limit price for the mock order
        mock_placed_order.side = 'buy'  # Set the side for the mock order
        mock_placed_order.status = OrderStatus.NEW
        # Modified to use place_order instead of place_order
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a low price
        price_update_buy = {'type': 'price_update', 'data': 99.25}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(TestScaleTIntegrationMocked.alpaca_interface.place_order.called)
        args, kwargs = TestScaleTIntegrationMocked.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)  # side
        self.assertEqual(args[1], 99.26)  # price
        self.assertEqual(args[2], 1.0)  # quantity

        # Simulate a price increase to trigger cancellation
        price_update_cancel = {'type': 'price_update', 'data': 101.00}
        self.decision_maker.action_queue.put(price_update_cancel)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that cancel_order was called
        self.assertTrue(TestScaleTIntegrationMocked.alpaca_interface.cancel_order.called)
        self.alpaca_interface.cancel_order.assert_called_with(mock_placed_order.id)

        # Simulate order update coming on queue
        mock_order_update = Mock()
        mock_order_update.event = MessageType.ORDER_UPDATE
        mock_order_update.order = mock_placed_order
        mock_placed_order.status = OrderStatus.CANCELED
        mock_placed_order.filled_qty = 0
        mock_placed_order.filled_avg_price = None
        # print(mock_placed_order.id)
        # mock_placed_order.id = mock_placed_order.id
        order_update = {'type': MessageType.ORDER_UPDATE, 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Check that the CSV data was not updated (shares remain 0)
        self.assertEqual(TestScaleTIntegrationMocked.csv_service.get_current_held_shares(), 0)
        self.assertIsNone(TestScaleTIntegrationMocked.csv_service.get_pending_order_info())
        self.logger.info("Test 1 completed.")

    @pytest.mark.order(2)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_buy_order_filled_no_unrealized_profit(self, mock_input, mock_send_notification):
        """Test a buy order that is placed and filled, with no unrealized profit."""
        self.logger.info("Starting test 2")
        self.list_of_tests_done.append(2)
        row = TestScaleTIntegrationMocked.csv_service.get_row_by_index(0)
        self.assertEqual(row['unrealized_profit'], '0.0')

        # Mock the order ID for the placed order, and its status
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_2"
        mock_placed_order.limit_price = 99.50  # Set limit price to match buy_price in CSV
        mock_placed_order.side = 'buy'  # Set the side for the mock order
        mock_placed_order.status = OrderStatus.NEW  # Start with NEW status
        mock_placed_order.filled_qty = '0'  # Start with no fills
        mock_placed_order.filled_avg_price = None  # No fill price yet
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price that only matches the first row (99.50)
        # The second row's buy price would be 99.00 (99.50 * 0.995)
        price_update_buy = {'type': 'price_update', 'data': 99.50}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(TestScaleTIntegrationMocked.alpaca_interface.place_order.called)
        args, kwargs = TestScaleTIntegrationMocked.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[1], 99.50)
        self.assertEqual(args[2], 1.0)

        # Update the mock order to be filled
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.filled_qty = '1'
        mock_placed_order.filled_avg_price = '99.50'  # Fill at exact buy_price

        # Update mock share count to match the filled order
        self.alpaca_interface.get_shares_count.return_value = 1

        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_placed_order
        mock_order_update.event = 'fill'

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)

        # Check that the CSV data was updated correctly
        row = TestScaleTIntegrationMocked.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 1)
        self.assertEqual(float(row['profit']), 0.0)
        self.assertEqual(float(row['unrealized_profit']), 0.0)
        self.logger.debug(self.csv_service.get_row_by_index(0))
        self.logger.debug(self.csv_service.get_row_by_index(1))
        self.logger.info("Test 2 completed.")

    @pytest.mark.order(3)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_sell_order_no_unrealized_profit_cancel(self, mock_input, mock_send_notification):
        """Test a sell order that is placed and then cancelled, with no unrealized profit."""
        self.logger.info("Starting test 3")
        self.logger.info(f"List of tests done: {self.list_of_tests_done}")
        # First, need to setup a buy order that gets filled so we have shares to sell
        # Mock the buy order
        self.logger.debug(self.csv_service.get_row_by_index(0))
        self.logger.debug(self.csv_service.get_row_by_index(1))
        self.logger.info("Test 3 completed.")
        
        mock_sell_order = Mock()
        mock_sell_order.id = "test_sell_order_id"
        mock_sell_order.limit_price = 100.0  # Sell at exact sell_price
        mock_sell_order.side = 'sell'
        mock_sell_order.status = OrderStatus.NEW
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_sell_order

        # Trigger a sell order with a high price that matches sell threshold
        price_update_sell = {'type': 'price_update', 'data': 100.00}
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        #print index 0 and index 1 to logger.debug
        self.csv_service.logger.debug(self.csv_service.get_row_by_index(0))
        self.csv_service.logger.debug(self.csv_service.get_row_by_index(1))

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.SELL)
        self.assertEqual(args[1], 100.00)
        self.assertEqual(args[2], 1.0)

        self.assertEqual(self.csv_service.get_pending_order_info(), {"order_id": mock_sell_order.id, "index": 0})

        # Price update that will trigger a cancel from the decision maker
        price_update_cancel = {'type': 'price_update', 'data': 99.75}
        self.decision_maker.action_queue.put(price_update_cancel)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Ensure cancel was called
        self.assertTrue(self.alpaca_interface.cancel_order.called)
        self.alpaca_interface.cancel_order.assert_called_with(mock_sell_order.id)

        # Update the order status to CANCELED before triggering order update
        mock_sell_order.status = OrderStatus.CANCELED
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        mock_sell_order_update = Mock()
        mock_sell_order_update.order = mock_sell_order
        mock_sell_order_update.event = 'cancel' 
        
        # Trigger the order update
        self.decision_maker.action_queue.put({"type": MessageType.ORDER_UPDATE, "data": mock_sell_order_update})

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Check that the order was removed from pending_order_id
        self.assertIsNone(TestScaleTIntegrationMocked.csv_service.get_pending_order_info())
        row = TestScaleTIntegrationMocked.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 1)  # Still holding the share
        self.assertEqual(float(row['profit']), 0.0)
        self.assertEqual(float(row['unrealized_profit']), 0.0)

    @pytest.mark.order(4)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_sell_order_no_unrealized_profit_filled(self, mock_input, mock_send_notification):
        """Test a sell order that is placed and filled, with no unrealized profit."""
        # There is 1 share at index 0 so we will sell that one
        # Prepare price update to trigger sell order
        price_update_sell = {'type': 'price_update', 'data': 100.00}

        # mock sell order
        mock_sell_order = Mock()
        mock_sell_order.id = "test_sell_order_id_2"
        mock_sell_order.limit_price = 100.00  # Sell at exact sell_price
        mock_sell_order.side = 'sell'
        mock_sell_order.status = OrderStatus.NEW
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_sell_order

        # Trigger the sell order
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.SELL)
        self.assertEqual(args[1], 100.00)
        self.assertEqual(args[2], 1.0)

        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_sell_order.id)
        self.assertEqual(pending_order_info['index'], 0)

        # Update the mock order to be filled
        mock_sell_order.status = OrderStatus.FILLED
        mock_sell_order.filled_qty = '1'
        mock_sell_order.filled_avg_price = '100.00'  # Fill at exact sell_price

        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_sell_order
        mock_order_update.event = 'fill'

        # Set alpaca share count
        self.alpaca_interface.get_shares_count.return_value = 0

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)

        # Check that the CSV data was updated correctly
        row = TestScaleTIntegrationMocked.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 0)
        self.assertEqual(float(row['profit']), 0.5)
        self.assertEqual(float(row['unrealized_profit']), 0.0)

        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)


    @pytest.mark.order(5)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_buy_order_filled_unrealized_profit(self, mock_input, mock_send_notification):
        """Test a buy order that is filled at a better price than the limit price, resulting in unrealized profit."""
        # Prep alpaca interface to return a mock buy order
        mock_buy_order = Mock()
        mock_buy_order.id = "test_buy_order_id"
        mock_buy_order.limit_price = 99.24
        mock_buy_order.side = 'buy'
        mock_buy_order.status = OrderStatus.NEW
        mock_buy_order.filled_qty = '0'
        mock_buy_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_buy_order
        
        # create price update to be placed
        price_update_buy = {'type': 'price_update', 'data': 99.23}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for processing
        time.sleep(0.5)
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[1], 99.24)
        self.assertEqual(args[2], 1.0)

        
        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.logger.debug(f"Pending order info: {pending_order_info}, csv_service: {self.csv_service}, self: {self}")
        self.assertEqual(pending_order_info['order_id'], mock_buy_order.id)
        self.assertEqual(pending_order_info['index'], 0)

        # Update the mock order to be filled
        mock_buy_order.status = OrderStatus.FILLED
        mock_buy_order.filled_qty = '1'
        mock_buy_order.filled_avg_price = '99.24'
        
        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_buy_order
        mock_order_update.event = 'fill'
        
        # Set Alpaca share count
        self.alpaca_interface.get_shares_count.return_value = 1

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)
        
        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 1)
        self.assertEqual(float(row['profit']), 0.5)
        self.assertEqual(float(row['unrealized_profit']), 0.26)
        
        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)
        
        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 1)

    @pytest.mark.order(6)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_sell_order_canceled_unrealized_profit(self, mock_input, mock_send_notification):
        """Test a sell order with unrealized profit that is cancelled."""
        # Buy order filled previously, lets setup sell order
        mock_sell_order = Mock()
        mock_sell_order.id = "test_sell_order_id"
        mock_sell_order.limit_price = 100.00  # Sell at exact sell_price
        mock_sell_order.side = 'sell'
        mock_sell_order.status = OrderStatus.NEW
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_sell_order

        # Trigger a sell order with a high price that matches sell threshold
        price_update_sell = {'type': 'price_update', 'data': 100.00}
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for processing
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.SELL)
        self.assertEqual(args[1], 100.00)
        self.assertEqual(args[2], 1.0)

        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_sell_order.id)
        self.assertEqual(pending_order_info['index'], 0)

        # Trigger a cancel on price update
        price_update_cancel = {'type': 'price_update', 'data': 90.00}
        self.decision_maker.action_queue.put(price_update_cancel)
        
        # Allow some time for processing
        time.sleep(0.5)

        # Assert that cancel_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.cancel_order.called)
        args, kwargs = self.alpaca_interface.cancel_order.call_args
        self.assertEqual(args[0], mock_sell_order.id)
        
        # Update the mock order to be canceled
        mock_sell_order.status = OrderStatus.CANCELED
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None

        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_sell_order
        mock_order_update.event = 'cancel'

        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})

        # Allow some time for processing
        time.sleep(0.5)

        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 1)
        self.assertEqual(float(row['profit']), 0.5)
        self.assertEqual(float(row['unrealized_profit']), 0.26)

        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)   

        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 1)
        for row in self.csv_service.csv_data[:5]:
            self.decision_maker.logger.debug(row)
    
    @pytest.mark.order(7)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_sell_order_filled_unrealized_profit(self, mock_input, mock_send_notification):
        """Test a sell order that is placed and filled, with the unrealized profit being realized."""
        
        self.assertEqual(self.csv_service.get_current_held_shares(), 1)
        # Lets check the buy and sell price of index 0
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(row['buy_price'], '99.5')
        self.assertEqual(row['sell_price'], '100.0')
        self.assertEqual(row['held_shares'], 1)
        self.assertEqual(row['profit'], 0.5)
        self.assertEqual(row['unrealized_profit'], 0.26)

        # print csv_contents first five rows
        for row in self.csv_service.csv_data[:5]:
            self.decision_maker.logger.debug(row)
        
        # share is alread there. setup mock return submit order response
        mock_sell_order = Mock()
        mock_sell_order.id = "test_sell_order_id"
        mock_sell_order.limit_price = 100.00
        mock_sell_order.side = 'sell'
        mock_sell_order.status = OrderStatus.NEW
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_sell_order

        # Trigger a sell order with a high price that matches sell threshold
        price_update_sell = {'type': 'price_update', 'data': 100.00}
        self.decision_maker.action_queue.put(price_update_sell)
        # Allow some time for processing
        time.sleep(2)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.SELL)
        self.assertEqual(args[1], 100.00)
        self.assertEqual(args[2], 1.0)

        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_sell_order.id)
        self.assertEqual(pending_order_info['index'], 0)
        # Update the mock order to be filled
        mock_sell_order.status = OrderStatus.FILLED
        mock_sell_order.filled_qty = '1'
        mock_sell_order.filled_avg_price = '100.00'
        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_sell_order
        mock_order_update.event = 'fill'
        self.alpaca_interface.get_shares_count.return_value = 0
        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})
        # Allow some time for processing
        time.sleep(0.5)
        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 0)
        self.assertEqual(float(row['profit']), 1.26) # current_profit = .5, unrealized = .26. New profit = .5
        self.assertEqual(float(row['unrealized_profit']), 0.0)
        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)
        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)

    @pytest.mark.order(8)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_share_buy_then_sell_order_filled_unrealized_and_extreme_profit(self, mock_input, mock_send_notification):
        """Test a buy order that is placed and filled, with unrealized profit and extreme profit."""
        
        # Setup buy order
        mock_buy_order = Mock()
        mock_buy_order.id = "test_buy_order_id"
        mock_buy_order.limit_price = 99.20  # Buy at lower buy_price
        mock_buy_order.side = 'buy'
        mock_buy_order.status = OrderStatus.NEW
        mock_buy_order.filled_qty = '0'
        mock_buy_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_buy_order
        
        # Trigger a buy order with a low price that matches buy threshold
        price_update_buy = {'type': 'price_update', 'data': 99.19}
        self.decision_maker.action_queue.put(price_update_buy)
        
        # Allow some time for processing
        time.sleep(0.5)
        
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[1], 99.20)
        self.assertEqual(args[2], 1.0)

        
        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_buy_order.id)
        self.assertEqual(pending_order_info['index'], 0)
        
        # Update the mock order to be filled
        mock_buy_order.status = OrderStatus.FILLED
        mock_buy_order.filled_qty = '1'
        mock_buy_order.filled_avg_price = '99.20'
        
        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_buy_order
        mock_order_update.event = 'fill'
        
        # Set alpaca share count
        self.alpaca_interface.get_shares_count.return_value = 1
        
        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})
        
        # Allow some time for processing
        time.sleep(0.5)
        
        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 1)
        
        # Setup mock sell order
        mock_sell_order = Mock()
        mock_sell_order.id = "test_sell_order_id"
        mock_sell_order.limit_price = 119.99
        mock_sell_order.side = 'sell'
        mock_sell_order.status = OrderStatus.NEW
        mock_sell_order.filled_qty = '0'
        mock_sell_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_sell_order

        # Trigger a sell order with a high price that matches sell threshold
        price_update_sell = {'type': 'price_update', 'data': 120.00}
        self.decision_maker.action_queue.put(price_update_sell)
        
        # Allow some time for processing
        time.sleep(0.5)
        
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)

        # Get pending order id and check it matches
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_sell_order.id)
        self.assertEqual(pending_order_info['index'], 0)
        
        # Update the mock order to be filled
        mock_sell_order.status = OrderStatus.FILLED
        mock_sell_order.filled_qty = '1'
        mock_sell_order.filled_avg_price = '119.99'
        
        # Mock the order update
        mock_order_update = Mock()
        mock_order_update.order = mock_sell_order
        mock_order_update.event = 'fill'
        
        # Set alpaca share count
        self.alpaca_interface.get_shares_count.return_value = 0
        
        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})
        
        # Allow some time for processing
        time.sleep(0.5)
        
        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 0)
        self.assertEqual(float(row['profit']), round(0.30 + 1.26+19.99+0.50, 2))   # unrealized_profit = 0.30, current_profit = .76, {extreme_profit = 19.99, new_profit = 0.50}= 20.49
        self.assertEqual(float(row['unrealized_profit']), 0.0)
        
        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)
        
        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)

    # What if alpaca triggered a cancel and we received it as part of an order update?
    @pytest.mark.order(9)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_alpaca_canceled_the_order(self, mock_input, mock_send_notification):
        # Setup buy order
        mock_buy_order = Mock()
        mock_buy_order.id = "test_buy_order_id" 
        mock_buy_order.limit_price = 99.20  # Buy at lower buy_price
        mock_buy_order.side = 'buy'
        mock_buy_order.status = OrderStatus.NEW
        mock_buy_order.filled_qty = '0'
        mock_buy_order.filled_avg_price = None
        self.alpaca_interface.place_order.return_value = mock_buy_order

        # Trigger a buy order with a low price that matches buy threshold
        price_update_buy = {'type': 'price_update', 'data': 99.19}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for processing
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)

        # Checking pending order info
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertEqual(pending_order_info['order_id'], mock_buy_order.id)
        self.assertEqual(pending_order_info['index'], 0)

        # Suprising got an order update that order was cancelled
        mock_buy_order.status = OrderStatus.CANCELED
        mock_buy_order.filled_qty = '0' # No shares filled
        mock_buy_order.filled_avg_price = None
        mock_order_update = Mock()
        mock_order_update.order = mock_buy_order
        mock_order_update.event = 'cancel'
        
        # Put order update message on queue
        self.decision_maker.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': mock_order_update})
        
        # Allow some time for processing
        time.sleep(0.5)
        
        # Check that the pending order was removed
        pending_order_info = self.csv_service.get_pending_order_info()
        self.assertIsNone(pending_order_info)
        
        # Check that the share count was updated    
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)
        
        # Check that the CSV data was updated correctly
        row = self.csv_service.get_row_by_index(0)
        self.assertEqual(int(row['held_shares']), 0)


# TO RUN: pytest -s tests/bots/SCALE_T/integration/test_integrations.py


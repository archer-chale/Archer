import unittest
from unittest.mock import Mock, patch
import tempfile
import os
import csv
import threading
import time
import pytest

from main.bots.SCALE_T.brokerages import alpaca_interface
from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.trading.decision_maker import DecisionMaker
from alpaca.trading.enums import OrderStatus, OrderSide


class TestScaleTIntegrationMocked(unittest.TestCase):
    """Integration tests for the SCALE_T bot with mocked components."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for each test."""
        # Create a temporary directory
        cls.csv_file_path = os.path.join("data", "SCALE_T", "ticker_data", "paper", "TEST.csv")
        os.makedirs(os.path.dirname(cls.csv_file_path), exist_ok=True)

        # Generate CSV data
        header = "index,buy_price,sell_price,target_shares,held_shares,pending_order_id,spc,unrealized_profit,last_action,profit"
        data = [header]
        sell_price = 100.0
        for i in range(50):
            buy_price = round(sell_price * 0.995, 2)
            row = f"{i},{buy_price},{sell_price},6,0,None,N,0.0,,0.0"
            data.append(row)
            sell_price = buy_price

        """ CSV data current view

        index,buy_price,sell_price,target_shares,held_shares,pending_order_id,spc,unrealized_profit,last_action,profit
        0,99.5,100.0,6,0,None,N,0.0,,0.0
        1,99.0,99.5,6,0,None,N,0.0,,0.0
        2,98.5,99.0,6,0,None,N,0.0,,0.0
        3,98.01,98.5,6,0,None,N,0.0,,0.0
        4,97.52,98.01,6,0,None,N,0.0,,0.0
        5,97.03,97.52,6,0,None,N,0.0,,0.0
        """

        # Write CSV data to file
        with open(cls.csv_file_path, 'w', newline='') as csvfile:
            for row in data:
                csvfile.write(row + '\n')

        # Mock AlpacaInterface
        cls.alpaca_interface = Mock(spec=AlpacaInterface)
        cls.alpaca_interface.ticker = "TEST"
        cls.alpaca_interface.trading_type = "paper"

        # Mock AlpacaInterface initialization methods
        cls.mock_initial_price = 101.0
        cls.alpaca_interface.get_current_price.return_value = cls.mock_initial_price
        cls.mock_shares_count = 0
        cls.alpaca_interface.get_shares_count.return_value = cls.mock_shares_count

        # Instantiate CSVService and DecisionMaker
        cls.csv_service = CSVService("TEST", "paper")
        cls.decision_maker = DecisionMaker(
            csv_service=cls.csv_service, alpaca_interface=cls.alpaca_interface
        )

        # Create and start the consumer thread
        cls.consumer_thread = threading.Thread(target=cls._consume_actions_thread)
        cls.consumer_thread.daemon = True  # Allow the thread to exit when the main thread exits
        cls.consumer_thread.start()

    @classmethod
    def _consume_actions_thread(cls):
        """Continuously consume actions from the queue."""
        while True:
            cls.decision_maker.consume_actions()
            time.sleep(0.1)  # Short delay to prevent busy-waiting

    @classmethod
    def tearDownClass(cls):
        """Clean up after each test."""
        if os.path.exists(cls.csv_file_path):
            os.remove(cls.csv_file_path)

    @pytest.mark.order(201)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_multi_share_buy_order_no_fill_cancel(self, mock_input, mock_send_notification):
        """Test a buy order that is placed to cover multiple rows but not filled, then canceled (price increase)."""
        # Mock the order ID for the placed order, and its status
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.limit_price = 97.03  # Set the limit price for the mock order
        mock_placed_order.side = 'buy'  # Set the side for the mock order
        mock_placed_order.status = OrderStatus.NEW
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price update
        price_update_buy = {'type': 'price_update', 'data': 97.03}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)  # side
        self.assertEqual(args[1], 97.03)  # price
        self.assertEqual(args[2], 36.0)  # quantity

        # Simulate a price increase to trigger cancellation
        price_update_cancel = {'type': 'price_update', 'data': 101.00}
        self.decision_maker.action_queue.put(price_update_cancel)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that cancel_order was called
        self.assertTrue(self.alpaca_interface.cancel_order.called)
        self.alpaca_interface.cancel_order.assert_called_with(mock_placed_order.id)

        # Simulate order update coming on queue
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        mock_placed_order.status = OrderStatus.CANCELED
        mock_placed_order.filled_qty = 0
        mock_placed_order.filled_avg_price = None
        # print(mock_placed_order.id)
        # mock_placed_order.id = mock_placed_order.id
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # # Check that the CSV data was not updated (shares remain 0)
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # Check csv data on index 0
        row_zero = self.csv_service.get_row_by_index(0)
        self.assertEqual(row_zero["held_shares"], '0')
        self.assertEqual(row_zero["pending_order_id"], 'None')
        self.assertEqual(row_zero["unrealized_profit"], '0.0')
        self.assertEqual(row_zero["profit"], '0.0')


    @pytest.mark.order(202)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_multi_share_buy_order_partial_fill_cancel(self, mock_input, mock_send_notification):
        """Test a buy order that is placed to cover multiple rows but only partially filled, then canceled."""

        # Mock the order ID for the placed order, and its status
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.limit_price = 97.03  # Set the limit price for the mock order
        mock_placed_order.side = 'buy'  # Set the side for the mock order
        mock_placed_order.status = OrderStatus.NEW
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price update
        price_update_buy = {'type': 'price_update', 'data': 97.03}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)  # side
        self.assertEqual(args[1], 97.03)  # price
        self.assertEqual(args[2], 36.0)  # quantity

        # Trigger a price update to trigger cancellation
        price_update_cancel = {'type': 'price_update', 'data': 99.0}
        self.decision_maker.action_queue.put(price_update_cancel)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Assert that cancel_order was called
        self.assertTrue(self.alpaca_interface.cancel_order.called)
        args, kwargs = self.alpaca_interface.cancel_order.call_args
        self.assertEqual(args[0], "test_order_id_1")

        # Update alpaca share count before triggering order update
        self.alpaca_interface.get_shares_count.return_value = 18
        # Simulate order update coming on queue
        mock_placed_order = Mock()
        mock_placed_order.status = OrderStatus.CANCELED
        mock_placed_order.filled_qty = 18
        mock_placed_order.filled_avg_price = 97.03
        mock_placed_order.side = 'buy'
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was not updated (shares remain 0)
        self.assertEqual(self.csv_service.get_current_held_shares(), 18)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # print the top 6 indexes of the csv file
        for i in range(6):
            print(self.csv_service.get_row_by_index(i))

        # Check csv data at index 0, 2, 4
        row_zero = self.csv_service.get_row_by_index(1)
        self.assertEqual(row_zero["held_shares"], 6)
        self.assertEqual(row_zero["pending_order_id"], 'None')
        self.assertEqual(row_zero["unrealized_profit"], 11.82)
        self.assertEqual(row_zero["profit"], '0.0')

        row_two = self.csv_service.get_row_by_index(2)
        self.assertEqual(row_two["held_shares"], 6)
        self.assertEqual(row_two["pending_order_id"], 'None')
        self.assertEqual(row_two["unrealized_profit"], 8.82)
        self.assertEqual(row_two["profit"], '0.0')

        row_four = self.csv_service.get_row_by_index(3)
        self.assertEqual(row_four["held_shares"], '0')
        self.assertEqual(row_four["pending_order_id"], 'None')
        self.assertEqual(row_four["unrealized_profit"], '0.0')
        self.assertEqual(row_four["profit"], '0.0')


    @pytest.mark.order(203)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_multi_share_buy_order_full_fill(self, mock_input, mock_send_notification):
        """Test a buy order that is placed to cover multiple rows and fully filled."""
        # Current state is 3 shares held, top rows, 0 pending order
        # Put the same price update and we get 3 multi line order that we can process as filled
        # Mock submit order return
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.side = 'buy'
        mock_placed_order.limit_price = 97.52
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price update
        price_update_buy = {'type': 'price_update', 'data': 97.52}
        self.decision_maker.action_queue.put(price_update_buy)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[2], 12.0)
        self.assertEqual(args[1], 97.52)

        # Update alpaca share count before triggering order update
        self.alpaca_interface.get_shares_count.return_value = 18+12 

        # Trigger a full fill
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.filled_qty = 12
        mock_placed_order.filled_avg_price = 97.52
        mock_placed_order.side = 'buy'
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was updated (shares remain 0)
        self.assertEqual(self.csv_service.get_current_held_shares(), 30)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # Check csv data at index 3, 4
        row_three = self.csv_service.get_row_by_index(3)
        self.assertEqual(row_three["held_shares"], 6)
        self.assertEqual(row_three["pending_order_id"], 'None')
        self.assertEqual(row_three["unrealized_profit"], 2.94)
        self.assertEqual(row_three["profit"], '0.0')

        row_four = self.csv_service.get_row_by_index(4)
        self.assertEqual(row_four["held_shares"], 6)
        self.assertEqual(row_four["pending_order_id"], 'None')
        self.assertEqual(row_four["unrealized_profit"], 0)
        self.assertEqual(row_four["profit"], '0.0')


    @pytest.mark.order(204)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_multi_share_sell_order_partial_fill_cancel(self, mock_input, mock_send_notification):
        """Test a sell order that is placed to cover multiple rows but only partially filled, then canceled."""
        # Current state is 30 shares held, top 30 rows, 0 pending order
        # Mock submit order return
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.side = 'sell'
        mock_placed_order.limit_price = 100.52
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a sell order with a price update
        price_update_sell = {'type': 'price_update', 'data': 100.52}
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], "sell")
        self.assertEqual(args[2], 30.0)
        self.assertEqual(args[1], 100.51)

        # Update alpaca share count before triggering order update
        self.alpaca_interface.get_shares_count.return_value = 18

        # Trigger a price update that causes the order to be canceled
        price_update_cancel = {'type': 'price_update', 'data': 100.0}
        self.decision_maker.action_queue.put(price_update_cancel)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Assert that cancel_order was called
        self.assertTrue(self.alpaca_interface.cancel_order.called)
        args, kwargs = self.alpaca_interface.cancel_order.call_args
        self.assertEqual(args[0], "test_order_id_1")

        # Send update order for cancel
        mock_placed_order.status = OrderStatus.CANCELED
        mock_placed_order.filled_qty = 12
        mock_placed_order.filled_avg_price = 100.51
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was not updated (shares remain 18)
        self.assertEqual(self.csv_service.get_current_held_shares(), 18)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # Check csv data at index 2, 3
        row_two = self.csv_service.get_row_by_index(2)
        self.assertEqual(row_two["held_shares"], 6)
        self.assertEqual(row_two["pending_order_id"], 'None')
        self.assertEqual(row_two["unrealized_profit"], 8.82)
        self.assertEqual(row_two["profit"], '0.0')

        row_three = self.csv_service.get_row_by_index(3)
        self.assertEqual(row_three["held_shares"], 0)
        self.assertEqual(row_three["pending_order_id"], 'None')
        self.assertEqual(row_three["unrealized_profit"], 0.0)
        self.assertEqual(row_three["profit"], 2.94+(6*(100.51-98.01)))
        

    @pytest.mark.order(205)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_multi_share_sell_order_full_fill(self, mock_input, mock_send_notification):
        """Test a sell order that is placed to cover multiple rows and fully filled."""
        # Current state is 30 shares held, top 30 rows, 0 pending order
        # Mock submit order return
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.side = 'sell'
        mock_placed_order.limit_price = 100.51
        mock_placed_order.qty = 18
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a sell order with a price update
        price_update_sell = {'type': 'price_update', 'data': 100.52}
        self.decision_maker.action_queue.put(price_update_sell)

        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], "sell")
        self.assertEqual(args[2], 18)
        self.assertEqual(args[1], 100.51)

        # Trigger an order update that triggers a fill
        self.alpaca_interface.get_shares_count.return_value = 0
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.filled_qty = 18
        mock_placed_order.filled_avg_price = 100.51
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was updated (shares remain 18)
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # Check csv data at index 0,1,2,3,4,5
        row_zero = self.csv_service.get_row_by_index(0)
        self.assertEqual(row_zero["held_shares"], 0)
        self.assertEqual(row_zero["pending_order_id"], 'None')
        self.assertEqual(row_zero["unrealized_profit"], 0.0)
        self.assertEqual(row_zero["profit"], round(6*(100.51-97.03), 2))

        row_one = self.csv_service.get_row_by_index(1)
        self.assertEqual(row_one["held_shares"], 0)
        self.assertEqual(row_one["pending_order_id"], 'None')
        self.assertEqual(row_one["unrealized_profit"], 0.0)
        self.assertEqual(row_one["profit"], round(6*(100.51-97.03), 2))

        row_two = self.csv_service.get_row_by_index(2)
        self.assertEqual(row_two["held_shares"], 0)
        self.assertEqual(row_two["pending_order_id"], 'None')
        self.assertEqual(row_two["unrealized_profit"], 0.0)
        self.assertEqual(row_two["profit"], round(6*(100.51-97.03), 2))

        row_three = self.csv_service.get_row_by_index(3)
        self.assertEqual(row_three["held_shares"], 0)
        self.assertEqual(row_three["pending_order_id"], 'None')
        self.assertEqual(row_three["unrealized_profit"], 0.0)
        self.assertEqual(row_three["profit"], round(6*(100.51-97.52), 2))

        row_four = self.csv_service.get_row_by_index(4)
        self.assertEqual(row_four["held_shares"], 0)
        self.assertEqual(row_four["pending_order_id"], 'None')
        self.assertEqual(row_four["unrealized_profit"], 0.0)
        self.assertEqual(row_four["profit"], round(6*(100.51-97.52), 2))
        
        row_five = self.csv_service.get_row_by_index(5)
        self.assertEqual(row_five["held_shares"], '0')
        self.assertEqual(row_five["pending_order_id"], 'None')
        self.assertEqual(row_five["unrealized_profit"], '0.0')
        self.assertEqual(row_five["profit"], '0.0')


    @pytest.mark.order(206)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_single_line_multi_share_buy_order_partial_fill_cancel(self, mock_input, mock_send_notification):
        """Test a buy order that is placed to cover 1 row but paritally filled and cancelled"""
        # Mock submit order return
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.status = OrderStatus.NEW
        mock_placed_order.side = 'buy'
        mock_placed_order.symbol = "TEST"
        self.alpaca_interface.place_order.return_value = mock_placed_order

        # Trigger a buy order with a price update
        price_update_buy = {'type': 'price_update', 'data': 99.48}
        self.decision_maker.action_queue.put(price_update_buy)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Assert that place_order was called with correct parameters
        self.assertTrue(self.alpaca_interface.place_order.called)
        args, kwargs = self.alpaca_interface.place_order.call_args
        self.assertEqual(args[0], OrderSide.BUY)
        self.assertEqual(args[2], 6.0)
        self.assertEqual(args[1], 99.49)

        # Trigger order update but to pending status
        self.alpaca_interface.get_shares_count.return_value = 4  
        mock_placed_order.status = OrderStatus.CANCELED
        mock_placed_order.filled_qty = 4
        mock_placed_order.filled_avg_price = 99.49
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was not updated (shares remain 4)
        self.assertEqual(self.csv_service.get_current_held_shares(), 4)
        self.assertIsNone(self.csv_service.get_pending_order_info())

        # Check csv data at index 0
        row_zero = self.csv_service.get_row_by_index(0)
        self.assertEqual(row_zero["held_shares"], 4)
        self.assertEqual(row_zero["pending_order_id"], 'None')
        self.assertEqual(row_zero["unrealized_profit"], 0.04)
        self.assertEqual(row_zero["profit"], round(6*(100.51-97.03), 2))

        # Check csv data at index 1
        row_one = self.csv_service.get_row_by_index(1)
        self.assertEqual(row_one["held_shares"], 0)
        self.assertEqual(row_one["pending_order_id"], 'None')
        self.assertEqual(row_one["unrealized_profit"], 0.0)
        self.assertEqual(row_one["profit"], round(6*(100.51-97.03), 2))

    @pytest.mark.order(207)
    @patch('main.bots.SCALE_T.trading.decision_maker.send_notification')
    @patch('builtins.input', return_value='y')
    def test_multi_line_sell_order_full_fill_on_partially_filled_buy(self, mock_input, mock_send_notification):
        """Test a sell order that is placed to cover single partial row and fully filled."""

        # Mock order update
        mock_placed_order = Mock()
        mock_placed_order.id = "test_order_id_1"
        mock_placed_order.status = OrderStatus.PENDING_NEW   
        mock_placed_order.side = 'sell'
        mock_placed_order.symbol = "TEST"
        self.alpaca_interface.place_order.return_value = mock_placed_order

        #send price update
        price_update_sell = {'type': 'price_update', 'data': 100.51}
        self.decision_maker.action_queue.put(price_update_sell)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)

        # send order update
        mock_placed_order.filled_qty = 4
        mock_placed_order.filled_avg_price = 100.51
        mock_placed_order.status = OrderStatus.FILLED
        mock_placed_order.side = 'sell'
        mock_placed_order.symbol = "TEST"
        mock_placed_order.id = "test_order_id_1"
        mock_order_update = Mock()
        mock_order_update.event = "order_update"
        mock_order_update.order = mock_placed_order
        self.alpaca_interface.get_shares_count.return_value = 0
        order_update = {'type': 'order_update', 'data': mock_order_update}
        self.decision_maker.action_queue.put(order_update)
        # Allow some time for the consumer thread to process
        time.sleep(0.5)
        # Check that the CSV data was updated (shares are now 0)
        self.assertEqual(self.csv_service.get_current_held_shares(), 0)
        self.assertIsNone(self.csv_service.get_pending_order_info())

# TO RUN: pytest -s --maxfail=1 tests/bots/SCALE_T/integration/test_integrations2.py


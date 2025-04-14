# import unittest
# from unittest.mock import Mock, patch, MagicMock
# from alpaca.trading.enums import OrderStatus

# # Import the DecisionMaker class
# from main.bots.SCALE_T.trading.decision_maker import DecisionMaker


# class TestDecisionMaker(unittest.TestCase):
#     """Test cases for the DecisionMaker class."""

#     def setUp(self):
#         """Set up test fixtures before each test method."""
#         # Create mock objects for the dependencies
#         self.mock_csv_service = Mock()
#         self.mock_alpaca_interface = Mock()
        
#         # Configure the mocks with default return values
#         self.mock_csv_service.get_pending_order_info.return_value = None
#         self.mock_alpaca_interface.get_shares_count.return_value = 10
#         self.mock_csv_service.get_current_held_shares.return_value = 10
#         self.mock_csv_service.ticker = "AAPL"
        
#         # Create an instance of DecisionMaker with the mocks
#         self.decision_maker = DecisionMaker(
#             self.mock_csv_service,
#             self.mock_alpaca_interface
#         )

#     def test_init_no_pending_order(self):
#         """Test initialization with no pending order."""
#         # Assertions for the initialization with no pending order
#         self.assertIsNone(self.decision_maker.pending_order)
#         self.assertIsNone(self.decision_maker.pending_order_index)
#         self.mock_csv_service.get_pending_order_info.assert_called_once()
#         self.mock_alpaca_interface.get_shares_count.assert_called_once()
#         self.mock_csv_service.get_current_held_shares.assert_called_once()

#     # def test_init_with_pending_order(self):
#         """Test initialization with a pending order."""
#         # Reset mocks
#         self.mock_csv_service.reset_mock()
#         self.mock_alpaca_interface.reset_mock()
        
#         # Configure mocks for this test case
#         mock_order = Mock()
#         # Set a valid order status to avoid error in handle_order_update
#         mock_order.status = OrderStatus.NEW
#         mock_order.filled_qty = 0
#         mock_order.filled_avg_price = 0
#         mock_order.side = "buy"
        
#         self.mock_csv_service.get_pending_order_info.return_value = {
#             "order_id": "test_order_id",
#             "index": 1
#         }
#         self.mock_alpaca_interface.get_order_by_id.return_value = mock_order
        
#         # Create a new instance with the configured mocks
#         decision_maker = DecisionMaker(
#             self.mock_csv_service,
#             self.mock_alpaca_interface
#         )
        
#         # Assertions
#         self.assertEqual(decision_maker.pending_order, mock_order)
#         self.assertEqual(decision_maker.pending_order_index, 1)
#         self.mock_alpaca_interface.get_order_by_id.assert_called_once_with("test_order_id")

#     def test_init_share_count_mismatch(self):
#         """Test initialization with mismatched share counts."""
#         # Reset mocks
#         self.mock_csv_service.reset_mock()
#         self.mock_alpaca_interface.reset_mock()
        
#         # Configure mocks for this test case
#         self.mock_alpaca_interface.get_shares_count.return_value = 10
#         self.mock_csv_service.get_current_held_shares.return_value = 5
        
#         # Expect a ValueError due to share count mismatch
#         with self.assertRaises(ValueError):
#             DecisionMaker(
#                 self.mock_csv_service,
#                 self.mock_alpaca_interface
#             )

#     def test_handle_order_update_filled(self):
#         """Test handling of a filled order."""
#         # Configure mock order with FILLED status
#         mock_order = Mock()
#         mock_order.status = OrderStatus.FILLED
#         mock_order.filled_qty = 5
#         mock_order.filled_avg_price = 150.00
#         mock_order.side = "buy"
        
#         # Set the pending order and index
#         self.decision_maker.pending_order = mock_order
#         self.decision_maker.pending_order_index = 1
        
#         # Call the method to test
#         self.decision_maker.handle_order_update()
        
#         # Verify that update_order_status was called with correct parameters
#         self.mock_csv_service.update_order_status.assert_called_once_with(
#             1, 5, 150.00, "buy"
#         )

#     def test_handle_order_update_canceled(self):
#         """Test handling of a canceled order."""
#         # Configure mock order with CANCELED status
#         mock_order = Mock()
#         mock_order.status = OrderStatus.CANCELED
#         mock_order.filled_qty = 0
#         mock_order.filled_avg_price = 0
#         mock_order.side = "buy"
        
#         # Set the pending order and index
#         self.decision_maker.pending_order = mock_order
#         self.decision_maker.pending_order_index = 1
        
#         # Call the method to test
#         self.decision_maker.handle_order_update()
        
#         # Verify that update_order_status was called with correct parameters
#         self.mock_csv_service.update_order_status.assert_called_once_with(
#             1, 0, 0, "buy"
#         )

#     def test_handle_order_update_pending(self):
#         """Test handling of a pending order."""
#         # Test for different pending statuses
#         pending_statuses = [
#             OrderStatus.ACCEPTED,
#             OrderStatus.NEW,
#             OrderStatus.PARTIALLY_FILLED,
#             OrderStatus.PENDING_NEW,
#             OrderStatus.PENDING_CANCEL
#         ]
        
#         for status in pending_statuses:
#             # Reset mock and configure order with pending status
#             self.mock_csv_service.reset_mock()
#             mock_order = Mock()
#             mock_order.status = status
            
#             # Set the pending order and index
#             self.decision_maker.pending_order = mock_order
#             self.decision_maker.pending_order_index = 1
            
#             # Call the method to test
#             self.decision_maker.handle_order_update()
            
#             # Verify that update_order_status was NOT called
#             self.mock_csv_service.update_order_status.assert_not_called()

#     def test_handle_order_update_unexpected(self):
#         """Test handling of an unexpected order status."""
#         # Configure mock order with an unexpected status
#         mock_order = Mock()
#         mock_order.status = "UNKNOWN_STATUS"
        
#         # Set the pending order and index
#         self.decision_maker.pending_order = mock_order
#         self.decision_maker.pending_order_index = 1
        
#         # Expect a ValueError due to unexpected status
#         with self.assertRaises(ValueError):
#             self.decision_maker.handle_order_update()

#     def test_check_cancel_order_buy_price_increase(self):
#         """Test cancellation of buy order when price increases."""
#         # Configure a mock pending buy order
#         mock_order = Mock()
#         mock_order.side = "buy"
#         mock_order.limit_price = "100.00"
#         mock_order.id = "test_order_id"
        
#         # Set the pending order
#         self.decision_maker.pending_order = mock_order
        
#         # Test with price that's 0.3% above limit (should cancel)
#         result = self.decision_maker._check_cancel_order(100.30)
        
#         # Verify that cancel_order was called and result is True
#         self.mock_alpaca_interface.cancel_order.assert_called_once_with("test_order_id")
#         self.assertTrue(result)

#     def test_check_cancel_order_buy_no_cancel(self):
#         """Test buy order not cancelled when price is below threshold."""
#         # Configure a mock pending buy order
#         mock_order = Mock()
#         mock_order.side = "buy"
#         mock_order.limit_price = "100.00"
#         mock_order.id = "test_order_id"
        
#         # Set the pending order
#         self.decision_maker.pending_order = mock_order
        
#         # Test with price that's 0.2% above limit (should NOT cancel)
#         result = self.decision_maker._check_cancel_order(100.20)
        
#         # Verify that cancel_order was NOT called and result is False
#         self.mock_alpaca_interface.cancel_order.assert_not_called()
#         self.assertFalse(result)

#     def test_check_cancel_order_sell_price_decrease(self):
#         """Test cancellation of sell order when price decreases."""
#         # Configure a mock pending sell order
#         mock_order = Mock()
#         mock_order.side = "sell"
#         mock_order.limit_price = "100.00"
#         mock_order.id = "test_order_id"
        
#         # Set the pending order
#         self.decision_maker.pending_order = mock_order
        
#         # Test with price that's 0.3% below limit (should cancel)
#         result = self.decision_maker._check_cancel_order(99.70)
        
#         # Verify that cancel_order was called and result is True
#         self.mock_alpaca_interface.cancel_order.assert_called_once_with("test_order_id")
#         self.assertTrue(result)

#     def test_check_cancel_order_sell_no_cancel(self):
#         """Test sell order not cancelled when price is above threshold."""
#         # Configure a mock pending sell order
#         mock_order = Mock()
#         mock_order.side = "sell"
#         mock_order.limit_price = "100.00"
#         mock_order.id = "test_order_id"
        
#         # Set the pending order
#         self.decision_maker.pending_order = mock_order
        
#         # Test with price that's 0.2% below limit (should NOT cancel)
#         result = self.decision_maker._check_cancel_order(99.80)
        
#         # Verify that cancel_order was NOT called and result is False
#         self.mock_alpaca_interface.cancel_order.assert_not_called()
#         self.assertFalse(result)

#     def test_check_cancel_order_no_pending_order(self):
#         """Test cancel check when there's no pending order."""
#         # Set pending_order to None
#         self.decision_maker.pending_order = None
        
#         # Test cancel check
#         result = self.decision_maker._check_cancel_order(100.00)
        
#         # Verify that cancel_order was NOT called and result is False
#         self.mock_alpaca_interface.cancel_order.assert_not_called()
#         self.assertFalse(result)

#     def test_check_place_buy_order_success(self):
#         """Test successful placement of buy order."""
#         # Configure CSV manager to return rows for buy
#         rows_to_buy = [
#             {"index": "1", "target_shares": "5", "held_shares": "0", "buy_price": "99.00"},
#             {"index": "2", "target_shares": "5", "held_shares": "0", "buy_price": "98.00"}
#         ]
#         self.mock_csv_service.get_rows_for_buy.return_value = rows_to_buy
        
#         # Configure mock order
#         mock_order = Mock()
#         mock_order.id = "new_order_id"
#         self.mock_alpaca_interface.submit_order.return_value = mock_order
        
#         # Test buy order placement with current price
#         result = self.decision_maker._check_place_buy_order(98.50)
        
#         # Get the actual arguments used in the submit_order call
#         call_args = self.mock_alpaca_interface.submit_order.call_args
#         self.assertIsNotNone(call_args, "submit_order was not called")
        
#         # Extract the actual order data passed
#         actual_order_data = call_args[0][0]
        
#         # Verify individual fields of the order data
#         self.assertEqual(actual_order_data['symbol'], "AAPL")
#         self.assertEqual(actual_order_data['qty'], "10")
#         self.assertEqual(actual_order_data['side'], 'buy')
#         self.assertEqual(actual_order_data['type'], 'limit')
#         self.assertEqual(float(actual_order_data['limit_price']), 98.0)  # Compare as floats
#         self.assertEqual(actual_order_data['time_in_force'], 'day')
        
#         # Verify that the decision_maker state was updated correctly
#         self.assertEqual(self.decision_maker.pending_order, mock_order)
#         self.assertEqual(self.decision_maker.pending_order_index, 2)  # Highest index (lowest price)
        
#         # Verify that CSV was updated and saved
#         self.mock_csv_service.save.assert_called_once()
#         self.assertTrue(result)

#     def test_check_place_buy_order_no_rows(self):
#         """Test no buy order placed when no rows are found."""
#         # Configure CSV manager to return no rows for buy
#         self.mock_csv_service.get_rows_for_buy.return_value = []
        
#         # Test buy order placement with current price
#         result = self.decision_maker._check_place_buy_order(98.50)
        
#         # Verify that submit_order was NOT called
#         self.mock_alpaca_interface.submit_order.assert_not_called()
        
#         # Verify that the result is False
#         self.assertFalse(result)

#     def test_check_place_buy_order_exception(self):
#         """Test exception handling when placing buy order."""
#         # Configure CSV manager to return rows for buy
#         rows_to_buy = [
#             {"index": "1", "target_shares": "5", "held_shares": "0", "buy_price": "99.00"}
#         ]
#         self.mock_csv_service.get_rows_for_buy.return_value = rows_to_buy
        
#         # Configure submit_order to raise an exception
#         self.mock_alpaca_interface.submit_order.side_effect = Exception("Submit order error")
        
#         # Test buy order placement with current price
#         result = self.decision_maker._check_place_buy_order(98.50)
        
#         # Verify that submit_order was called
#         self.mock_alpaca_interface.submit_order.assert_called_once()
        
#         # Verify that the result is False due to exception
#         self.assertFalse(result)

#     def test_check_place_sell_order_success(self):
#         """Test successful placement of sell order."""
#         # Configure CSV manager to return rows for sell
#         rows_to_sell = [
#             {"index": "3", "held_shares": "3", "sell_price": "101.00"},
#             {"index": "4", "held_shares": "7", "sell_price": "102.00"}
#         ]
#         self.mock_csv_service.get_rows_for_sell.return_value = rows_to_sell
        
#         # Configure mock order
#         mock_order = Mock()
#         mock_order.id = "new_order_id"
#         self.mock_alpaca_interface.submit_order.return_value = mock_order
        
#         # Test sell order placement with current price
#         result = self.decision_maker._check_place_sell_order(101.50)
        
#         # Verify that submit_order was called with correct parameters
#         expected_order_data = {
#             'symbol': "AAPL",
#             'qty': "10",  # Total of 3+7 from both rows
#             'side': 'sell',
#             'type': 'limit',
#             'limit_price': "101.49",  # Max of current-0.01 and lowest sell_price
#             'time_in_force': 'day',
#         }
#         self.mock_alpaca_interface.submit_order.assert_called_once_with(expected_order_data)
        
#         # Verify that the decision_maker state was updated correctly
#         self.assertEqual(self.decision_maker.pending_order, mock_order)
#         self.assertEqual(self.decision_maker.pending_order_index, 3)  # Lowest index (lowest price)
        
#         # Verify that CSV was updated and saved
#         self.mock_csv_service.save.assert_called_once()
#         self.assertTrue(result)

#     def test_check_place_sell_order_no_rows(self):
#         """Test no sell order placed when no rows are found."""
#         # Configure CSV manager to return no rows for sell
#         self.mock_csv_service.get_rows_for_sell.return_value = []
        
#         # Test sell order placement with current price
#         result = self.decision_maker._check_place_sell_order(101.50)
        
#         # Verify that submit_order was NOT called
#         self.mock_alpaca_interface.submit_order.assert_not_called()
        
#         # Verify that the result is False
#         self.assertFalse(result)

#     def test_check_place_sell_order_exception(self):
#         """Test exception handling when placing sell order."""
#         # Configure CSV manager to return rows for sell
#         rows_to_sell = [
#             {"index": "3", "held_shares": "5", "sell_price": "101.00"}
#         ]
#         self.mock_csv_service.get_rows_for_sell.return_value = rows_to_sell
        
#         # Configure submit_order to raise an exception
#         self.mock_alpaca_interface.submit_order.side_effect = Exception("Submit order error")
        
#         # Test sell order placement with current price
#         result = self.decision_maker._check_place_sell_order(101.50)
        
#         # Verify that submit_order was called
#         self.mock_alpaca_interface.submit_order.assert_called_once()
        
#         # Verify that the result is False due to exception
#         self.assertFalse(result)

#     def test_handle_price_update_cancel_order(self):
#         """Test price update handling with order cancellation."""
#         # Mock the _check_cancel_order method to return True
#         self.decision_maker._check_cancel_order = Mock(return_value=True)
#         self.decision_maker._check_place_sell_order = Mock()
#         self.decision_maker._check_place_buy_order = Mock()
        
#         # Test price update handling
#         price_data = {"price": 100.00}
#         self.decision_maker.handle_price_update(price_data)
        
#         # Verify that _check_cancel_order was called
#         self.decision_maker._check_cancel_order.assert_called_once_with(100.00)
        
#         # Verify that _check_place_sell_order and _check_place_buy_order were NOT called
#         self.decision_maker._check_place_sell_order.assert_not_called()
#         self.decision_maker._check_place_buy_order.assert_not_called()

#     def test_handle_price_update_place_sell_order(self):
#         """Test price update handling with sell order placement."""
#         # Mock methods with appropriate return values
#         self.decision_maker._check_cancel_order = Mock(return_value=False)
#         self.decision_maker._check_place_sell_order = Mock(return_value=True)
#         self.decision_maker._check_place_buy_order = Mock()
        
#         # Test price update handling
#         price_data = {"price": 100.00}
#         self.decision_maker.handle_price_update(price_data)
        
#         # Verify that methods were called in correct order
#         self.decision_maker._check_cancel_order.assert_called_once_with(100.00)
#         self.decision_maker._check_place_sell_order.assert_called_once_with(100.00)
        
#         # Verify that _check_place_buy_order was NOT called
#         self.decision_maker._check_place_buy_order.assert_not_called()

#     def test_handle_price_update_place_buy_order(self):
#         """Test price update handling with buy order placement."""
#         # Mock methods with appropriate return values
#         self.decision_maker._check_cancel_order = Mock(return_value=False)
#         self.decision_maker._check_place_sell_order = Mock(return_value=False)
#         self.decision_maker._check_place_buy_order = Mock()
        
#         # Test price update handling
#         price_data = {"price": 100.00}
#         self.decision_maker.handle_price_update(price_data)
        
#         # Verify that all methods were called in correct order
#         self.decision_maker._check_cancel_order.assert_called_once_with(100.00)
#         self.decision_maker._check_place_sell_order.assert_called_once_with(100.00)
#         self.decision_maker._check_place_buy_order.assert_called_once_with(100.00)

#     def test_consume_actions_order_update(self):
#         """Test consuming an order update action."""
#         # Create a mock action queue
#         self.decision_maker.action_queue = Mock()
        
#         # Configure the queue.get to return an order update message and then raise an exception
#         self.decision_maker.action_queue.get.side_effect = [
#             {"type": "order_update", "data": {}},
#             Exception("Stop loop")
#         ]
        
#         # Mock the handle_order_update method
#         self.decision_maker.handle_order_update = Mock()
        
#         # Call consume_actions (it will run until the exception is raised)
#         with self.assertRaises(Exception):
#             self.decision_maker.consume_actions()
        
#         # Verify that handle_order_update was called
#         self.decision_maker.handle_order_update.assert_called_once()
        
#         # Verify that task_done was called
#         self.decision_maker.action_queue.task_done.assert_called_once()

#     def test_consume_actions_price_update(self):
#         """Test consuming a price update action."""
#         # Create a mock action queue
#         self.decision_maker.action_queue = Mock()
        
#         # Configure the queue.get to return a price update message and then raise an exception
#         price_data = {"price": 100.00}
#         self.decision_maker.action_queue.get.side_effect = [
#             {"type": "price_update", "data": price_data},
#             Exception("Stop loop")
#         ]
        
#         # Mock the handle_price_update method
#         self.decision_maker.handle_price_update = Mock()
        
#         # Call consume_actions (it will run until the exception is raised)
#         with self.assertRaises(Exception):
#             self.decision_maker.consume_actions()
        
#         # Verify that handle_price_update was called with correct data
#         self.decision_maker.handle_price_update.assert_called_once_with(price_data)
        
#         # Verify that task_done was called
#         self.decision_maker.action_queue.task_done.assert_called_once()


# if __name__ == "__main__":
#     unittest.main()

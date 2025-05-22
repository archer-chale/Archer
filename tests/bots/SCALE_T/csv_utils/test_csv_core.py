"""Unit tests for CSVService class in the SCALE_T bot."""

import unittest
from unittest.mock import patch, mock_open
import json

from main.bots.SCALE_T.csv_utils.csv_core import CSVCore
from main.bots.SCALE_T.common.constants import TradingType

class TestCsvCore(unittest.TestCase):
    """
    Test cases for CSVService class.
    1. Init testing. Isolate the internal function calls
    2. Individual function calls
        - _save_csv_data
        - _load_csv_data -**
        - _get_column_names
        - validate_csv_data
        - _get_required_columns
        - _load_metadata
    """
    @classmethod
    def setUpClass(cls):
        cls.ticker = "TEST"
        cls.trading_type = TradingType.PAPER
        cls.test_csv_core1 = CSVCore(ticker=cls.ticker, trading_type=cls.trading_type)

    def test_init_success(self):
        """ Currently init just assigns stuff. Leaving the method calls to their own tests"""
        self.assertEqual(self.test_csv_core1.ticker, self.ticker)
        self.assertEqual(self.test_csv_core1.trading_type, self.trading_type)

    # 3 major cases
    # - File is there and there is not exception. - no validate failure
    @patch('main.bots.SCALE_T.csv_utils.csv_core.CSVCore.validate_csv_data')
    @patch('csv.DictReader')
    @patch('builtins.open')
    def test_load_csv_data_success(self, mock_open, mock_csv_dictreader, mock_validate_csv):
        my_list = ["test", "list"]
        mock_csv_dictreader.return_value = my_list
        self.assertTrue(self.test_csv_core1.csv_data == my_list)
        self.test_csv_core1._load_csv_data()
        self.assertEqual(self.test_csv_core1.csv_data, my_list)

    # - FileNotFoundError - only one way to trigger this
    @patch('builtins.open', side_effect=FileNotFoundError("FILE not found"))
    def test_load_csv_data_file_not_found(self, mock_file):
        with self.assertRaises(FileNotFoundError) as context:
            self.test_csv_core1._load_csv_data()

    # - Generic Exceptions - possible multiple ways to trigger this
    @patch('csv.DictReader')
    @patch('builtins.open', new_callable=mock_open, read_data="da")
    def test_load_csv_data_generic_exception1(self, mock_file, mock_csv_dictreader):
        def mr_exception(file_descriptor):
            raise Exception("some error")
        mock_csv_dictreader.side_effect = mr_exception
        with self.assertRaises(Exception) as context:
            self.test_csv_core1._load_csv_data()
        self.assertIn("Error loading CSV data:", str(context.exception))

    @patch('main.bots.SCALE_T.csv_utils.csv_core.CSVCore.validate_csv_data')
    @patch('csv.DictReader')
    @patch('builtins.open', new_callable=mock_open, read_data="da")
    def test_load_csv_data_generic_exception2(self, mock_file, mock_csv_dictreader, validate_csv_data):
        my_list = ["test", "list"]
        mock_csv_dictreader.return_value = my_list
        exception_msg = "another exception"
        def mr_exception():
            raise Exception(exception_msg)
        validate_csv_data.side_effect = mr_exception
        with self.assertRaises(Exception) as context:
            self.test_csv_core1._load_csv_data()
        self.assertIn(f"Error loading CSV data: {exception_msg}", str(context.exception))

    # load metadata
    # successful open and load
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({"my": "data"}))
    def test_load_metadata_success(self, mock_file):
        ret = self.test_csv_core1._load_metadata()
        self.assertEqual(ret, {"my": "data"})

    # failure triggering file not found exception and returning empty {}
    @patch('builtins.open', side_effect=FileNotFoundError("FILE not found"))
    def test_load_metadata_file_not_found(self, mock_file):
        ret = self.test_csv_core1._load_metadata()
        self.assertEqual(ret, {})

    # Generic exception
    # @patch('json.load', side_effect=Exception("hello exception"))
    @patch('builtins.open', new_callable=mock_open, read_data="hi")
    def test_load_metadata_generic_exception(self, mock_file):
        ret = self.test_csv_core1._load_metadata()
        self.assertEqual(ret, {})

    # get_required columns
    def test_get_required_columns_with_required_columns(self):
        """Test that required columns are correctly identified from metadata."""
        self.test_csv_core1.metadata = {
            "versions": [
                {
                    "columns": [
                        {"name": "index", "config": {"required": True}},
                        {"name": "target_shares", "config": {"required": True}},
                        {"name": "buy_price", "config": {"required": False}}
                    ]
                }
            ]
        }
        result = self.test_csv_core1._get_required_columns()
        self.assertEqual(result, ["index", "target_shares"])

    def test_get_required_columns_empty_result(self):
        """Test that empty list is returned when no columns are required."""
        self.test_csv_core1.metadata = {
            "versions": [
                {
                    "columns": [
                        {"name": "column1", "config": {"required": False}},
                        {"name": "column2", "config": {}}
                    ]
                }
            ]
        }
        result = self.test_csv_core1._get_required_columns()
        self.assertEqual(result, [])

    def test_get_required_columns_empty_metadata(self):
        """Test that empty list is returned when metadata is empty."""
        self.test_csv_core1.metadata = {}
        result = self.test_csv_core1._get_required_columns()
        self.assertEqual(result, [])

    def test_get_required_columns_no_versions(self):
        """Test that empty list is returned when versions key is missing."""
        self.test_csv_core1.metadata = {"other_key": "value"}
        result = self.test_csv_core1._get_required_columns()
        self.assertEqual(result, [])

    def test_get_required_columns_empty_versions(self):
        """Test that empty list is returned when versions list is empty."""
        self.test_csv_core1.metadata = {"versions": []}
        result = self.test_csv_core1._get_required_columns()
        self.assertEqual(result, [])

    # validate_csv_data
    def test_validate_csv_data_empty(self):
        """Test that empty data validation passes without error."""
        self.test_csv_core1.csv_data = []
        self.test_csv_core1.validate_csv_data()  # Should return without error

    def test_validate_csv_data_required_columns_present(self):
        """Test validation with all required columns present."""
        self.test_csv_core1.required_columns = ["index", "target_shares"]
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "100",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        self.test_csv_core1.validate_csv_data()  # Should not raise exception

    def test_validate_csv_data_missing_required_column(self):
        """Test validation fails when required column is missing."""
        self.test_csv_core1.required_columns = ["index", "target_shares"]
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        with self.assertRaises(ValueError) as context:
            self.test_csv_core1.validate_csv_data()
        self.assertIn("Missing required column: target_shares", str(context.exception))
    
    def test_validate_csv_data_valid_numeric_types(self):
        """Test validation with valid numeric values."""
        self.test_csv_core1.required_columns = []  # No required columns for this test
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "100",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        self.test_csv_core1.validate_csv_data()  # Should not raise exception

    def test_validate_csv_data_invalid_index(self):
        """Test validation fails with non-integer index."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [{
            "index": "not_a_number",
            "target_shares": "100",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        with self.assertRaises(ValueError):
            self.test_csv_core1.validate_csv_data()

    def test_validate_csv_data_invalid_target_shares(self):
        """Test validation fails with non-numeric target_shares."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "invalid",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        with self.assertRaises(ValueError):
            self.test_csv_core1.validate_csv_data()

    def test_validate_csv_data_invalid_prices(self):
        """Test validation fails with non-numeric prices."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "100",
            "buy_price": "invalid",
            "sell_price": "also_invalid"
        }]
        with self.assertRaises(ValueError):
            self.test_csv_core1.validate_csv_data()

    def test_validate_csv_data_missing_optional_fields(self):
        """Test validation succeeds with missing optional fields (using default values)."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "100"
            # buy_price and sell_price are missing
        }]
        self.test_csv_core1.validate_csv_data()  # Should not raise exception

    def test_validate_csv_data_multiple_rows(self):
        """Test validation works across multiple rows of data."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "buy_price": "10.5",
                "sell_price": "11.0"
            },
            {
                "index": "2",
                "target_shares": "200",
                "buy_price": "20.5",
                "sell_price": "21.0"
            }
        ]
        self.test_csv_core1.validate_csv_data()  # Should not raise exception

    def test_validate_csv_data_invalid_middle_row(self):
        """Test validation fails when middle row contains invalid data."""
        self.test_csv_core1.required_columns = []
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "buy_price": "10.5",
                "sell_price": "11.0"
            },
            {
                "index": "2",
                "target_shares": "invalid",  # Invalid value in middle row
                "buy_price": "20.5",
                "sell_price": "21.0"
            },
            {
                "index": "3",
                "target_shares": "300",
                "buy_price": "30.5",
                "sell_price": "31.0"
            }
        ]
        with self.assertRaises(ValueError):
            self.test_csv_core1.validate_csv_data()
    
    # get_column_names
    def test_get_column_names_empty_data(self):
        """Test that empty data returns empty list of column names."""
        self.test_csv_core1.csv_data = []
        result = self.test_csv_core1._get_column_names()
        self.assertEqual(result, [])

    def test_get_column_names_single_row(self):
        """Test column names are extracted from single row data."""
        self.test_csv_core1.csv_data = [{
            "index": "1",
            "target_shares": "100",
            "buy_price": "10.5",
            "sell_price": "11.0"
        }]
        result = self.test_csv_core1._get_column_names()
        self.assertEqual(result, ["index", "target_shares", "buy_price", "sell_price"])

    def test_get_column_names_multiple_rows(self):
        """Test column names are extracted from first row only with multiple rows."""
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "buy_price": "10.5"
            },
            {
                "index": "2",
                "target_shares": "200",
                "buy_price": "20.5",
                "sell_price": "21.0"  # Extra column in second row should be ignored
            }
        ]
        result = self.test_csv_core1._get_column_names()
        self.assertEqual(result, ["index", "target_shares", "buy_price"])

    def test_get_column_names_empty_row(self):
        """Test with empty dictionary row returns empty list."""
        self.test_csv_core1.csv_data = [{}]
        result = self.test_csv_core1._get_column_names()
        self.assertEqual(result, [])

    # _save_csv_data
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    def test_save_csv_data_success(self, mock_csv_dictwriter, mock_open):
        # Mock the DictWriter and its writerows method
        mock_writer = mock_csv_dictwriter.return_value
        csv_data = [{"index": "1", "target_shares": "100"}]
        self.test_csv_core1._save_csv_data("test.csv", csv_data)
        mock_open.assert_called_once_with("test.csv", 'w', newline='')
        # Check that the DictWriter was created with the correct fieldnames
        mock_csv_dictwriter.assert_called_once_with(mock_open(), fieldnames=csv_data[0].keys())
        # Check that writerows was called with the correct data
        mock_writer.writeheader.assert_called_once()
        mock_writer.writerows.assert_called_once_with(csv_data)

    # _save_csv_data - file not found
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('builtins.print')
    def test_save_csv_data_file_not_found(self, mock_print, mock_open):
        # Mock the DictWriter and its writerows method
        csv_data = [{"index": "1", "target_shares": "100"}]
        self.test_csv_core1._save_csv_data("test.csv", csv_data)
        self.assertTrue(mock_print.called)
        mock_print.assert_called_once_with("Error saving CSV data: File not found")

    # save
    @patch('main.bots.SCALE_T.csv_utils.csv_core.CSVCore._save_csv_data')
    def test_save_success(self, mock_internal_save):
        # Mock the internal save method
        self.test_csv_core1._save_csv_data = mock_internal_save
        self.test_csv_core1.save()
        mock_internal_save.assert_called_once()
    
    # get_epoch time
    @patch('time.time')
    def test_get_epoch_time_success(self, mock_time):
        """Test that the epoch time is returned correctly."""
        mock_time.return_value = 1234567890
        result = self.test_csv_core1._get_epoch_time()
        self.assertEqual(result, 1234567890)

    # even_distribution
    @patch('main.bots.SCALE_T.csv_utils.csv_core.CSVCore._save_csv_data')
    def test_even_redistribution(self, mock_internal_save):
        """Test that even distribution is applied correctly."""
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "held_shares": "0",
                "buy_price": "10.5",
                "sell_price": "11.0"
            },
            {
                "index": "2",
                "target_shares": "200",
                "held_shares": "0",
                "buy_price": "20.5",
                "sell_price": "21.0"
            }
        ]
        success = self.test_csv_core1.even_redistribution(total_cash=1000)
        # Check that the internal save method was called
        mock_internal_save.assert_called_once()
        # Check that the csv_data was updated correctly
        # for 1000, 500 for each line. find the share count
        # line 0, 500/10.5 = 47.61904761904762
        # line 1, 500/20.5 = 24.390243902439025
        # Checking only the target_shares for simplicity
        self.assertTrue(success)
        self.assertAlmostEqual(float(self.test_csv_core1.csv_data[0]["target_shares"]), 47.61904761904762, places=6)
        self.assertAlmostEqual(float(self.test_csv_core1.csv_data[1]["target_shares"]), 24.390243902439025, places=6)
        # one case where cash amount is not evenly divisible
        # lets do 201
        success = self.test_csv_core1.even_redistribution(total_cash=201)
        # for 201, 100.5 for each line. find the share count
        # line 0, 100.5/10.5 = 9.523809523809524
        # line 1, 100.5/20.5 = 4.926829268292683
        self.assertTrue(success)
        self.assertAlmostEqual(float(self.test_csv_core1.csv_data[0]["target_shares"]), 9.523809523809524, places=6)
        self.assertAlmostEqual(float(self.test_csv_core1.csv_data[1]["target_shares"]), 4.926829268292683, places=6)

        # Check the return on False
        # Test with heldshares
        self.test_csv_core1.csv_data[0]["held_shares"] = "50"
        success = self.test_csv_core1.even_redistribution(total_cash=1000)
        self.assertFalse(success)

        # Test with empty data
        self.test_csv_core1.csv_data = []
        success = self.test_csv_core1.even_redistribution(total_cash=1000)
        self.assertFalse(success)



    # chase_price
    @patch('main.bots.SCALE_T.csv_utils.csv_core.CSVCore._load_csv_data')
    def test_chase_price(self, mock_load_csv_data):
        """Strategy is is to test, 1. new line insertion, 2. price gap shift on index 0"""
        self.test_csv_core1.csv_data = [
            {
                "index": "0",
                "target_shares": "100",
                "held_shares": "0",
                "buy_price": "10.5",
                "sell_price": "11.0"
            },
            {
                "index": "1",
                "target_shares": "200",
                "held_shares": "0",
                "buy_price": "10.0",
                "sell_price": "10.5"
            },
            {
                "index": "2",
                "target_shares": "300",
                "held_shares": "0",
                "buy_price": "9.5",
                "sell_price": "10.0"
            }
        ]
        self.test_csv_core1.chase_price({'current_price':12.0})
        # Check that the internal load method was called
        mock_load_csv_data.assert_not_called()
        # Check that the csv_data was updated correctly
        # Check that a new row is added with the correct values
        new_row = self.test_csv_core1.csv_data[0]
        self.assertEqual(new_row["index"], 0)
        self.assertEqual(new_row["buy_price"], 10.51)
        self.assertEqual(new_row["sell_price"], round(10.51*1.005,2))
        self.assertEqual(len(self.test_csv_core1.csv_data), 4)  # Check that a new row is added
        # Now lets check the shift of first index after another chase
        self.test_csv_core1.chase_price({'current_price': 12.0})
        # Check that the internal load method was called
        mock_load_csv_data.assert_not_called()
        # Check that the csv_data was updated correctly
        # Check that a new row is added with the correct values
        self.assertEqual(len(self.test_csv_core1.csv_data), 4)  # Check that a new row is added
        same_old_row = self.test_csv_core1.csv_data[0]
        self.assertEqual(same_old_row["buy_price"], 10.52)
        self.assertEqual(same_old_row["sell_price"], round(10.52*1.005,2))

    # get_total_cash_value
    def test_get_total_cash_value(self):
        """Test that the total cash value is returned correctly."""
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "buy_price": "10.5",
                "sell_price": "11.0"
            },
            {
                "index": "2",
                "target_shares": "200",
                "buy_price": "20.5",
                "sell_price": "21.0"
            }
        ]
        result = self.test_csv_core1.get_total_cash_value()
        expected_value = (100 * 10.5) + (200 * 20.5)
        self.assertEqual(result, expected_value)

    def test_get_total_cash_value_empty_data(self):
        """Test that total cash value is 0 when data is empty."""
        self.test_csv_core1.csv_data = []
        result = self.test_csv_core1.get_total_cash_value()
        self.assertEqual(result, 0)


    def test_is_chasable_lines(self):
        """Test that the number of chasable lines is returned correctly."""
        self.test_csv_core1.csv_data = [
            {
                "index": "1",
                "target_shares": "100",
                "held_shares": "0",
                "buy_price": "10.5",
                "sell_price": "11.0",
                "pending_order_id": "None",
            },
            {
                "index": "2",
                "target_shares": "200",
                "held_shares": "0",
                "buy_price": "20.5",
                "sell_price": "21.0",
                "pending_order_id": "None",
            }
        ]
        good_current_price = "10.51"
        result = self.test_csv_core1.is_chasable_lines(current_price=good_current_price)
        self.assertTrue(result, "Expected chasable lines to be True")

        bad_current_price = "9.9"
        result = self.test_csv_core1.is_chasable_lines(current_price=bad_current_price)
        self.assertFalse(result, "Current price isn't higher that index 0's buy price")

        # Test with pending order ID
        self.test_csv_core1.csv_data[0]["pending_order_id"] = "12345"
        result = self.test_csv_core1.is_chasable_lines(good_current_price)
        self.assertFalse(result, "Expected chasable lines to be False")
        # Test with held shares
        self.test_csv_core1.csv_data[0]["held_shares"] = "50"
        result = self.test_csv_core1.is_chasable_lines(good_current_price)
        self.assertFalse(result, "Expected chasable lines to be False")
        # Test with empty data
        self.test_csv_core1.csv_data = []
        result = self.test_csv_core1.is_chasable_lines(good_current_price)
        self.assertFalse(result, "Expected chasable lines to be False")
        

if __name__=="__main__":
    unittest.main()

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
    def test_load_csv_data_file_not_found(self):
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
    # get_column_names
    # _save_csv_data
    # save
    # get_epoch time

if __name__=="__main__":
    unittest.main()

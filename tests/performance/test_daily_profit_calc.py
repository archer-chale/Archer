import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import json

from main.performance.daily_profit_calc import DailyProfitManager

class TestDailyProfitManager(unittest.TestCase):

    def setUp(self):
        self.manager = DailyProfitManager()
        self.maxDiff = None

    def test_init(self):
        """
        Test the initialization of DailyProfitManager.
        """
        manager = DailyProfitManager()
        self.assertIsNotNone(manager)
        self.assertIsNone(manager.profit_content)
        self.assertIsNone(manager.current_day)
        self.assertIsNone(manager.current_profit_path)

    @patch('main.performance.daily_profit_calc.dt')
    def test_get_complete_profit_path(self, mock_dt):
        """
        Test the complete path for the profit file.
        """
        manager = DailyProfitManager()
        mock_dt.now.return_value = datetime(2023, 10, 15, 12, 0, 0)
        path = manager.get_complete_profit_path()
        self.assertEqual('data/performance/profits/2023/10/2023-10-15_profit.json', path)

    @patch('builtins.open', new_callable=mock_open)
    def test_read_profit_file(self, mock_file):
        """
        Test reading the profit file.
        """
        manager = DailyProfitManager()
        manager.current_profit_path = 'data/performance/profits/2023/10/2023-10-15_profit.json'
        mock_file.return_value.read.return_value = '{"profit": 100}'
        manager.read_profit_file()
        mock_file.assert_called_once_with('data/performance/profits/2023/10/2023-10-15_profit.json', 'r')
        self.assertEqual(manager.profit_content, {"profit": 100})

    @patch('main.performance.daily_profit_calc.json')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_profit(self, mock_file, mock_json):
        """
        Test saving the profit file.
        """
        manager = DailyProfitManager()
        manager.current_profit_path = 'data/performance/profits/2023/10/2023-10-15_profit.json'
        manager.profit_content = {"profit": 100}
        manager.save_profit()
        mock_file.assert_called_once_with('data/performance/profits/2023/10/2023-10-15_profit.json', 'w')
        mock_json.dump.assert_called_once_with({"profit": 100}, mock_file())

    @patch('main.performance.daily_profit_calc.DailyProfitManager.save_profit')
    @patch('main.performance.daily_profit_calc.DailyProfitManager.read_profit_file')
    @patch('main.performance.daily_profit_calc.dt')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_handle_new_day(self, mock_makedirs, mock_exists, mock_dt, mock_read_profit_file, mock_save_profit):
        """
        Test handling a new day.
        """
        self.manager = DailyProfitManager()
        mock_dt.now.return_value = datetime(2023, 10, 15, 12, 0, 0)

        # First call, file does not exist
        mock_exists.return_value = False
        self.manager.handle_new_day()
        mock_makedirs.assert_called_once_with('data/performance/profits/2023/10', exist_ok=True)
        self.assertEqual(self.manager.current_profit_path, 'data/performance/profits/2023/10/2023-10-15_profit.json')
        self.assertEqual(self.manager.profit_content, {})
        self.assertEqual(self.manager.current_day, datetime(2023, 10, 15).date())

        # Second call, file exists
        mock_exists.return_value = True
        self.manager.profit_content = {"profit": 100}
        self.manager.handle_new_day()
        mock_read_profit_file.assert_called_once()
        self.assertEqual(self.manager.current_profit_path, 'data/performance/profits/2023/10/2023-10-15_profit.json')
        self.assertEqual(self.manager.current_day, datetime(2023, 10, 15).date())
        self.assertEqual(self.manager.profit_content, {"profit": 100})

    @patch('main.performance.daily_profit_calc.DailyProfitManager.handle_new_day')
    @patch('main.performance.daily_profit_calc.DailyProfitManager.save_profit')
    @patch('main.performance.daily_profit_calc.dt')
    def test_account_profit(self, mock_dt, mock_save_profit, mock_handle_new_day):
        """
        Test the account profit calculation.
        """
        today = datetime(2023, 10, 15, 12, 0, 0)
        todays_date = today.date()
        message = {
            "symbol": "AAPL",
            "total": 100,
            "unrealized": 100,
            "realized": 0,
            "converted": 0,
            "timestamp": today
        }
        # 1. If its a new day it should call handle_new_day
        # 1a. symbol doesn't exist
        mock_dt.now.return_value = today
        self.assertIsNone(self.manager.current_day)
        self.assertIsNone(self.manager.profit_content)
        self.manager.profit_content = {} # supposed to be done by handle_new_day
        self.manager.account_profit(message)
        # make sure the current_day is set
        self.manager.current_day = datetime(2023, 10, 15).date()
        mock_handle_new_day.assert_called_once()
        expected_profit = {
            "aggregate": {
                "total": 100,
                "unrealized": 100,
                "realized": 0,
                "converted": 0,
                "timestamp": datetime(2023, 10, 15, 12, 0, 0)
            },
            "AAPL": {
                "total": 100,
                "unrealized": 100,
                "realized": 0,
                "converted": 0,
                "timestamp": datetime(2023, 10, 15, 12, 0, 0)
            }
        }
        self.assertEqual(self.manager.profit_content, expected_profit)
        # 1b. symbol does exist
        message["total"] = 50
        message["unrealized"] = 0
        message["realized"] = 25
        message["converted"] = 25

        mock_handle_new_day.reset_mock()
        self.manager.account_profit(message)
        expected_profit["AAPL"]["total"] += 50
        expected_profit["AAPL"]["realized"] += 25
        expected_profit["AAPL"]["converted"] += 25
        expected_profit["aggregate"]["total"] += 50
        expected_profit["aggregate"]["realized"] += 25
        expected_profit["aggregate"]["converted"] += 25
        mock_handle_new_day.assert_not_called()
        self.assertEqual(self.manager.profit_content, expected_profit)

        # same day but symbol doesn't exist
        message["symbol"] = "GOOGL"
        message["total"] = 20
        message["unrealized"] = 20
        message["realized"] = 0
        message["converted"] = 0
        mock_handle_new_day.reset_mock()
        mock_save_profit.reset_mock()
        self.manager.account_profit(message)
        expected_profit["GOOGL"] = {
            "total": 20,
            "unrealized": 20,
            "realized": 0,
            "converted": 0,
            "timestamp": datetime(2023, 10, 15, 12, 0, 0)
        }
        expected_profit["aggregate"]["total"] += 20
        expected_profit["aggregate"]["unrealized"] += 20
        expected_profit["aggregate"]["timestamp"] = datetime(2023, 10, 15, 12, 0, 0)
        self.assertEqual(self.manager.profit_content, expected_profit)
        mock_save_profit.assert_called_once()
        mock_save_profit.reset_mock()
        
        # check new day from the previous day
        today = datetime(2023, 10, 16, 12, 0, 0)
        todays_date = today.date()
        mock_dt.now.return_value = today
        message["symbol"] = "AAPL"
        message["total"] = 10
        message["unrealized"] = 10
        message["realized"] = 0
        message["converted"] = 0
        message["timestamp"] = today
        # reset mocks we check
        mock_handle_new_day.reset_mock()
        mock_save_profit.reset_mock()
        self.manager.profit_content = {} # By product of handle_new_day
        self.manager.account_profit(message)
        expected_profit = {
            "aggregate": {
                "total": 10,
                "unrealized": 10,
                "realized": 0,
                "converted": 0,
                "timestamp": today
            },
            "AAPL": {
                "total": 10,
                "unrealized": 10,
                "realized": 0,
                "converted": 0,
                "timestamp": today
            }
        }
        self.assertEqual(self.manager.profit_content, expected_profit)
        mock_handle_new_day.assert_called_once()
        mock_save_profit.assert_called_once()

if __name__ == '__main__':
    unittest.main()

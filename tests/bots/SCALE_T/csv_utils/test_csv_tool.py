import unittest
from unittest.mock import patch

from main.bots.SCALE_T.csv_utils.csv_tool import CSVWorker
from main.bots.SCALE_T.common.constants import TradingType

class TestCSVWorker(unittest.TestCase):
    # TODO Create a test for create csv

    # @patch('main.bots.SCALE_T.csv_utils.csv_tool.CSVWorker.even_redistribution')
    @patch('main.bots.SCALE_T.csv_utils.csv_tool.CSVCore.even_redistribution')
    def test_add_cash(self, mock_even_redistribution):
        new_cash = 1000
        csv_worker = CSVWorker("AAPL", TradingType.PAPER)
        csv_worker.csv_data = [
            {"buy_price": 100, "target_shares": 10},
            {"buy_price": 200, "target_shares": 5}
        ]
        csv_worker.add_cash_update(new_cash)
        total_cash = sum(row["buy_price"] * row["target_shares"] for row in csv_worker.csv_data)+ new_cash
        mock_even_redistribution.assert_called_once_with(total_cash)


if __name__ == '__main__':
    unittest.main()

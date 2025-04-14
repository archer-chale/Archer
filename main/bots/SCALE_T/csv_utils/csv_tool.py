"""
CSV Worker module for handling CSV processing tasks in the SCALE_T bot.

This module contains the CSVWorker class which provides functionality for
processing and manipulating CSV data according to the SCALE_T strategy.
"""

from typing import Dict, Optional, Union
from main.bots.SCALE_T.csv_utils.csv_core import CSVCore
from main.bots.SCALE_T.csv_utils.csv_tool_prompts import create_csv_questionaire, manipulate_csv_questionaire
from main.bots.SCALE_T.csv_utils.csv_tool_helper import find_least_decimal_digit_for_shares

# Usable by Nanny, Usable by csv_tool loop below
class CSVWorker(CSVCore):
    def __init__(self, ticker: str, trading_type: str, custom_id: Optional[str] = None):
        super().__init__(ticker, trading_type, custom_id)
        # Try to load csv, capturing success or failure through data or something
        # Think through the return types and how useful it works downstream


    def create_csv(self, answers: Dict[str, Union[str, float, int]]):
        # We need to create the DictReader object and save it to the csv file
        # Get the keys from required_columns
        keys = self.required_columns

        risk_type = answers["risk_type"]
        percentage_diff = answers["percentage_diff"]
        assert percentage_diff < 1, "Percentage difference must be less than 1"
        starting_buy_price = answers["starting_buy_price"]
        distribution_style = answers["distribution_style"] # will be needed when we do uneven distributions

        # decide base number of lines based on risk type
        num_lines = risk_type*100

        current_sell_price = round(starting_buy_price * (1 + (percentage_diff)), 2)
        dollar_per_line = answers["total_cash"] / num_lines
        print(f"dollar per line is {dollar_per_line}")
        extra_dollars = 0
        # Create the line by line creation loop for the list of dicts
        for i in range(num_lines):
            row = {}
            row["index"] = i
            buy_price = round(current_sell_price * (1 - percentage_diff), 2)
            row["buy_price"] = buy_price
            row["sell_price"] = current_sell_price
            least_decimal_place_shares = find_least_decimal_digit_for_shares(buy_price)
            # take dollar per line/ devide by buy price that gives u shares per line. To ensure the share
            # count is above $2 in value, we cut the digits at the least allowed decimal place
            # How do we cut the digits?
            # take the least decimal place shares from function. For 100 buy price, least decimal place share is
            # .1 . only variable is dollar_per line. lets say we got 10 per line. 10/100 = .1
            # We need to set number to 0 or remove extra digits
            # we do that by cases
            # 1. if number is less than least digits. set to 0
            # 2. cut digits down to same as least_decimal digits
            # 3. save extras as dollar amount and set target shares
            available_dollars_for_line = dollar_per_line + extra_dollars
            intended_target_shares = available_dollars_for_line/buy_price
            if intended_target_shares < least_decimal_place_shares:
                row["target_shares"] = 0
                extra_dollars = intended_target_shares * buy_price
            else :
                # By cut down what i mean is 
                # if ldd is .01 we want to only have multiples of this number
                multiples_ldd = int(intended_target_shares/least_decimal_place_shares)*least_decimal_place_shares
                row["target_shares"] = multiples_ldd
                # Save the extra money
                extra_dollars = buy_price*(intended_target_shares-multiples_ldd)

            row["held_shares"] = 0
            row["pending_order_id"] = "None"
            row["spc"] = "N"
            row["unrealized_profit"] = 0
            row["last_action"] = self._get_epoch_time()
            row["profit"] = 0
            
            self.csv_data.append(row)
            current_sell_price = buy_price


        # Save the list of dicts to the csv file
        self.save()


    def manipulate_csv(self):
        # Place holder
        pass


if __name__ == "__main__":
    # Example usage of the CSVWorker class
    import argparse
    from main.bots.SCALE_T.common.constants import get_ticker_filepath, PAPER_TRADING, LIVE_TRADING
    
    parser = argparse.ArgumentParser(description="CSV Worker for SCALE_T bot")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol (e.g., 'AAPL')")
    parser.add_argument("--trading-type", type=str, choices=[PAPER_TRADING, LIVE_TRADING], 
                        default=PAPER_TRADING, help="Trading type (paper or live)")
    parser.add_argument("--custom-id", type=str, help="Optional custom identifier for the CSV file")
    args = parser.parse_args()
    
    # Initialize and use CSVWorker
    worker = CSVWorker(args.ticker, args.trading_type, args.custom_id)
    
    # Validation error out failure
    try :
        worker._load_csv_data()
    except FileNotFoundError:
        print(f"File not found: {worker.csv_filepath}")
        answers = create_csv_questionaire()
        worker.create_csv(answers)
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        raise Exception(f"Error loading CSV data: {e}")

    # Manipulation eternal loop
    while True:
        answers = manipulate_csv_questionaire()
        worker.manipulate_csv(answers)
    

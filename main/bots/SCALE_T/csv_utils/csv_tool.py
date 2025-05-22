"""
CSV Worker module for handling CSV processing tasks in the SCALE_T bot.

This module contains the CSVWorker class which provides functionality for
processing and manipulating CSV data according to the SCALE_T strategy.
"""

from typing import Dict, Optional, Union
from main.bots.SCALE_T.common.constants import TradingType
from main.bots.SCALE_T.csv_utils.csv_core import CSVCore
from main.bots.SCALE_T.csv_utils.csv_tool_helper import find_least_decimal_digit_for_shares, clip_decimal_place_shares
from main.bots.SCALE_T.csv_utils.csv_tool_prompts import (
    create_csv_questionaire, get_information_on_csv_questionaire, update_csv_questionaire
)

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
        num_lines = int(risk_type*100)

        current_sell_price = round(starting_buy_price * (1 + (percentage_diff)), 2)
        dollar_per_line = answers["total_cash"] / num_lines
        print(f"dollar per line is {dollar_per_line}")
        extra_dollars = 0
        last_row = None
        # Create the line by line creation loop for the list of dicts
        for i in range(num_lines):
            row = {}
            row["index"] = i
            buy_price = round(current_sell_price * (1 - percentage_diff), 2)
            row["buy_price"] = buy_price
            row["sell_price"] = current_sell_price
            # Calculate the number of shares to buy
            # Split extra dollars across lines left
            lines_left = num_lines - i
            # Calculate extra for this line
            extra_for_this_line = extra_dollars / lines_left
            extra_dollars -= extra_for_this_line
            dollar_for_this_line = dollar_per_line + extra_for_this_line
            # Calculate the intended shares
            intended_shares = dollar_for_this_line / buy_price
            # Get the clipped extra shares
            extra_shares = clip_decimal_place_shares(buy_price, intended_shares)
            # take out the extra shares
            intended_shares -= extra_shares
            #Put the extra shares back into the extra dollars
            extra_dollars += extra_shares * buy_price
            # set the target shares
            row["target_shares"] = intended_shares
            row["held_shares"] = 0
            row["pending_order_id"] = "None"
            row["spc"] = "N"
            row["unrealized_profit"] = 0
            row["last_action"] = self._get_epoch_time()
            row["profit"] = 0
            
            last_row = row
            self.csv_data.append(row)
            current_sell_price = buy_price

        if extra_dollars:
            last_row["target_shares"] += extra_dollars/last_row['buy_price']
            last_row["spc"] = "last"

        # Save the list of dicts to the csv file
        self.save()

    def get_information(self):
        # Place holder
        pass

    def add_cash_update(self, additional_cash: float):
        # Add additional cash to the total cash in the CSV
        current_cash = self.get_total_cash_value()
        new_cash = current_cash + additional_cash

        # For now even distribution until config can bring in new distribution styles
        self.even_redistribution(new_cash)



if __name__ == "__main__":
    # Example usage of the CSVWorker class
    import argparse
    from main.bots.SCALE_T.common.constants import get_ticker_filepath
    
    parser = argparse.ArgumentParser(description="CSV Worker for SCALE_T bot")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol (e.g., 'AAPL')")
    parser.add_argument("--trading-type", type=TradingType, 
                        default=TradingType.PAPER, choices=[TradingType.LIVE, TradingType.PAPER], help="Trading type (paper or live)")
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
        print("What would you like to do")
        pick = int(input(f"1. For Information.  2. For Updating: "))
        if pick == 1:
            # Get information on the csv
            answers = get_information_on_csv_questionaire()
            worker.get_information(answers)
        elif pick == 2:
            # Update the csv
            print("=== CSV Update ===")
            answers = update_csv_questionaire()
            if answers["update_type"] == 1:
                # Chase price
                # After implementing the chase price we can ask worker to do so with answers
                if worker.is_chasable_lines(answers.get("current_price", "None")):
                    print("Based on current conditions,csv is chasable, chasing now")
                    worker.chase_price(answers)
                else:
                    print("CSV is not chasable")
            else:
                print("No other options yet")

# Would like to setup this tooling to look like a database. Instead of CRUD ops
# Would be nice to have Create, Information, Update

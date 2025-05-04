from datetime import datetime as dt
import os
import json
import logging


# Define base path for the profit file
profit_base_path = 'data/performance/profits/'

"""This module is responsible for managing daily profit calculations.

It'll look like this:
{
   "aggregate":{
        "total": 0,
        "unrealized": 0,
        "converted": 0,
        "realized": 0
    },
    "SOXL":{
        "total": 0,
        "unrealized": 0,
        "converted": 0,
        "realized": 0
    },
    "TSLA":{
        "total": 0,
        "unrealized": 0,
        "converted": 0,
        "realized": 0
    },
    "AAPL":{
        "total": 0,
        "unrealized": 0,
        "converted": 0,
        "realized": 0
    }
}
"""



class DailyProfitManager:
    """
    Class to manage daily profit calculations.
    """
    def __init__(self):
        self.profit_content = None
        self.current_day = None
        self.current_profit_path = None

    def get_complete_profit_path(self):
        """
        Get the complete path for the profit file.
        """
        current_date_utc = dt.now(dt.timezone.utc)
        # Convert date to string format
        date_str = current_date_utc.strftime('%Y-%m-%d')
        year = current_date_utc.strftime('%Y')
        month = current_date_utc.strftime('%m')
        path = os.path.join(profit_base_path, year, month, date_str + '_profit.json')
        return path
    
    def handle_new_day(self):
        # Check if current day has a file.
        current_date_utc = dt.now(dt.timezone.utc).date()
        # setup the day file if it doesn't exist, if it does, load the content
        self.current_profit_path = self.get_complete_profit_path()
        if not os.path.exists(self.current_profit_path):
            # If the file doesn't exist, create it
            os.makedirs(os.path.dirname(self.current_profit_path), exist_ok=True)
            self.profit_content = {}
            self.save_profit()
        else:
            # Load the existing content
            self.read_profit_file()
        self.current_day = current_date_utc

    def account_profit(self, message):
        """
        Calculate the profit for a given account message.
        """
        # Get todays date
        current_date_utc = dt.now(dt.timezone.utc).date()
        # Check if the current date is different from the last processed date
        if self.current_day != current_date_utc:
            # If so, handle the new day
            self.handle_new_day()

        # Extract the relevant information from the message
        symbol = message.get("symbol")
        total = message.get("total")
        unrealized = message.get("unrealized")
        realized = message.get("realized")
        converted = message.get("converted")
        timestamp = message.get("timestamp")
        # Add the separate sections to the profit content
        if symbol not in self.profit_content:
            self.profit_content[symbol] = {
                "total": total,
                "unrealized": unrealized,
                "realized": realized,
                "converted": converted,
                "timestamp": timestamp
            }
        else:
            # Update the existing entry
            self.profit_content[symbol]["total"] += total
            self.profit_content[symbol]["unrealized"] += unrealized
            self.profit_content[symbol]["realized"] += realized
            self.profit_content[symbol]["converted"] += converted
            self.profit_content[symbol]["timestamp"] = timestamp
        
        aggregate = self.profit_content.get("aggregate", {})
        # Add the aggregate section to the profit content
        aggregate['total'] = aggregate.get("total", 0) + total
        aggregate['unrealized'] = aggregate.get("unrealized", 0) + unrealized
        aggregate['realized'] = aggregate.get("realized", 0) + realized
        aggregate['converted'] = aggregate.get("converted", 0) + converted
        aggregate['timestamp'] = timestamp
        # Update the profit content with the aggregate
        self.profit_content["aggregate"] = aggregate
        # Save the updated profit content
        self.save_profit()

    def read_profit_file(self):
        """
        Read the profit file for today's content.
        """
        # Check if the profit_content is already loaded
        if self.profit_content is None:
            # Load the profit file (assuming it's a CSV for this example)
            try:
                with open(self.current_profit_path, 'r') as file:
                    self.profit_content = json.load(file)
            except FileNotFoundError:
                print("Profit file not found.")
                self.profit_content = None

    def save_profit(self):
        with open(self.current_profit_path, 'w') as f:
            json.dump(self.profit_content, f)


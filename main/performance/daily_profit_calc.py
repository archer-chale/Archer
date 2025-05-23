from datetime import datetime as dt, timezone
import os
import json
import logging

from main.utils.redis import RedisPublisher, CHANNELS


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
    def __init__(self, redis_host='redis', redis_port=6379, redis_db=0):
        self.profit_content = None
        self.current_day = None
        self.current_profit_path = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis publisher
        try:
            self.publisher = RedisPublisher(host=redis_host, port=redis_port, db=redis_db)
            self.logger.info("Redis publisher initialized")
        except Exception as e:
            self.logger.error(f"Error initializing Redis publisher: {e}")
            self.publisher = None

    def get_complete_profit_path(self):
        """
        Get the complete path for the profit file.
        """
        current_date_utc = dt.now(timezone.utc)
        # Convert date to string format
        date_str = current_date_utc.strftime('%Y-%m-%d')
        year = current_date_utc.strftime('%Y')
        month = current_date_utc.strftime('%m')
        path = os.path.join(profit_base_path, year, month, date_str + '_profit.json')
        return path
    
    def handle_new_day(self):
        # Check if current day has a file.
        current_date_utc = dt.now(timezone.utc).date()
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
        self.logger.info(f"Processing profit message: {message}")
        # Get todays date
        current_date_utc = dt.now(timezone.utc).date()
        # Check if the current date is different from the last processed date
        if self.current_day != current_date_utc:
            # If so, handle the new day
            self.handle_new_day()

        # Extract the relevant information from the message
        data = message.get("data")
        symbol = data.get("symbol")
        total = data.get("total")
        unrealized = data.get("unrealized")
        realized = data.get("realized")
        converted = data.get("converted")
        timestamp = data.get("timestamp")
        # Add the separate sections to the profit content
        if symbol not in self.profit_content:
            self.profit_content[symbol] = {
                "total": round(total, 2),
                "unrealized": round(unrealized, 2),
                "realized": round(realized, 2),
                "converted": round(converted, 2),
                "timestamp": timestamp
            }
        else:
            # Update the existing entry
            self.profit_content[symbol]["total"] = round(self.profit_content[symbol]["total"] + total, 2)
            self.profit_content[symbol]["unrealized"] = round(self.profit_content[symbol]["unrealized"] + unrealized, 2)
            self.profit_content[symbol]["realized"] = round(self.profit_content[symbol]["realized"] + realized, 2)
            self.profit_content[symbol]["converted"] = round(self.profit_content[symbol]["converted"] + converted, 2)
            self.profit_content[symbol]["timestamp"] = timestamp
        
        aggregate = self.profit_content.get("aggregate", {})
        # Add the aggregate section to the profit content
        aggregate['total'] = round(aggregate.get("total", 0) + total, 2)
        aggregate['unrealized'] = round(aggregate.get("unrealized", 0) + unrealized, 2)
        aggregate['realized'] = round(aggregate.get("realized", 0) + realized, 2)
        aggregate['converted'] = round(aggregate.get("converted", 0) + converted, 2)
        aggregate['timestamp'] = timestamp
        # Update the profit content with the aggregate
        self.profit_content["aggregate"] = aggregate
        # Save the updated profit content
        self.save_profit()
        
        # Publish performance data to Redis
        self.publish_performance_data(symbol, self.profit_content[symbol])
        
        # Also publish aggregate as its own symbol
        self.publish_performance_data('aggregate', self.profit_content['aggregate'])

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
    
    def publish_performance_data(self, symbol, performance_data):
        """
        Publish performance data to Redis for a specific symbol.
        
        Args:
            symbol: The ticker symbol
            performance_data: Dictionary with performance metrics
        """
        if not self.publisher:
            self.logger.error(f"Cannot publish performance data for {symbol}: Redis publisher not initialized")
            return
            
        try:
            channel = CHANNELS.get_ticker_performance_channel(symbol)
            
            # Ensure timestamp is included
            if 'timestamp' not in performance_data:
                performance_data['timestamp'] = dt.now(timezone.utc).isoformat()
                
            # Add symbol to data
            performance_data_copy = performance_data.copy()  # Create a copy to avoid modifying the original
            performance_data_copy['symbol'] = symbol
                
            # Publish to Redis
            self.publisher.publish(
                channel=channel,
                message_data=performance_data_copy,
                sender='performance_calculator'
            )
            self.logger.info(f"Published performance data for {symbol} to Redis")
            
        except Exception as e:
            self.logger.error(f"Error publishing performance data for {symbol}: {e}")


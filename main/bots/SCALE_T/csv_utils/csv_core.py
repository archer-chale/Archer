from typing import Optional
from ..common.constants import get_ticker_filepath
from typing import List, Dict, Union
import csv, os, json, time

from ..common.constants import (
    METADATA_FILE,
    TradingType
)
from ..csv_utils.csv_tool_helper import clip_decimal_place_shares

class CSVCore:
    """
    Base class for CSV operations in the SCALE_T bot.
    This class provides core functionality that can be extended by specific CSV handlers.
    """
    
    def __init__(self, ticker: str, trading_type: TradingType, custom_id: Optional[str] = None):
        self.ticker = ticker.upper()
        self.trading_type = trading_type
        self.custom_id = custom_id
        self.csv_filepath = get_ticker_filepath(self.ticker, self.trading_type, self.custom_id)
        self.metadata = self._load_metadata()
        self.required_columns = self._get_required_columns()
        self.csv_data = [] # Initialize to empty on start

    def _load_csv_data(self) -> List[Dict[str, Union[str, float, int]]]:
        """
        Load CSV data from the given filepath. (PEP 8 naming for internal method)

        Args:
            filepath (str): The path to the CSV file.

        Returns:
            List[Dict[str, Union[str, float, int]]]: A list of dictionaries representing the CSV data.
        """
        try:
            with open(self.csv_filepath, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                self.csv_data = data
            self.validate_csv_data()
        except FileNotFoundError:
            print(f"File not found: {self.csv_filepath}")
            raise FileNotFoundError(f"File not found: {self.csv_filepath}")
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            raise Exception(f"Error loading CSV data: {e}")

    def _load_metadata(self):
        """Loads the metadata JSON file."""
        metadata_path = os.path.join('data', 'SCALE_T', 'templates', METADATA_FILE)
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Metadata file not found: {metadata_path}")
            return {}  # Return an empty dictionary if file not found
        except Exception as e:
            print(f"Unknown exception, something might be wrong with metadata: {e}")
            return {}
        
    def _get_required_columns(self):
        """Extracts and returns a list of required column names from the metadata.
        
        Returns:
            list[str]: List of required column names. Returns empty list if:
                - Metadata is empty or invalid
                - No versions found
                - No columns defined
                - No required columns found
        """
        required_columns = []
        if self.metadata and 'versions' in self.metadata and self.metadata['versions']:
            # Assuming we use the first version in the list
            columns = self.metadata['versions'][0].get('columns', [])
            for column in columns:
                # Check if config exists and has required=True
                config = column.get('config', {})
                if config.get('required', False) and 'name' in column:
                    required_columns.append(column['name'])
        return required_columns

    def validate_csv_data(self) -> bool:
        """
        Validate the CSV data to ensure it has the correct structure. (Public method)

        Returns:
            throw Exception on validation failure
        """
        column_names = self._get_column_names()
        if not column_names:
            return # Consider empty data as valid

        # 1. Check for required columns
        for required_col in self.required_columns: # Use self.required_columns
            if required_col not in column_names:
                raise ValueError(f"Validation failed: Missing required column: {required_col}") # Debugging

        # 2. Basic data type checks
        for row in self.csv_data:
            int(row.get('index', 0))  # Check if index is integer-like
            float(row.get('target_shares', 0)) # Check if target_shares is numeric
            float(row.get('buy_price', 0)) # Check if buy_price is float-like
            float(row.get('sell_price', 0)) # Check if sell_price is float-like

    def _get_column_names(self) -> List[str]:
        """
        Get the column names from the CSV file. (Public method)

        Returns:
            List[str]: A list of column names.
        """
        if not self.csv_data:
            return []  # Return empty list if no data loaded
        return list(self.csv_data[0].keys()) # Get keys from the first row

    def _save_csv_data(self, filepath: str, data: List[Dict[str, Union[str, float, int]]]) -> None:
        """
        Save CSV data to the given filepath. (Internal method - PEP 8 naming)

        Args:
            filepath (str): The path to the CSV file.
            data (List[Dict[str, Union[str, float, int]]]): The CSV data to save.
        """
        try:
            with open(filepath, 'w', newline='') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        except Exception as e:
            print(f"Error saving CSV data: {e}")

    def save(self) -> None:
        """
        Save the CSV data to file. (Public method)

        This method is used to save the current CSV data to the file.
        It calls the internal _save_csv_data method to perform the actual saving.
        """
        self._save_csv_data(self.csv_filepath, self.csv_data)

    # Total cash value of all lines
    def get_total_cash_value(self) -> float:
        """
        Get the total cash value of all lines in the CSV data. (Public method)

        Returns:
            float: The total cash value.
        """
        total_value = 0
        for row in self.csv_data:
            total_value += float(row.get('target_shares', 0)) * float(row.get('buy_price', 0))
        return total_value

    def chase_price(self, context: Dict[str, Union[str, float, int]]):
        """
        Before this function is called, a check for
        1. No held shared in csv should be done
        2. No pending orders in csv
        """
        # Get the current price from the context
        current_price = context["current_price"]
        # Make sure lines are loaded
        if not self.csv_data:
            self._load_csv_data()

        # Do the appropriate checks to see if price is chasable
        # Chasable in the sense that current price is more than .01 of buy_price at index 0
        if not float(self.csv_data[0]["buy_price"])+0.01 < current_price:
            # Handle unchasable lines
            print(f'Current price {current_price} is not greater than buy price {self.csv_data[0]["buy_price"]} + 0.01')
            print(f"Not chasing price, current price {current_price} is not greater than buy price {self.csv_data[0]['buy_price']}")
            return
        # Proceed with chasable lines        
        # Because of the sliding lock of the top line we need to compare with second line to ensure lock limit
        # ex. line 1 [ 105, 205 ]  line 2 [ 100, 200 ]
        # another illustration of example above
        # line 1 [ ......105..............................205 ]  
        # line 2 [ 100..........................200.......... ]
        # We still keep the check for the first line having a difference of .5% between buy and sell price
        first_line = self.csv_data[0]
        second_line = self.csv_data[1]
        buy_price = float(first_line["buy_price"])
        sell_price = float(first_line["sell_price"])
        # Check that the difference is close to .5%
        precentage_diff = abs((sell_price - buy_price) / buy_price)
        if precentage_diff < 0.004: # Keep it at .4% for now as its close to .5%
            print(f"Unexpected price difference {precentage_diff}, not chasing")
            return
        
        # Get total cash value from all lines combined
        total_cash_value = self.get_total_cash_value()
        new_buy_price = round(float(first_line["buy_price"]) + 0.01, 2)
        new_sell_price = round(new_buy_price * (1 + 0.005), 2)
        # Check that the second line and first line are locked at buy and sell price
        if abs((float(second_line["sell_price"]) - float(first_line["buy_price"])) != 0):
            print(f"First line and second line are not locked, shifting first line up")
            # shift row 1 buy price up by .01 cents and sell price be .5% of buy price
            # new_buy_price = round(float(first_line["buy_price"]) + 0.01, 2)
            first_line["buy_price"] = new_buy_price
            first_line["sell_price"] = new_sell_price
        else :
            print(f"First line and second line are locked inserting new line")
            # We need a new line at the top that copies the first line and shifts the diff
            new_line = {
                "index": 0,
                "buy_price": new_buy_price,
                "sell_price": new_sell_price,
                "target_shares": 0,
                "held_shares": 0,
                "pending_order_id": "None",
                "spc": "N",
                "unrealized_profit": 0,
                "last_action": self._get_epoch_time(),
                "profit": 0
            }
            # Shift all other lines up an index by 1
            for i in range(len(self.csv_data)):
                # Shift the index of the line
                self.csv_data[i]["index"] = i + 1
            # Set the new line at index 0, need to not loose the first line
            self.csv_data.insert(0, new_line)
        
        # need to rebalance cash value of all lines
        print(f"Rebalancing cash value of all lines")
        self.even_redistribution(total_cash_value)

    def even_redistribution(self, total_cash: float) -> None:
        """
        Distribute cash evenly across all lines.
        Args:
            total_cash (float): The total cash to distribute.
        """
        # Warning about shares being held
        for row in self.csv_data:
            if float(row["held_shares"]) > 0:
                print(f"Warning: {row['held_shares']} shares are held, not redistributing cash.")
                return False

        # Get the number of lines
        num_lines = len(self.csv_data)
        if num_lines == 0:
            print("No lines to redistribute cash to.")
            return False
        
        # Calculate the cash per line
        cash_per_line = total_cash / num_lines
        extra_dollars = 0
        # Distribute the cash
        for row in self.csv_data:
            # Get the current buy price
            buy_price = float(row["buy_price"])
            # Calculate the number of shares to buy
            intended_shares = (cash_per_line + extra_dollars) / buy_price
            # Get the clipped extra shares
            extra_shares = clip_decimal_place_shares(buy_price, intended_shares)
            # take out the extra shares
            intended_shares -= extra_shares
            #Put the extra shares back into the extra dollars
            extra_dollars = extra_shares * buy_price
            # set the target shares
            row["target_shares"] = intended_shares

        # If there are any extra dollars left, add them to the last line
        if extra_dollars:
            last_row = self.csv_data[-1]
            last_row["target_shares"] += extra_dollars / float(last_row["buy_price"])
            last_row["spc"] = "last"
        # Save the updated CSV data
        self._save_csv_data(self.csv_filepath, self.csv_data)
        return True
        
    def is_chasable_lines(self, current_price=None):
        """
        Check if the lines are chasable.
        This function checks if the lines are chasable based on the state of csv_price.
        empty lines are not chasable. and shares on index 0 are not chasable.
        If the lines are chasable, it will return True, otherwise False.
        """
        # Check if the lines are empty
        if not self.csv_data or not current_price:
            return False
        # Check if the first line has shares
        if float(self.csv_data[0]["held_shares"]) > 0:
            return False
        # Check if current_price is not greater than index 0's buy_price
        if float(self.csv_data[0]["buy_price"]) >= float(current_price):
            return False

        # Check if there are any pending orders
        for row in self.csv_data:
            if row["pending_order_id"] != "None":
                return False
        return True        

    def _get_epoch_time(self):
        return int(time.time())

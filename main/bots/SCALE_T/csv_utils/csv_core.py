from typing import Optional
from ..common.constants import get_ticker_filepath
from typing import List, Dict, Union
import csv, os, json, time

from ..common.constants import (
    METADATA_FILE,
    TradingType
)

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

    def _get_epoch_time(self):
        return int(time.time())

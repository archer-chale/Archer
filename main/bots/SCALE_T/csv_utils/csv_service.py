"""
CSV Manager for SCALE_T bot.

This module provides functionality to manage CSV files containing trading data.
It handles reading, validation, and updating of CSV data using dictionary-based operations.
"""

import csv
import json
import os
import time
from typing import Dict, List, Optional, Union
from .csv_core import CSVCore

from main.bots.SCALE_T.common.constants import (
    METADATA_FILE
)

from main.bots.SCALE_T.common.logging_config import get_logger

class CSVService(CSVCore):
    """
    Manages CSV data for SCALE_T trading strategy.
    Handles reading, validation, and updating of CSV files containing trading data.
    Uses dictionary-based operations for data manipulation.
    """

    def __init__(self, ticker: str, trading_type: str, custom_id: Optional[str] = None):
        """
        Initialize CSVService with ticker and trading type.

        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
            trading_type (str): Either 'paper' or 'live' trading
            custom_id (Optional[str]): Optional custom identifier for the CSV file

        Raises:
            ValueError: If trading_type is invalid
        """
        super().__init__(ticker, trading_type, custom_id)
        self.logger = get_logger("csv_service")
        self.logger.info(f"Initializing CSVService for {self.ticker} ({self.trading_type}) with custom_id: {self.custom_id}")
        # Load metadata and get required columns
        self.metadata = self._load_metadata()
        self.required_columns = self._get_required_columns()
        self.csv_data = [] # Initialize to empty list
        self.csv_data = self._load_csv_data(self.csv_filepath)
        self.logger.info(f"CSVService initialized successfully.")

    def get_row_by_index(self, index: int) -> Optional[Dict[str, Union[str, float, int]]]:
        """
        Get a row from the CSV data by index. (Public method)

        Args:
            index (int): The index of the row to retrieve.

        Returns:
            Optional[Dict[str, Union[str, float, int]]]: The row data, or None if not found.
        """
        for row in self.csv_data:
            if str(row.get('index')) == str(index):
                return row
        return None

    def _get_total_row_count(self) -> int:
        """
        Get the total number of rows in the CSV data. (Public method)

        Returns:
            int: The total number of rows.
        """
        return len(self.csv_data)

    def get_current_held_shares(self):
        """
        Gets the number of shares currently held from the CSV data.
        """
        total_held_shares = 0
        for row in self.csv_data:
            total_held_shares += float(row.get('held_shares', 0))  # Default to 0 if not found or invalid
        return total_held_shares

    def get_pending_order_info(self):
        """
        Gets the pending order ID and its index from the CSV data.
        Iterates through all rows and returns the first non-empty pending_order_id found.
        """
        for index, row in enumerate(self.csv_data):
            if "pending_order_id" in row and row["pending_order_id"] != "None":
                return {"order_id": row["pending_order_id"], "index": index}
        return None

    def get_rows_for_buy(self, current_price):
        return [
            row
            for row in self.csv_data
            if float(row["buy_price"]) >= current_price and float(row["held_shares"]) < float(row["target_shares"])
        ]

    def get_rows_for_sell(self, current_price):
        return [
            row
            for row in self.csv_data
            if float(row["sell_price"]) <= current_price and float(row["held_shares"]) > 0
        ]

    # Instead of distributing shares bottom up for buys and top down for sells, do the opposite
    def update_order_status(self, index, filled_qty, filled_avg_price, side):
        """Updates the CSV data when an order is filled or cancelled with a filled quantity > 0.
        Handles buy and sell orders differently, distributing shares appropriately.
        """
        row = self.get_row_by_index(index)
        if not row:
            raise ValueError(f"Row with index {index} not found in update_order_status.")
            
        time_now = self._get_epoch_time()

        if side == 'buy' and filled_qty > 0:
            self.logger.debug(f"Distributing {filled_qty} shares to rows above {index}")
            while filled_qty > 0:
                for i in range(0, index+1):
                    current_row = self.get_row_by_index(i)
                    if current_row:
                        assignable = min(filled_qty, float(current_row['target_shares']) - float(current_row['held_shares']))
                        if assignable > 0:
                            self.logger.debug(f"Assigning {assignable} shares to index {i}, filled_qty: {filled_qty}")
                            prev_held_shares = float(current_row['held_shares'])
                            current_row['held_shares'] = prev_held_shares + assignable
                            filled_qty -= assignable
                            self.logger.debug(f"After assignment, filled_qty: {filled_qty}")
                            #update unrealized profit
                            if prev_held_shares > 0:
                                existing_unrealized = float(current_row.get('unrealized_profit', 0))
                            else:
                                existing_unrealized = 0.0
                            self.logger.debug(f"Before unrealized profit update, existing: {existing_unrealized}")
                            #Add unrealized profit for the new shares
                            new_unrealized = (float(current_row['buy_price']) - float(filled_avg_price)) * assignable
                            current_row['unrealized_profit'] = round(existing_unrealized + new_unrealized, 2)
                            self.logger.debug(f"After unrealized profit update, new: {current_row['unrealized_profit']}")
                            current_row['last_action'] = time_now
                    if filled_qty == 0:
                        break

        elif side == 'sell' and filled_qty > 0:
            while filled_qty > 0:
                for i in range(self._get_total_row_count()-1, index-1, -1):
                    current_row = self.get_row_by_index(i)
                    if current_row:
                        sellable = min(filled_qty, float(current_row['held_shares']))
                        if sellable > 0:
                            self.logger.debug(f"Selling {sellable} shares from index {i}, filled_qty: {filled_qty}")
                            prev_held_shares = float(current_row['held_shares'])
                            current_row['held_shares'] = prev_held_shares - sellable
                            filled_qty -= sellable
                            prev_unrealised_profit = float(current_row.get('unrealized_profit', 0))
                            current_row['unrealized_profit'] = 0.0
                            sale_profit = (float(filled_avg_price) - float(current_row['buy_price'])) * sellable
                            previous_profit = float(current_row.get('profit'))
                            self.logger.debug(f"Before profit update, existing unrealized: {prev_unrealised_profit}, sale_profit: {sale_profit}, previous_profit: {previous_profit}")
                            current_row['profit'] = round(prev_unrealised_profit + sale_profit+previous_profit,2)
                            self.logger.debug(f"After sale, profit: {current_row['profit']}")
                            current_row['last_action'] = time_now
                    if filled_qty  == 0:
                        self.logger.debug(f"Filled quantity reached 0. Selling complete.")
                        break  
          
        row['pending_order_id'] = "None"
        row['last_action'] = time_now

        self.save()

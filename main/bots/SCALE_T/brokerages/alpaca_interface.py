"""
Alpaca brokerage interface for SCALE_T bot.

This module provides an interface (AlpacaInterface class) for interacting with the Alpaca brokerage API using the alpaca-py SDK.
It encapsulates brokerage functionalities and provides a singleton trading client for efficient reuse.
"""

import os, sys
from typing import Tuple, List, Dict, Any, Optional, Callable, Awaitable, Union
import asyncio
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import AssetStatus, OrderStatus, OrderSide, OrderType, TimeInForce
from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.data.models import Trade, Quote, Bar
from alpaca.common.exceptions import APIError

from ..common.constants import (
    # PAPER_ALPACA_KEY_ID,
    # PAPER_ALPACA_SECRET_KEY,
    # LIVE_ALPACA_KEY_ID,
    # LIVE_ALPACA_SECRET_KEY,
    ENV_FILE,
    TradingType,
    TRADING_TYPE_TO_KEY_NAME
)
from ..common.logging_config import get_logger

# Load environment variables from .env file
load_dotenv(ENV_FILE)


class AlpacaInterface:
    """
    Provides an interface for interacting with the Alpaca brokerage API.

    Handles API key validation and trading functionalities using the alpaca-py SDK.
    Uses a singleton pattern for the trading client for efficiency.
    """

    def __init__(self, trading_type: str = "paper", ticker: str = None):
        self.logger = get_logger(self.__class__.__name__)
        self.trading_type = trading_type
        self.ticker = ticker
        self.api_key = None
        self.secret_key = None
        self.trading_client = None # Instance-level variable
        self.data_client = None
        self.logger.info("Initializing AlpacaInterface ")
        self.set_trading_client()


        is_valid, errors = self.validate_alpaca_keys()
        if not is_valid:
            self.logger.error(f"Alpaca key validation failed: {errors}. Exiting.")
            sys.exit(0)
        self.logger.info("Alpaca interface initialized successfully.")

    def set_trading_client(self) -> None:
        """
        Sets the Alpaca Trading client and api/secret keys.
        """

        KEY_ID_NAME = TRADING_TYPE_TO_KEY_NAME[self.trading_type]["KEY_ID_NAME"]
        SECRET_KEY_NAME = TRADING_TYPE_TO_KEY_NAME[self.trading_type]["SECRET_KEY_NAME"]
        self.api_key = os.environ.get(KEY_ID_NAME)
        self.secret_key = os.environ.get(SECRET_KEY_NAME)
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=(self.trading_type == TradingType.PAPER))
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)

    def validate_alpaca_keys(self) -> Tuple[bool, List[str]]:
        """
        Validates that Alpaca API keys exist and are valid.
        """
        errors = []
        self.logger.info("Validating Alpaca keys...")

        # If keys don't exist, return early
        if errors:
            return False, errors

        # Test API connection
        try:
            # Get account information
            account = self.trading_client.get_account()

            # Check if account is active
            if account.status != "ACTIVE":
                self.logger.error(f"Alpaca account is not active. Status: {account.status}")
                errors.append(f"Alpaca account is not active. Status: {account.status}")
                return False, errors

        except APIError as e:
            self.logger.error(f"API Error: {str(e)}")
            errors.append(f"API Error: {str(e)}")
            return False, errors
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            errors.append(f"Unexpected error: {str(e)}")
            return False, errors

        return True, []

    def get_shares_count(self) -> float:
        """
        Gets the number of shares held for the ticker.
        """
        positions = self.trading_client.get_all_positions()
        for position in positions:
            if position.symbol == self.ticker:
                return float(position.qty)
        return 0.0

    def get_buying_power(self):
        """Gets the current buying power."""
        return float(self.trading_client.get_account().buying_power)

    def get_current_price(self):
        self.logger.debug(f"Getting current price for {self.ticker}")
        trade = self.data_client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=self.ticker))
        return trade[self.ticker].price

    def get_order_by_id(self, order_id):
        """
        Gets an order by its ID.
        """
        return self.trading_client.get_order_by_id(order_id)

    def cancel_order(self, order_id: str) -> bool:
      """Cancels an order by ID.
      
      Returns:
          bool: True if cancellation was successful, False otherwise.
      """
      try:
        order = self.trading_client.get_order_by_id(order_id)
        
        if order.status is OrderStatus.FILLED:
            self.logger.info(f"Order {order_id} is already filled.")
            return False
        elif order.status is OrderStatus.CANCELED:
            self.logger.warning(f"Order {order_id} is already canceled. Should be picked up by order update.")
            return False
        
        if int(order.filled_qty) > 0:
            self.logger.warning(f"Order {order_id} has some shares filled.")

        self.trading_client.cancel_order_by_id(order_id)
        self.logger.info(f"Order {order_id} cancelled successfully.")
        return True
      except Exception as e:
        self.logger.error(f"Failed to cancel order {order_id}: {e}")
        return False

    def place_order(self, side, price, quantity):
      """Place a buy/sell order with simplified interface.
      
      Args:
          side (str or OrderSide): 'buy'/'sell' or OrderSide enum
          price (float): Limit price for the order
          quantity (float): Number of shares to buy/sell, can be fractional
          
      Returns:
          Object: Complete order object if successful, None otherwise
      """
      try:
          # Convert side to OrderSide enum if it's a string
          if isinstance(side, str):
              order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
          else:
              # Assume it's already an OrderSide enum
              order_side = side
          
          # Log order details
          side_str = "buy" if order_side == OrderSide.BUY else "sell"
          self.logger.info(f"Placing {side_str} order for {quantity} shares of {self.ticker} at ${price}")
          
          # Handle fractional orders with market orders
          if quantity % 1 > 0.0:
              self.logger.info(f"Fractional order detected: {quantity} shares. Using market order.")
              
              # For market orders, first check if the current price is favorable compared to limit price
              current_price = self.get_current_price()
              
              # For buy orders, ensure current price is less than limit price
              # For sell orders, ensure current price is greater than limit price
              price_is_favorable = (order_side == OrderSide.BUY and current_price < price) or \
                                  (order_side == OrderSide.SELL and current_price > price)
              
              if not price_is_favorable:
                  self.logger.warning(f"Current price ${current_price} is not favorable compared to expected order price ${price}. Order not placed.")
                  return None
                  
              # Create market order request for fractional shares
              order_data = MarketOrderRequest(
                  symbol=self.ticker,
                  side=order_side,
                  qty=quantity,
                  time_in_force=TimeInForce.DAY,
                  extended_hours=False  # Market orders can't be extended hours
              )
          else:
              # Create limit order request for whole shares
              order_data = LimitOrderRequest(
                  symbol=self.ticker,
                  limit_price=price,
                  side=order_side,
                  qty=quantity,
                  type=OrderType.LIMIT,
                  time_in_force=TimeInForce.DAY,
                  extended_hours=True
              )
          
          # Submit the order directly to trading client
          order = self.trading_client.submit_order(order_data=order_data)
          
          if order.status not in [OrderStatus.ACCEPTED, OrderStatus.NEW, OrderStatus.PENDING_NEW]:
              self.logger.warning(f"Order may not have been accepted properly. Status: {order.status}")
              self.logger.debug(f"Order details: {order}")
          
          return order
          
      except Exception as e:
          self.logger.error(f"An error occurred while placing the order: {e}")
          return None

if __name__ == "__main__":
    import sys

    print(f"Python executable used: {sys.executable}")

    # Define key sets and validation function calls
    key_sets = {
        "Paper": {
            "paper": True,
            "key_id": "PAPER_KEY_ID_PLACEHOLDER",
            "secret_key": "PAPER_SECRET_KEY_PLACEHOLDER",
        },
        "Live": {
            "paper": False,
            "key_id": "LIVE_KEY_ID_PLACEHOLDER",
            "secret_key": "LIVE_SECRET_KEY_PLACEHOLDER",
        },
    }

    for key_type, keys in key_sets.items():
        print(f"\nValidating {key_type} keys...")
        interface = AlpacaInterface()  # Initialize AlpacaInterface
        is_valid, errors = interface.validate_alpaca_keys()
        if is_valid:
            interface.logger.info(f"{key_type} Alpaca keys are valid.")
        else:
            interface.logger.error(f"{key_type} Alpaca keys are invalid. Errors: {errors}")

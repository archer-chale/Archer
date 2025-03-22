"""
Constants for the SCALE_T bot.

This module contains constants used throughout the SCALE_T bot implementation.
All file paths and directory structures are centralized here for easier maintenance.
"""

import os
from typing import Optional

# Brokerage types
ALPACA_BROKERAGE = "alpaca"

SUPPORTED_BROKERAGES = [ALPACA_BROKERAGE]

# Trading types
PAPER_TRADING = "paper"
LIVE_TRADING = "live"

# API Key names
PAPER_ALPACA_KEY_ID = "PAPER_ALPACA_API_KEY_ID"
PAPER_ALPACA_SECRET_KEY = "PAPER_ALPACA_API_SECRET_KEY"
LIVE_ALPACA_KEY_ID = "ALPACA_API_KEY_ID"
LIVE_ALPACA_SECRET_KEY = "ALPACA_API_SECRET_KEY"

PROJECT_NAME = "Archer"
# Determine the base path of your project
current_path = os.path.dirname(os.path.abspath(__file__))

# Traverse up to find "BasePath"
while not current_path.endswith(PROJECT_NAME):
    parent_path = os.path.dirname(current_path)
    if parent_path == current_path:  # If we reached the root directory
        raise Exception(f"{PROJECT_NAME} not found in directory structure.")
    current_path = parent_path

# Base directory paths
BASE_DIR = os.path.join(current_path, "data/SCALE_T")
CONFIG_DIR = os.path.join(current_path, "configs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TICKER_DATA_BASE = os.path.join(BASE_DIR, "ticker_data")

# ENV File Location
ENV_FILE = os.path.join(CONFIG_DIR, ".env")

# Trading mode paths
PAPER_TRADING_PATH = os.path.join(TICKER_DATA_BASE, PAPER_TRADING)
LIVE_TRADING_PATH = os.path.join(TICKER_DATA_BASE, LIVE_TRADING)

# Template files
TEMPLATE_CSV = os.path.join(TEMPLATES_DIR, "SCALE_T.csv")
METADATA_FILE = os.path.join(TEMPLATES_DIR, "csv_versions_metadata.json")

# File naming patterns
DEFAULT_CSV_PATTERN = "{ticker}.csv"  # Standard pattern
CUSTOM_ID_CSV_PATTERN = "{ticker}_{custom_id}.csv"  # Pattern with custom ID

def get_trading_path(trading_type: str) -> str:
    """
    Get the appropriate directory path based on trading type.
    
    Args:
        trading_type (str): Either PAPER_TRADING or LIVE_TRADING
        
    Returns:
        str: The directory path for the specified trading type
        
    Raises:
        ValueError: If an invalid trading type is provided
    """
    if trading_type == PAPER_TRADING:
        return PAPER_TRADING_PATH
    elif trading_type == LIVE_TRADING:
        return LIVE_TRADING_PATH
    else:
        raise ValueError(f"Invalid trading type: {trading_type}. Must be either '{PAPER_TRADING}' or '{LIVE_TRADING}'.")

def get_ticker_filename(ticker: str, custom_id: Optional[str] = None) -> str:
    """
    Generate a filename for a ticker, optionally with a custom ID.
    
    Args:
        ticker (str): The ticker symbol
        custom_id (Optional[str]): Custom identifier to append to the filename
        
    Returns:
        str: The generated filename
    """
    ticker = ticker.upper()
    if custom_id:
        return CUSTOM_ID_CSV_PATTERN.format(ticker=ticker, custom_id=custom_id)
    else:
        return DEFAULT_CSV_PATTERN.format(ticker=ticker)

def get_ticker_filepath(ticker: str, trading_type: str, custom_id: Optional[str] = None) -> str:
    """
    Get the full file path for a ticker's CSV file.
    
    Args:
        ticker (str): The ticker symbol
        trading_type (str): Either PAPER_TRADING or LIVE_TRADING
        custom_id (Optional[str]): Custom identifier to append to the filename
        
    Returns:
        str: The full file path
    """
    base_path = get_trading_path(trading_type)
    filename = get_ticker_filename(ticker, custom_id)
    return os.path.join(base_path, filename)

def parse_ticker_filename(filename: str) -> tuple:
    """
    Parse a ticker filename to extract ticker symbol and custom ID.
    
    Args:
        filename (str): The filename to parse (e.g., 'AAPL.csv' or 'AAPL_myID.csv')
        
    Returns:
        tuple: (ticker_symbol, custom_id) where custom_id may be None
    """
    # Remove .csv extension
    base_name = os.path.splitext(filename)[0]
    
    # Check if there's an underscore (indicating a custom ID)
    if '_' in base_name:
        parts = base_name.split('_', 1)  # Split on first underscore only
        return parts[0], parts[1]
    else:
        return base_name, None

"""
Constants for the SCALE_T bot.

This module contains constants used throughout the SCALE_T bot implementation.
All file paths and directory structures are centralized here for easier maintenance.
"""

import os
from typing import Optional
import pytz
from enum import Enum

NYC_TZ = pytz.timezone("America/New_York")  # Use NYC timezone for logging

# Brokerage types
ALPACA_BROKERAGE = "alpaca"

SUPPORTED_BROKERAGES = [ALPACA_BROKERAGE]

class TradingType(Enum):
    PAPER = "paper"
    LIVE = "live"

TRADING_TYPE_TO_KEY_NAME = {
    TradingType.PAPER : {
        "KEY_ID_NAME" : "PAPER_ALPACA_API_KEY_ID",
        "SECRET_KEY_NAME" : "PAPER_ALPACA_API_SECRET_KEY"
    },
    TradingType.LIVE : {
        "KEY_ID_NAME" : "ALPACA_API_KEY_ID",
        "SECRET_KEY_NAME" : "ALPACA_API_SECRET_KEY"
    }
}

def find_base_path(start_path: str, base_path_name: str) -> str:
    """
    Traverse up the directory tree to find the base path.
    
    Args:
        start_path (str): The starting directory path
        base_path_name (str): The name of the base path to look for
        
    Returns:
        str: The found base path or None if not found
    """
    current_path = start_path
    while not os.path.basename(current_path) == base_path_name:
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # If we reached the root directory
            return None
        current_path = parent_path
    return current_path

PROJECT_BASE_PATH = "Archer"
BOT_NAME = "SCALE_T"
DOCKER_BASE_PATH = "app"
# Determine the base path of your project
env =  "docker"
current_path = os.path.dirname(os.path.abspath(__file__))
ABS_BASE_PATH = find_base_path(current_path, DOCKER_BASE_PATH)
if ABS_BASE_PATH is None:
    # Possibly running from non-docker environment try project root
    current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ABS_BASE_PATH = find_base_path(current_path, PROJECT_BASE_PATH)
    env = "local"

# Base directory paths - Current path is now the base directory of Archer
if env == "docker":
    DATA_PATH = os.path.join(ABS_BASE_PATH, "data")
else:
    DATA_PATH = os.path.join(ABS_BASE_PATH, "data", "SCALE_T")
LOGS_DIR = os.path.join(DATA_PATH, "logs")
CONFIG_DIR = os.path.join(ABS_BASE_PATH, "configs")
TEMPLATES_DIR = os.path.join(DATA_PATH, "templates")
TICKER_DATA_BASE = os.path.join(DATA_PATH ,"ticker_data")


# ENV File Location
ENV_FILE = os.path.join(CONFIG_DIR, ".env")

# Trading mode paths
TRADING_TYPE_TO_PATH = {
    TradingType.PAPER :  os.path.join(TICKER_DATA_BASE, TradingType.PAPER.value),
    TradingType.LIVE : os.path.join(TICKER_DATA_BASE, TradingType.LIVE.value)
}

# Template files
TEMPLATE_CSV = os.path.join(TEMPLATES_DIR, "SCALE_T.csv")
METADATA_FILE = os.path.join(TEMPLATES_DIR, "csv_versions_metadata.json")

# File naming patterns
DEFAULT_CSV_PATTERN = "{ticker}.csv"  # Standard pattern
CUSTOM_ID_CSV_PATTERN = "{ticker}_{custom_id}.csv"  # Pattern with custom ID

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

def get_ticker_filepath(ticker: str, trading_type: TradingType, custom_id: Optional[str] = None) -> str:
    """
    Get the full file path for a ticker's CSV file.
    
    Args:
        ticker (str): The ticker symbol
        trading_type (TradingType): Either PAPER_TRADING or LIVE_TRADING
        custom_id (Optional[str]): Custom identifier to append to the filename
        
    Returns:
        str: The full file path
    """
    base_path = TRADING_TYPE_TO_PATH[trading_type]
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

# SCALE_T CSV Utilities

## Overview

The `csv_utils` module provides a comprehensive system for managing trading strategy data in CSV format for the SCALE_T trading bot. It handles reading, writing, validation, and manipulation of CSV files that define the trading parameters and state for each stock ticker.

## Architecture

The module follows a layered architecture:

1. **Core Layer** (`csv_core.py`): Base functionality for CSV operations
2. **Service Layer** (`csv_service.py`): Trading-specific CSV operations
3. **Tool Layer** (`csv_tool.py`): Interactive utilities for CSV creation and management
4. **Helper Components**: Utility functions and interactive prompts

## Core Components

### `CSVCore` (csv_core.py)

Base class that provides fundamental CSV handling:

- File loading and saving operations
- CSV data validation against required columns
- Metadata management
- Path resolution using trading types (paper/live)

```python
from ..common.constants import TradingType
from csv_utils.csv_core import CSVCore

# Initialize core CSV handler
core = CSVCore("AAPL", TradingType.PAPER)
```

### `CSVService` (csv_service.py)

Extends `CSVCore` to provide trading-specific operations:

- Getting current held shares
- Retrieving row data by index
- Finding rows eligible for buy/sell orders
- Updating order status when trades are filled
- Profit/loss tracking for positions

```python
from ..common.constants import TradingType
from csv_utils.csv_service import CSVService

# Initialize CSV service
service = CSVService("AAPL", TradingType.PAPER)

# Get current position
shares = service.get_current_held_shares()
```

### `CSVWorker` (csv_tool.py)

Tool for creating and manipulating CSV files:

- Interactive CSV creation based on risk profile and trading parameters
- Distribution of funds across multiple price levels
- Command-line interface for CSV management

```python
from csv_utils.csv_tool import CSVWorker

# Create a new CSV with trading parameters
worker = CSVWorker("AAPL", "paper")
worker.create_csv({
    "total_cash": 10000,
    "risk_type": 3,
    "percentage_diff": 0.02,
    "starting_buy_price": 150.0,
    "distribution_style": "linear"
})
```

### Helper Components

- **`csv_tool_helper.py`**: Utility functions for CSV operations
  - `find_least_decimal_digit_for_shares()`: Determines appropriate share precision

- **`csv_tool_prompts.py`**: Interactive prompts for CSV creation and manipulation
  - `create_csv_questionaire()`: Gathers inputs for new CSV files
  - `manipulate_csv_questionaire()`: Interface for modifying existing CSVs

## CSV Data Structure

The CSV files managed by this module follow a specific structure:

| Column | Description |
|--------|-------------|
| index | Row identifier |
| buy_price | Target price for buying shares |
| sell_price | Target price for selling shares |
| target_shares | Number of shares to acquire at this price level |
| held_shares | Current number of shares held at this level |
| pending_order_id | ID of any pending order for this row |
| spc | Special flag for row behavior |
| unrealized_profit | Unrealized P/L for current position |
| last_action | Timestamp of last activity |
| profit | Realized profit from completed trades |

## Trading Strategy Logic

The CSV structure implements a grid/ladder trading strategy where:

1. Each row represents a price level with buy/sell targets
2. Buy orders are placed when the current price drops to buy_price
3. Sell orders are placed when the current price rises to sell_price
4. Shares are distributed across multiple price levels
5. Profit is tracked at each price level

## Working with CSV Files

### Creating a New CSV

```python
from main.bots.SCALE_T.csv_utils.csv_tool import CSVWorker
from main.bots.SCALE_T.common.constants import TradingType

# Create a new CSV for AAPL
worker = CSVWorker("AAPL", TradingType.PAPER)

# Parameters for grid strategy
params = {
    "total_cash": 10000,       # Total capital to allocate
    "risk_type": 3,            # Risk level (1-5)
    "percentage_diff": 0.02,   # % difference between buy/sell prices
    "starting_buy_price": 150, # Starting price for first level
    "distribution_style": "linear" # How to distribute capital
}

# Create the CSV with these parameters
worker.create_csv(params)
```

### Reading and Modifying CSV Data

```python
from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.common.constants import TradingType

# Open existing CSV
service = CSVService("AAPL", TradingType.PAPER)

# Get rows eligible for buying at current price
buy_rows = service.get_rows_for_buy(147.50)

# Update order status when filled
service.update_order_status(
    index=5, 
    filled_qty=10, 
    filled_avg_price=148.25,
    side="buy"
)
```

## Best Practices

1. **Always use CSVService for trading operations** - It handles the complex logic of share distribution and profit tracking
2. **CSVCore should only be extended, not used directly** - Use the specialized subclasses
3. **Validate CSV data after any updates** - The validate_csv_data() method ensures data integrity
4. **Use constants for trading types** - Import TradingType from constants.py
5. **Handle exceptions for file operations** - CSV operations can throw FileNotFoundError and other exceptions

## Development Guidelines

When extending the CSV utilities:

1. Maintain the layered architecture (core -> service -> tools)
2. Use type hints for better code documentation
3. Add appropriate error handling and logging
4. Update metadata file when adding new columns
5. Follow the established naming conventions

## Command-Line Usage

The csv_tool.py module can be run directly for CSV creation and manipulation:

```bash
python -m main.bots.SCALE_T.csv_utils.csv_tool --ticker AAPL --trading-type paper
```

This will start an interactive session for creating or modifying CSV files.

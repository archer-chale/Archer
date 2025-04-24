# Alpaca Interface for SCALE_T

## Overview

The `alpaca_interface.py` module provides a robust interface for interacting with the Alpaca brokerage API using the alpaca-py SDK. It's designed to be used within the SCALE_T trading bot ecosystem to execute trades, check account status, and manage orders.

## Features

- **Environment-aware Trading**: Support for both paper trading and live trading environments
- **Order Management**: Place, check, and cancel stock orders
- **Account Information**: Retrieve account details like buying power and position sizes
- **Real-time Pricing**: Get current market prices for symbols
- **Order Type Support**: Handle both market and limit orders, including fractional shares
- **Automatic Validation**: Verify API keys and account status before trading

## Prerequisites

- Python 3.6+
- Valid Alpaca account with API keys
- Environment variables configured (see Configuration section)

## Installation

The module is part of the SCALE_T bot package. No separate installation is needed if you're using the bot.

## Configuration

The interface requires Alpaca API keys to be set as environment variables:

```
# For paper trading
PAPER_ALPACA_KEY_ID=your_paper_key
PAPER_ALPACA_SECRET_KEY=your_paper_secret

# For live trading
LIVE_ALPACA_KEY_ID=your_live_key
LIVE_ALPACA_SECRET_KEY=your_live_secret
```

These can be placed in an `.env` file in the project root, which will be loaded automatically.

## Usage

### Basic Initialization

```python
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface

# Initialize for paper trading with a specific ticker
alpaca = AlpacaInterface(trading_type="paper", ticker="AAPL")

# Initialize for live trading
# alpaca = AlpacaInterface(trading_type="live", ticker="AAPL")
```

### Placing Orders

```python
# Place a buy limit order
order = alpaca.place_order(
    side="buy",  # or OrderSide.BUY
    price=150.00,  # limit price
    quantity=1.5  # supports fractional shares
)

# Place a sell limit order
order = alpaca.place_order(side="sell", price=160.00, quantity=1)
```

### Checking Account & Positions

```python
# Get current buying power
buying_power = alpaca.get_buying_power()
print(f"Available buying power: ${buying_power}")

# Check current position
shares = alpaca.get_shares_count()
print(f"Current shares held: {shares}")

# Get current market price
price = alpaca.get_current_price()
print(f"Current price of {alpaca.ticker}: ${price}")
```

### Order Management

```python
# Check status of a specific order
order = alpaca.get_order_by_id("order_id_here")

# Cancel an order
success = alpaca.cancel_order("order_id_here")
if success:
    print("Order canceled successfully")
```

## Error Handling

The interface includes robust error handling for API errors, connectivity issues, and validation problems. All errors are logged using the configured logger.

## Key Methods

| Method | Description |
|--------|-------------|
| `__init__(trading_type, ticker)` | Initialize the interface with trading type and ticker |
| `validate_alpaca_keys()` | Validate API keys and account status |
| `place_order(side, price, quantity)` | Place buy/sell orders |
| `get_current_price()` | Get the latest market price |
| `get_shares_count()` | Get the current position size |
| `get_buying_power()` | Get available buying power |
| `get_order_by_id(order_id)` | Retrieve order details |
| `cancel_order(order_id)` | Cancel an existing order |

## Important Notes

1. The interface automatically validates keys on initialization
2. Fractional orders are placed as market orders with price validation
3. Whole share orders are placed as limit orders
4. The module handles converting between string side indicators ('buy'/'sell') and OrderSide enums

## Logging

The module uses a configured logger (from `common.logging_config`) that tracks all operations, errors, and warnings.

## Testing

You can test your Alpaca API key setup by running the module directly:

```bash
python -m main.bots.SCALE_T.brokerages.alpaca_interface
```

This will validate both paper and live trading keys if configured.

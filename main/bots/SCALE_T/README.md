# SCALE_T Trading Bot

## Overview

SCALE_T is an automated trading bot implementing a grid/ladder trading strategy. It places buy orders at predefined price levels as prices fall and sell orders as prices rise, capturing profits from price oscillations. The bot uses Alpaca Markets as its brokerage platform and follows a scalable, CSV-driven configuration approach.

## Project Structure

```
SCALE_T/
├── brokerages/                # Brokerage integrations
│   └── alpaca_interface.py    # Alpaca Markets API wrapper
├── common/                    # Shared utilities
│   ├── constants.py           # System-wide constants
│   ├── logging_config.py      # Logging configuration
│   └── ...
├── csv_utils/                 # CSV configuration system
│   ├── csv_core.py            # Base CSV operations
│   ├── csv_service.py         # Trading-specific CSV operations
│   └── ...
├── trading/                   # Trading logic
│   ├── decision_maker.py      # Core trading intelligence
│   └── constants.py           # Trading-specific constants
├── engine.py                  # Main entry point
├── create_scale_t_csv.py      # Utility to create trading configurations
├── Dockerfile                 # Container definition
└── requirements.txt           # Python dependencies
```

## Requirements

### System Requirements

- Python 3.10+
- Docker (for containerized deployment)
- Internet connectivity for API communication

### Dependencies

- `alpaca-py` (≥0.8.0): Alpaca Markets API client
- `python-dotenv` (≥1.0.0): Environment variable management

### API Keys

You need valid Alpaca Markets API keys:

1. **Paper Trading**: For testing with simulated money
   - `PAPER_ALPACA_API_KEY_ID`
   - `PAPER_ALPACA_API_SECRET_KEY`

2. **Live Trading**: For real money trading (use with caution)
   - `ALPACA_API_KEY_ID`
   - `ALPACA_API_SECRET_KEY`

## Setup Guide

### 1. Environment Setup

Create a `.env` file in the `configs` directory with your API keys:

```
# Alpaca API Keys - Paper Trading
PAPER_ALPACA_API_KEY_ID=your_paper_key_here
PAPER_ALPACA_API_SECRET_KEY=your_paper_secret_here

# Alpaca API Keys - Live Trading
ALPACA_API_KEY_ID=your_live_key_here
ALPACA_API_SECRET_KEY=your_live_secret_here

# Logging Configuration
LOG_LEVEL=DEBUG
CONSOLE_LOG_LEVEL=INFO
```

### 2. Directory Structure Setup

Ensure these directories exist:

```
data/
└── SCALE_T/
    ├── logs/
    ├── templates/
    │   ├── SCALE_T.csv
    │   └── csv_versions_metadata.json
    └── ticker_data/
        ├── paper/
        └── live/
```

### 3. Creating Trading Configuration

For each ticker you want to trade, create a CSV configuration file:

```bash
# Option 1: Using the built-in script
python -m main.bots.SCALE_T.create_scale_t_csv

# Option 2: Using the more advanced CSV tool
python -m main.bots.SCALE_T.csv_utils.csv_tool --ticker AAPL --trading-type paper
```

This will create a CSV file that defines your trading strategy parameters.

### 4. Running the Bot

#### Direct Execution

```bash
# Run the bot for a specific ticker
python -m main.bots.SCALE_T.engine AAPL paper
```

#### Docker Execution

```bash
# Build the Docker image
docker build -t scale-t-bot -f main/bots/SCALE_T/Dockerfile .

# Run the container
docker run -d --name scale-t-aapl \
  -v /path/to/data:/app/data \
  -v /path/to/configs:/app/configs \
  scale-t-bot AAPL paper
```

## Development Workflow

### Core Concepts

1. **CSV-Driven Trading**: All trading parameters are stored in CSV files, making strategies easy to adjust without code changes.
2. **Event-Driven Architecture**: The bot reacts to real-time price and order updates through event queues.
3. **Modular Design**: Clean separation between brokerage access, trading logic, and configuration.

### Adding New Features

1. **Brokerage Integration**: 
   - Add new broker connectors to the `brokerages` directory
   - Implement the same interface as `AlpacaInterface` for consistency

2. **Trading Strategy Enhancements**:
   - Modify the `DecisionMaker` class in `trading/decision_maker.py`
   - Update buy/sell decision logic in `_check_place_buy_order` and `_check_place_sell_order`

3. **CSV Configuration Updates**:
   - Update the metadata template at `data/SCALE_T/templates/csv_versions_metadata.json`
   - Modify CSV schema in the `CSVCore` validation methods

### Testing

1. **API Key Validation**:
   ```bash
   python -c "from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface; AlpacaInterface()"
   ```

2. **CSV Validation**:
   ```bash
   python -c "from main.bots.SCALE_T.csv_utils.csv_service import CSVService; CSVService('AAPL', 'paper')"
   ```

3. **Paper Trading**: Always test new features with paper trading before live trading.

## Logging and Monitoring

Logs are stored in the `data/SCALE_T/logs/` directory, organized by date:

```
data/SCALE_T/logs/
└── YYYY/
    └── MM/
        └── SCALE_T-YYYY-MM-DD.log
```

Monitor logs for:

- Price updates (frequency indicates data stream health)
- Order execution and updates (shows trading activity)
- Error messages (require immediate attention)

## Troubleshooting

### Common Issues

1. **Missing CSV Files**:
   - Ensure you've created a CSV configuration for your ticker
   - Check the correct path at `data/SCALE_T/ticker_data/paper/TICKER.csv`

2. **API Key Issues**:
   - Verify keys in your `.env` file
   - Confirm keys have appropriate permissions in Alpaca dashboard

3. **Order Placement Failures**:
   - Check account buying power
   - Verify ticker is tradable during current market hours
   - Confirm no PDT (Pattern Day Trader) restrictions

4. **Bot Stops Processing**:
   - Check for exceptions in the log files
   - Verify internet connectivity
   - Ensure Alpaca API is operational

## Contributing

To contribute to the SCALE_T bot:

1. Understand the architecture by reviewing the README files in each subdirectory
2. Follow the existing code style and patterns
3. Add comprehensive logging for all new functionality
4. Document any changes to the trading logic or API interactions
5. Test thoroughly with paper trading before submitting changes

## Safety Guidelines

1. **Start with Paper Trading**: Always test new features and strategies with paper trading.
2. **Risk Management**: Configure appropriate position sizes and price levels.
3. **Continuous Monitoring**: Regularly check logs and performance metrics.
4. **Failsafes**: The bot includes validation steps to prevent mismatched positions.

## License

Internal use only. All rights reserved.

---

*For additional information, please refer to the README files in each subdirectory for component-specific documentation.*

# Docker Compose Generator

## Overview

This repository contains a multi-service trading infrastructure that allows for automated trading using various strategies. The `generate_compose.py` script dynamically generates a Docker Compose configuration to run multiple trading bots simultaneously, each handling different ticker symbols, along with supporting services like Redis and the Alpaca broker service.

## Project Architecture

The trading infrastructure consists of several components:

1. **SCALE_T Trading Bots**: Grid/ladder-based trading strategy bots that make buy/sell decisions based on predefined price levels
2. **Alpaca Broker Service**: Centralized broker that handles market data streaming and order execution
3. **Redis**: Message broker for real-time communication between services using pub/sub patterns
4. **Supporting Utilities**: Shared libraries for Redis communication, logging, and notification

```
┌─────────────────┐      ┌───────────────┐
│                 │      │               │
│  Alpaca Broker  │─────►│     Redis     │
│    (Market      │      │  (Message     │
│     Data)       │◄─────│   Broker)     │
└─────────────────┘      └───────────────┘
                                ▲
                                │
                                ▼
            ┌──────────────────┬──────────────────┐
            │                  │                  │
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │               │  │               │  │               │
      │  SCALE_T Bot  │  │  SCALE_T Bot  │  │  SCALE_T Bot  │
      │   (AAPL)      │  │   (MSFT)      │  │   (TSLA)      │
      └───────────────┘  └───────────────┘  └───────────────┘
```

## The Generate Compose Script

The `generate_compose.py` script:

1. Reads a list of ticker symbols from `configs/tickers.txt`
2. Creates the base services (Redis and Alpaca broker) configuration
3. Dynamically generates a SCALE_T bot service for each ticker symbol
4. Writes the complete configuration to a `docker-compose.yml` file

This approach allows for easily scaling up or down the number of trading bots without manual configuration.

## How to Run

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose installed
- Alpaca API keys (placed in `configs/.env`)
- List of tickers to trade (in `configs/tickers.txt`)

### Step 1: Configure Tickers

Edit `configs/tickers.txt` to include the ticker symbols you want to trade, one per line:

```
AAPL
MSFT
TSLA
```

### Step 2: Set Up Environment Variables

Create a `configs/.env` file with your Alpaca API credentials:

```
APCA_API_KEY_ID=your_api_key
APCA_API_SECRET_KEY=your_api_secret
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

### Step 3: Generate the Docker Compose File

```bash
python generate_compose.py
```

This will create a `docker-compose.generated.yml` file configured with all necessary services.

### Step 4: Start the Trading Infrastructure

```bash
docker-compose -f docker-compose.generated.yml up --build 
```

To run only specific services:

```bash
docker-compose up -d redis alpaca_broker scale_t_AAPL
```

### Step 5: Monitor Logs

```bash
# All logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f scale_t_AAPL
```

## Important Directories

- `main/alpaca_broker/`: The centralized Alpaca broker service
- `main/bots/SCALE_T/`: The SCALE_T trading bot implementation
- `main/utils/redis/`: Redis pub/sub library for inter-service communication
- `configs/`: Configuration files and environment variables

## CSV-Driven Trading Strategy

The SCALE_T bot uses CSV files to define trading strategies, with each row representing a price level in a grid/ladder strategy:

1. Create CSV files for each ticker using `create_scale_t_csv.py`
2. Each CSV defines buy prices, sell prices, and target shares at each price level
3. The DecisionMaker monitors real-time prices and executes orders based on the CSV configuration

## Development Workflow

1. Create or modify CSV strategy files in the `bots/SCALE_T/csvs/` directory
2. Update the tickers list in `configs/tickers.txt`
3. Run `python generate_compose.py` to update the Docker Compose configuration
4. Start the services with `docker-compose up -d`
5. Monitor logs and performance

## Extending the System

### Adding New Trading Bots

To add a new type of trading bot:

1. Create a new directory under `main/bots/`
2. Implement the bot's logic and Dockerfile
3. Update the `generate_compose.py` script to include the new bot type

### Modifying the Compose Generator

The `generate_compose.py` script can be extended to:

- Support different broker services
- Add monitoring/visualization tools
- Configure resource limits for containers
- Support different deployment environments

## Troubleshooting

- **Connection Issues**: Ensure Redis is running and accessible
- **API Errors**: Verify Alpaca API keys in the `.env` file
- **Missing Ticker Data**: Check that the ticker symbols are valid and active
- **Bot Crashes**: Inspect logs with `docker-compose logs -f scale_t_TICKER`

## Additional Resources

For more detailed documentation, see:

- [SCALE_T Bot README](main/bots/SCALE_T/README.md)
- [Alpaca Broker README](main/alpaca_broker/README.md)
- [Redis Utilities README](main/utils/redis/README.md)
- [DecisionMaker Deep Dive](main/bots/SCALE_T/trading/DECISION_MAKER.md)

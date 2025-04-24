# Alpaca Broker Service

## Overview

The Alpaca Broker Service is a standalone microservice that acts as a centralized hub for Alpaca market data and order streams. It connects to Alpaca's API to receive real-time price updates and order status changes, then distributes this data to trading bots via Redis pub/sub channels.

This service follows a broker pattern where multiple trading bots can share a single connection to Alpaca's streaming API, improving efficiency and reducing API connection overhead.

## Architecture

```
┌─────────────────┐    Alpaca API     ┌─────────────────┐
│                 │◄───Streaming─────►│                 │
│  Trading Bots   │                   │  Alpaca Broker  │
│  (Subscribers)  │◄───Redis PubSub──►│    Service      │
│                 │                   │                 │
└─────────────────┘                   └─────────────────┘
```

The service consists of these key components:

1. **AlpacaBroker Class**: Core class managing connections and data streams
2. **Price Producer**: Thread that listens for real-time price updates
3. **Order Producer**: Thread that listens for order status updates
4. **Redis Integration**: Publisher/Subscriber for communicating with trading bots

## Features

- **Shared Connection**: Multiple trading bots can share a single connection to Alpaca's streaming API
- **Dynamic Symbol Subscription**: Trading bots can register and unregister symbols to receive price updates
- **Real-time Data Distribution**: Market data and order updates are forwarded in real-time via Redis
- **Graceful Shutdown**: Properly closes all connections and threads on termination
- **Containerization**: Ready to deploy as a Docker container

## Configuration

### Environment Variables

The broker service relies on these environment variables:

```
# Alpaca API Keys - Paper Trading
PAPER_ALPACA_API_KEY_ID=your_paper_key
PAPER_ALPACA_API_SECRET_KEY=your_paper_secret

# Alpaca API Keys - Live Trading
ALPACA_API_KEY_ID=your_live_key
ALPACA_API_SECRET_KEY=your_live_secret

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logging Configuration
LOG_LEVEL=INFO
```

These should be placed in `.env` file in the `configs` directory.

## Installation

### Prerequisites

- Python 3.10+
- Redis server running
- Valid Alpaca API keys

### Dependencies

```
alpaca-py==0.10.0
python-dotenv==1.0.0
redis>=4.5.1,<5.0.0
```

## Running the Service

### Direct Execution

```bash
# Install dependencies
pip install -r main/alpaca_broker/requirements.txt

# Run the broker service
python -m main.alpaca_broker.main
```

### Docker Execution

```bash
# Build the Docker image
docker build -t alpaca-broker -f main/alpaca_broker/Dockerfile .

# Run the container
docker run -d --name alpaca-broker \
  --env-file ./configs/.env \
  --network host \
  alpaca-broker
```

## How It Works

### Registration Process

1. Trading bots send registration messages to the `broker:registration` Redis channel
2. The broker subscribes to requested symbols on Alpaca's streaming API
3. Price updates for subscribed symbols are published to `price:SYMBOL` channels
4. Order updates are published to `order:ACCOUNT_ID` channels

### Message Format

#### Registration Message

```json
{
  "action": "register",
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "account_id": "your_alpaca_account_id"
}
```

#### Price Update Message

```json
{
  "type": "price_update",
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": 1628107200
}
```

#### Order Update Message

```json
{
  "type": "order_update",
  "order_id": "order_id_here",
  "status": "filled",
  "filled_qty": 10,
  "filled_avg_price": 150.25,
  "side": "buy",
  "timestamp": 1628107300
}
```

## Integration with Trading Bots

Trading bots can integrate with the Alpaca Broker service by:

1. **Subscribing to Price Updates**:
   ```python
   from main.utils.redis import RedisPublisher, RedisSubscriber, CHANNELS
   
   # Register for symbol updates
   publisher = RedisPublisher()
   publisher.publish(CHANNELS.BROKER_REGISTRATION, {
       "action": "register",
       "symbols": ["AAPL"],
       "account_id": "your_account_id"
   })
   
   # Listen for price updates
   subscriber = RedisSubscriber()
   subscriber.subscribe(f"price:AAPL", handle_price_update)
   subscriber.start_listening()
   ```

2. **Listening for Order Updates**:
   ```python
   # Listen for order updates
   subscriber = RedisSubscriber()
   subscriber.subscribe(f"order:{account_id}", handle_order_update)
   ```

## Error Handling

The broker service implements several error handling mechanisms:

- **Connection Retry**: Automatically attempts to reconnect if Redis or Alpaca connections are lost
- **Logging**: Detailed logging for debugging and monitoring
- **Graceful Degradation**: Continues functioning with available services if some fail

## Monitoring

Monitor the broker service by:

1. Watching Redis channels with `redis-cli`:
   ```bash
   redis-cli subscribe broker:logs
   ```

2. Checking the application logs:
   ```bash
   docker logs alpaca-broker
   ```

## Development Guidelines

When extending the Alpaca Broker:

1. Maintain the thread safety of the existing implementation
2. Follow the established pub/sub patterns for communication
3. Add appropriate error handling and logging
4. Test thoroughly with paper trading before live deployment
5. Ensure proper cleanup of resources in the `stop()` method

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**:
   - Verify Redis is running and accessible
   - Check network configuration if running in Docker

2. **Alpaca API Connection Issues**:
   - Validate API keys in your .env file
   - Check if Alpaca services are operational

3. **Missing Price Updates**:
   - Ensure symbols are properly registered
   - Verify the trading hours for the requested symbols

## License

Internal use only. All rights reserved.

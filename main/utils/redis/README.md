# Redis Pub/Sub Library

A lightweight, channel-based Redis pub/sub library for Python applications. This library provides simple, schema-validated message publishing and subscription capabilities for real-time data distribution between services.

## Features

- **Schema-based message validation**: Define expected message structures for each channel
- **Simple API**: Clean interfaces for publishing and subscribing to channels
- **Connection management**: Centralized Redis connection handling
- **Real-time messaging**: Event-driven design with callback registration
- **Thread safety**: Safe background processing of incoming messages

## Installation

1. Add this library to your project
2. Install required dependencies:

```bash
pip install redis>=4.5.1,<5.0.0
```

## Quick Start

### Publishing Messages

```python
from main.utils.redis import RedisPublisher, CHANNELS

# Create a publisher
publisher = RedisPublisher()

# Publish a price update to a ticker channel
ticker = "AAPL"
ticker_channel = CHANNELS.get_ticker_channel(ticker)
price_data = {
    'type': 'price',
    'timestamp': '2025-04-24T09:45:00.000Z',
    'price': 150.00,
    'volume': 1000,
    'symbol': ticker
}
publisher.publish(ticker_channel, price_data)

# Close when done
publisher.close()
```

### Subscribing to Messages

```python
from main.utils.redis import RedisSubscriber, CHANNELS
import time

# Define a message handler
def ticker_handler(message):
    data = message['data']
    if data['type'] == 'price':
        print(f"Received price: ${data['price']:.2f} for {data['symbol']}")
    
# Create a subscriber
subscriber = RedisSubscriber()

# Subscribe to ticker updates
ticker = "AAPL"
ticker_channel = CHANNELS.get_ticker_channel(ticker)
subscriber.subscribe(ticker_channel, ticker_handler)

# Start listening for messages (in a background thread)
subscriber.start_listening()

# Keep your application running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    subscriber.close()
```

## API Reference

### Constants

#### CHANNELS

Defines standardized channel names for pub/sub communication:

```python
from main.utils.redis import CHANNELS

# Fixed registration channel
CHANNELS.BROKER_REGISTRATION  # "BROKER_REGISTRATION"

# Dynamic ticker channels
ticker_channel = CHANNELS.get_ticker_channel("AAPL")  # "TICKER_UPDATES_AAPL"

# Get schema for a channel
schema = CHANNELS.get_schema(CHANNELS.BROKER_REGISTRATION)
ticker_schema = CHANNELS.get_schema(ticker_channel)
```

#### MESSAGE_SCHEMAS

Defines message schemas for each channel:

```python
from main.utils.redis import MESSAGE_SCHEMAS

# Access schemas for validation
registration_schema = MESSAGE_SCHEMAS.BROKER_REGISTRATION
ticker_updates_schema = MESSAGE_SCHEMAS.TICKER_UPDATES

# Get schema dynamically
schema = MESSAGE_SCHEMAS.get(CHANNELS.BROKER_REGISTRATION)
```

### Connection

#### RedisConnection

Manages connections to Redis:

```python
from main.utils.redis import RedisConnection

# Create a connection
connection = RedisConnection(host='localhost', port=6379, db=0)

# Get the Redis client
redis_client = connection.connection

# Close the connection when done
connection.disconnect()
```

### Publisher

#### RedisPublisher

Publishes messages to Redis channels:

```python
from main.utils.redis import RedisPublisher, CHANNELS

# Create a publisher
publisher = RedisPublisher(host='localhost', port=6379, db=0)

# Publish a ticker update message
ticker_channel = CHANNELS.get_ticker_channel("MSFT")
publisher.publish(ticker_channel, {
    'type': 'price',
    'timestamp': '2025-04-24T09:45:00.000Z',
    'symbol': 'MSFT',
    'price': 300.50,
    'volume': 2000
})

# Publish a broker registration message
publisher.publish(CHANNELS.BROKER_REGISTRATION, {
    'action': 'subscribe',
    'ticker': 'MSFT'
})

# Clean up
publisher.close()
```

### Subscriber

#### RedisSubscriber

Subscribes to Redis channels:

```python
from main.utils.redis import RedisSubscriber, CHANNELS

# Create a subscriber
subscriber = RedisSubscriber(host='localhost', port=6379, db=0)

# Define handlers
def ticker_handler(message):
    # Process ticker updates (price or order)
    data = message['data']
    if data['type'] == 'price':
        print(f"Price update for {data['symbol']}: {data['price']}")
    elif data['type'] == 'order':
        print(f"Order update for {data['symbol']}")

def registration_handler(message):
    # Process broker registration messages
    data = message['data']
    print(f"Registration action: {data['action']} for {data['ticker']}")

# Subscribe to channels
ticker_channel = CHANNELS.get_ticker_channel("AAPL")
subscriber.subscribe(ticker_channel, ticker_handler)
subscriber.subscribe(CHANNELS.BROKER_REGISTRATION, registration_handler)

# Start listening for messages
thread = subscriber.start_listening()

# Unsubscribe from a specific channel
subscriber.unsubscribe(ticker_channel)

# Unsubscribe from all channels
subscriber.unsubscribe()

# Stop listening and clean up
subscriber.close()
```

### Message Functions

Utilities for message validation and formatting:

```python
from main.utils.redis import (
    validate_message,
    create_message,
    format_for_channel,
    parse_message,
    extract_data,
    MessageValidationError
)

# Validate a message against a channel's schema
ticker_channel = CHANNELS.get_ticker_channel("AAPL")
try:
    validate_message(ticker_channel, {
        'type': 'price',
        'timestamp': '2025-04-24T09:45:00.000Z',
        'symbol': 'AAPL',
        'price': 150.00
    })
except MessageValidationError as e:
    print(f"Invalid message: {e}")

# Create a standardized message
message = create_message({
    'type': 'price',
    'timestamp': '2025-04-24T09:45:00.000Z',
    'symbol': 'AAPL',
    'price': 150.00
})

# Format a message for a specific channel (validates and formats)
message_json = format_for_channel(ticker_channel, {
    'type': 'price',
    'timestamp': '2025-04-24T09:45:00.000Z',
    'symbol': 'AAPL',
    'price': 150.00
})

# Parse a message from JSON
parsed = parse_message(message_json)

# Extract data from a message
data = extract_data(parsed)
```

## Message Formats

Messages are formatted as JSON with a standard structure:

```json
{
  "data": {
    "type": "price",
    "timestamp": "2025-04-24T09:45:00.000Z",
    "symbol": "AAPL",
    "price": 150.00,
    "volume": 1000
  },
  "timestamp": "2025-04-24T09:45:01.123456",
  "sender": "broker_service"
}
```

### Channel-Specific Schemas

There are two main schema types:

1. **Broker Registration Schema**: Used for the BROKER_REGISTRATION channel
   - Required fields: `action`, `ticker`
   - Allowed actions: `subscribe`, `unsubscribe`

2. **Ticker Updates Schema**: Used for all ticker update channels (TICKER_UPDATES_*)
   - Required fields: `type`, `timestamp`
   - Optional fields: `price`, `volume`, `symbol`, `order_data`
   - Types: `price`, `order`

## Error Handling

The library raises `MessageValidationError` for validation issues:

```python
from main.utils.redis import MessageValidationError, CHANNELS

try:
    # Missing required field 'type'
    ticker_channel = CHANNELS.get_ticker_channel("AAPL")
    publisher.publish(ticker_channel, {
        'symbol': 'AAPL',
        'price': 150.00
    })
except MessageValidationError as e:
    print(f"Validation error: {e}")
```

## Integration with Alpaca Broker Service

This Redis library is used by the Alpaca Broker Service to:

1. **Receive registration requests**:
   - Trading bots register interest in specific tickers
   - Broker subscribes to Alpaca streaming for those tickers

2. **Distribute market data**:
   - Price updates are published to ticker-specific channels
   - Order updates are published to account-specific channels

## Usage in SCALE_T Trading Bot

The SCALE_T bot uses this library to:

1. **Register interest in tickers**:
   - Sends registration messages to the broker
   - Subscribes to ticker-specific channels

2. **Receive real-time data**:
   - Processes price updates to trigger trading decisions
   - Processes order updates to track position changes

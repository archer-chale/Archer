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
pip install -r main/utils/redis/requirements.txt
```

## Quick Start

### Publishing Messages

```python
from main.utils.redis import RedisPublisher, CHANNELS

# Create a publisher
publisher = RedisPublisher()

# Publish a price update
price_data = {
    'symbol': 'AAPL',
    'price': 150.00,
    'volume': 1000
}
publisher.publish(CHANNELS.PRICE_DATA, price_data, sender='my_service')

# Close when done
publisher.close()
```

### Subscribing to Messages

```python
from main.utils.redis import RedisSubscriber, CHANNELS
import time

# Define a message handler
def price_handler(message):
    data = message['data']
    print(f"Received price: ${data['price']:.2f} for {data['symbol']}")
    
# Create a subscriber
subscriber = RedisSubscriber()

# Subscribe to price updates
subscriber.subscribe(CHANNELS.PRICE_DATA, price_handler)

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

# Use predefined channels
CHANNELS.PRICE_DATA  # "PRICE_DATA"
```

#### MESSAGE_SCHEMAS

Defines message schemas for each channel:

```python
from main.utils.redis import MESSAGE_SCHEMAS

# Access schemas for validation
price_schema = MESSAGE_SCHEMAS.PRICE_DATA
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

# Publish a message
publisher.publish(CHANNELS.PRICE_DATA, {
    'symbol': 'MSFT',
    'price': 300.50,
    'volume': 2000
}, sender='my_service')

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

# Define a handler
def message_handler(message):
    # Process the message
    print(message)

# Subscribe to a channel
subscriber.subscribe(CHANNELS.PRICE_DATA, message_handler)

# Start listening for messages
thread = subscriber.start_listening()

# Unsubscribe from a specific channel
subscriber.unsubscribe(CHANNELS.PRICE_DATA)

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
try:
    validate_message(CHANNELS.PRICE_DATA, {'symbol': 'AAPL', 'price': 150.00})
except MessageValidationError as e:
    print(f"Invalid message: {e}")

# Create a standardized message
message = create_message({'symbol': 'AAPL', 'price': 150.00}, sender='my_service')

# Format a message for a specific channel (validates and formats)
message_json = format_for_channel(CHANNELS.PRICE_DATA, 
                                 {'symbol': 'AAPL', 'price': 150.00},
                                 sender='my_service')

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
    // Channel-specific data fields
    "symbol": "AAPL",
    "price": 150.00
  },
  "timestamp": "2025-04-18T12:34:56.789012",
  "sender": "my_service"
}
```

### Channel-Specific Schemas

## Error Handling

The library raises `MessageValidationError` for validation issues:

```python
from main.utils.redis import MessageValidationError

try:
    # Some operation that might fail validation
    publisher.publish(CHANNELS.PRICE_DATA, {'symbol': 'AAPL'})  # Missing 'price'
except MessageValidationError as e:
    print(f"Validation error: {e}")
```

## Examples

Example scripts are available in the `main/utils/redis/examples` directory:

- `test_publisher.py` - Example of publishing price messages
- `test_subscriber.py` - Example of subscribing to price messages
- `test_simplified_message.py` - Example of message validation and handling
- `test_redis_lib.py` - Example of the publisher and subscriber working together

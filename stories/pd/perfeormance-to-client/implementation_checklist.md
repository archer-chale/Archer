# Performance-to-Client Implementation Checklist

This checklist outlines all the necessary steps to implement the stock performance data feature, which will allow users to view the performance of each stock in the frontend application.

## 1. Update Redis Constants

**File:** `main\utils\redis\constants.py`

**Why:** We need to define a new channel pattern for ticker performance data to use in Redis pub/sub.

**Tasks:**
- [ ] Add a new static method to the `CHANNELS` class to generate performance channel names
- [ ] Add a schema definition for performance data in `MESSAGE_SCHEMAS`
- [ ] Update the schema getter methods to handle the new channel pattern

**Pseudo Code:**
```python
# In CHANNELS class
@staticmethod
def get_ticker_performance_channel(ticker: str) -> str:
    """Generate the dynamic channel name for a specific ticker's performance data."""
    if not ticker or not isinstance(ticker, str):
        logger.error(f"Invalid ticker provided for performance channel generation: {ticker}")
        raise ValueError("Ticker must be a non-empty string")
    return f"TICKER_PERFORMANCE_{ticker.upper()}"

# In MESSAGE_SCHEMAS class
# Add new schema for performance data
TICKER_PERFORMANCE = {
    "required_fields": ["symbol", "total", "unrealized", "realized", "timestamp"],
    "optional_fields": ["converted"],
    "field_types": {
        "total": (int, float, str),
        "unrealized": (int, float, str),
        "realized": (int, float, str),
        "converted": (int, float, str),
        "timestamp": str,
        "symbol": str
    },
    "allowed_values": {}
}

# Update get_schema method to handle performance channels
@classmethod
def get_schema(cls, channel_name: str):
    # ...existing code...
    elif channel_name.startswith("TICKER_PERFORMANCE_"):
        return MESSAGE_SCHEMAS.TICKER_PERFORMANCE
    # ...rest of method...

# Update get method as well
@classmethod
def get(cls, channel_name: str, default=None):
    # ...existing code...
    elif channel_name.startswith("TICKER_PERFORMANCE_"):
        return cls.TICKER_PERFORMANCE
    # ...rest of method...
```

## 2. Modify Performance Calculator

**File:** `main\performance\daily_profit_calc.py`

**Why:** Currently, the performance calculator saves data to a local file. We need to extend it to publish updates to Redis so the data can be forwarded to Firebase.

**Tasks:**
- [ ] Add Redis publisher initialization
- [ ] Create method to publish performance data to Redis
- [ ] Modify existing code to publish performance updates when calculated

**Pseudo Code:**
```python
# Add imports
from main.utils.redis import RedisPublisher, CHANNELS

# Add to __init__ method
self.publisher = RedisPublisher(host=redis_host, port=redis_port, db=redis_db)

# New method to publish performance
def publish_performance_data(self, symbol, performance_data):
    """
    Publish performance data to Redis for a specific symbol.
    
    Args:
        symbol: The ticker symbol
        performance_data: Dictionary with performance metrics
    """
    try:
        channel = CHANNELS.get_ticker_performance_channel(symbol)
        
        # Ensure timestamp is included
        if 'timestamp' not in performance_data:
            performance_data['timestamp'] = dt.now(timezone.utc).isoformat()
            
        # Add symbol to data
        performance_data['symbol'] = symbol
            
        # Publish to Redis
        self.publisher.publish(
            channel=channel,
            message_data=performance_data,
            sender='performance_calculator'
        )
        self.logger.info(f"Published performance data for {symbol} to Redis")
        
    except Exception as e:
        self.logger.error(f"Error publishing performance data for {symbol}: {e}")

# Modify save_daily_profits to also publish to Redis
# In the appropriate place after calculating profits for a symbol:
for symbol, profit_data in updated_profits.items():
    # After saving to file or alongside it
    if symbol != 'aggregate':  # Handle aggregate separately
        self.publish_performance_data(symbol, profit_data)
    else:
        # Publish aggregate as its own symbol
        self.publish_performance_data('aggregate', profit_data)

Comment:
- Are we currently looping to publish the performance data for each symbol?

```

## 3. Update Firebase Client

**File:** `main\firebase_client\src\firebase_client.py`

**Why:** We need to add methods to store performance data in Firebase for each ticker.

**Tasks:**
- [ ] Create a generic `store_ticker_data` method
- [ ] Implement a `store_performance` method using the generic method

**Pseudo Code:**
```python
def store_ticker_data(self, symbol: str, data_key: str, data_value: Dict[str, Any]) -> bool:
    """
    Generic method to store data for a ticker at a specific key
    
    Args:
        symbol: The ticker symbol (e.g., AAPL)
        data_key: The key under the ticker to store data (e.g., 'performance')
        data_value: The data to store
        
    Returns:
        bool: True if storing successful, False otherwise
    """
    if not self.db_ref:
        self.logger.error(f"Cannot store {data_key}: Firebase connection not established")
        return False
        
    try:
        # Store in Firebase - path will be /services/{symbol}/{data_key}
        service_ref = self.db_ref.child('services').child(symbol)
        service_ref.child(data_key).set(data_value)
        
        self.logger.info(f"Stored {data_key} for {symbol}")
        return True
        
    except Exception as e:
        self.logger.error(f"Error storing {data_key} for {symbol}: {e}")
        return False

def store_performance(self, symbol: str, performance_data: Dict[str, Any]) -> bool:
    """
    Store performance data for a ticker
    
    Args:
        symbol: The ticker symbol (e.g., AAPL)
        performance_data: Dictionary containing performance details
        
    Returns:
        bool: True if storing successful, False otherwise
    """
    try:
        # Format performance data for Firebase
        formatted_performance = {
            "total": performance_data.get("total", "0"),
            "unrealized": performance_data.get("unrealized", "0"),
            "realized": performance_data.get("realized", "0"),
            "converted": performance_data.get("converted", "0"),
            "timestamp": performance_data.get("timestamp", str(time.time()))
        }
        
        # Store using the generic method
        return self.store_ticker_data(symbol, 'performance', formatted_performance)
            
    except Exception as e:
        self.logger.error(f"Error formatting performance data for {symbol}: {e}")
        return False
```

## 4. Update Redis Subscriber

**File:** `main\firebase_client\src\redis_subscriber.py`

**Why:** We need to subscribe to performance channels and handle performance data messages.

**Tasks:**
- [ ] Update `subscribe_to_ticker_channels` to also subscribe to performance channels
- [ ] Add a handler method for performance data
- [ ] Update the `_message_handler` to route performance messages to the new handler

**Pseudo Code:**
```python
def subscribe_to_ticker_channels(self) -> None:
    """
    Subscribe to all ticker price update and performance channels
    """
    if not self.subscriber:
        self.logger.error("Cannot subscribe: Redis connection not established")
        return
        
    self.logger.info(f"Subscribing to {len(self.tickers)} ticker channels")
    for ticker in self.tickers:
        # Subscribe to price updates
        price_channel = CHANNELS.get_ticker_channel(ticker)
        success = self.subscriber.subscribe(price_channel, self._message_handler)
        if success:
            self.logger.info(f"Subscribed to channel: {price_channel}")
        else:
            self.logger.error(f"Failed to subscribe to channel: {price_channel}")
            
        # Subscribe to performance updates
        performance_channel = CHANNELS.get_ticker_performance_channel(ticker)
        success = self.subscriber.subscribe(performance_channel, self._message_handler)
        if success:
            self.logger.info(f"Subscribed to channel: {performance_channel}")
        else:
            self.logger.error(f"Failed to subscribe to channel: {performance_channel}")
    
    # Also subscribe to aggregate performance as its own "ticker"
    aggregate_performance_channel = CHANNELS.get_ticker_performance_channel('aggregate')
    success = self.subscriber.subscribe(aggregate_performance_channel, self._message_handler)
    if success:
        self.logger.info(f"Subscribed to channel: {aggregate_performance_channel}")
    else:
        self.logger.error(f"Failed to subscribe to channel: {aggregate_performance_channel}")

def _message_handler(self, message: Dict[str, Any]) -> None:
    """
    Handle incoming messages from Redis
    
    Args:
        message: The message received from Redis
    """
    try:
        channel = message.get('channel', '')
        data = message.get('data', {})
        timestamp = message.get('timestamp', 'unknown')
        sender = message.get('sender', 'unknown')
        
        # Determine message type based on channel
        if channel.startswith('TICKER_UPDATES_'):
            message_type = data.get('type')
            if message_type == 'price':
                self._handle_price_update(data, timestamp, sender)
            elif message_type == 'order':
                self._handle_order_update(data, timestamp, sender)
            else:
                self.logger.warning(f"Received unknown message type: {message_type} on channel {channel}")
        elif channel.startswith('TICKER_PERFORMANCE_'):
            self._handle_performance_update(data, timestamp, sender)
        else:
            self.logger.warning(f"Received message on unknown channel: {channel}")
            
    except Exception as e:
        self.logger.error(f"Error handling message: {e}")
        self.logger.debug(f"Raw message: {message}")

def _handle_performance_update(self, data: Dict[str, Any], timestamp: str, sender: str) -> None:
    """
    Handle performance update messages
    
    Args:
        data: The performance data from the message
        timestamp: The timestamp of the message
        sender: The sender of the message
    """
    symbol = data.get('symbol', 'unknown')
    total = data.get('total', 'unknown')
    unrealized = data.get('unrealized', 'unknown')
    realized = data.get('realized', 'unknown')
    
    self.logger.info(f"PERFORMANCE UPDATE [{timestamp}] from {sender}")
    self.logger.info(f"  Symbol: {symbol}, Total: {total}, Unrealized: {unrealized}, Realized: {realized}")
    self.logger.debug(f"  Raw data: {data}")
    
    # Store performance in Firebase if client is available
    if self.firebase_client:
        success = self.firebase_client.store_performance(symbol, data)
        if success:
            self.logger.debug(f"Successfully stored performance for {symbol} in Firebase")
        else:
            self.logger.warning(f"Failed to store performance for {symbol} in Firebase")
```

## 5. Testing and Verification

**Tasks:**
- [ ] Test the Redis channel creation and subscription
- [ ] Verify that performance data is correctly published to Redis
- [ ] Confirm Redis subscriber receives the performance data
- [ ] Check that Firebase Realtime Database contains performance data in the correct structure
- [ ] Validate that aggregate performance data is properly handled

**Test Approach:**
1. Manual code review of all modified files
2. Test the daily profit calculator in isolation
3. Run integration tests between performance calculator, Redis, and Firebase
4. Verify data in Firebase Realtime Database manually

## 6. Expected Data Structure in Firebase

The performance data should appear in Firebase with this structure:

```json
{
  "services": {
    "AAPL": {
      "price": "123.45",
      "timestamp": "2025-05-16T08:00:00.000Z",
      "orders": {...},
      "performance": {
        "total": "28.76",
        "unrealized": "28.76",
        "realized": "0.0",
        "converted": "0.0",
        "timestamp": "2025-05-16T08:00:00.000Z"
      }
    },
    "aggregate": {
      "performance": {
        "total": "840.87",
        "unrealized": "776.4",
        "realized": "43.57",
        "converted": "20.9",
        "timestamp": "2025-05-16T08:00:00.000Z"
      }
    }
  }
}
```

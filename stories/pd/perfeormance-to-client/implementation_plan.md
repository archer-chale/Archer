# Stock Performance Data Implementation Plan

## Overview
This document outlines the implementation plan for adding stock performance data to the Firebase Realtime Database, enabling users to view the performance of each stock in the frontend application.

## Requirements
- Create a new Redis channel for profit performance data with naming convention `TICKER_PERFORMANCE_{ticker_name}`
- Follow existing JSON structure for performance data (total, unrealized, realized, converted, timestamp)
- Store performance data as a child object of each ticker in Firebase
- Treat aggregate performance data as its own symbol with the same structure
- No historical data storage required - only latest performance values

## Implementation Steps

### 1. Update Redis Constants
- Add new constant for `TICKER_PERFORMANCE_{ticker_name}` pattern in `main\utils\redis\constants.py`

### 2. Modify Performance Calculator
- Update `main\performance\daily_profit_calc.py` to publish performance data to Redis
- Implement function to send updates to the new Redis channel when performance data changes
- Ensure both individual ticker updates and aggregate updates are published

### 3. Update Firebase Client
- Create a generic `store_ticker_data` method in `main\firebase_client\src\firebase_client.py`
  - Takes parameters: symbol, data_key, data_value
  - Allows reuse for different types of ticker data (performance, orders, etc.)
- Implement `store_performance` method using the generic method above
  - Properly structure performance data as a child of each ticker

### 4. Update Redis Subscriber
- Modify `main\firebase_client\src\redis_subscriber.py` to:
  - Subscribe to performance channels for each ticker
  - Add aggregate as one of the subscribed symbols
  - Create a message handler for performance data
  - Call the Firebase client to update performance data when messages arrive

### 5. Testing
- Verify data flows correctly from performance calculator to Redis
- Ensure Redis subscriber receives performance data and forwards to Firebase
- Confirm Firebase Realtime Database contains performance data in correct structure

## Data Structure
Performance data will be stored in Firebase with the following structure:

```
{
  "tickers": {
    "{ticker_symbol}": {
      "price": 123.45,
      "timestamp": "2025-05-16T08:00:00.000Z",
      "orders": [...],
      "performance": {
        "total": 28.76,
        "unrealized": 28.76,
        "realized": 0.0,
        "converted": 0.0,
        "timestamp": "2025-05-16T08:00:00.000Z"
      }
    },
    "aggregate": {
      "price": null,
      "timestamp": "2025-05-16T08:00:00.000Z",
      "performance": {
        "total": 840.87,
        "unrealized": 776.4,
        "realized": 43.57,
        "converted": 20.9,
        "timestamp": "2025-05-16T08:00:00.000Z"
      }
    }
  }
}
```

## Future Considerations
- Historical performance data tracking could be added in the future
- Performance visualization in the frontend will be addressed separately

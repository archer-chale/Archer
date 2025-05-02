# Firebase Client Service Implementation Design

## Overview
This document outlines the design for a Firebase client service that will subscribe to Redis channels containing bot trading data and forward this information to a Firebase Realtime Database. This service will allow users to monitor their trading bots' activities remotely via a mobile application.

## Architecture

### High-Level Components
1. **Redis Subscriber**: Listens to specific Redis channels for trading bot updates
2. **Data Processor**: Processes and formats incoming Redis messages
3. **Firebase Client**: Pushes processed data to the Firebase Realtime Database
4. **Docker Container**: Encapsulates the service for local deployment

```
┌─────────────────────────────────┐
│       Local User Environment    │
│                                 │
│  ┌───────────┐    ┌───────────┐ │
│  │ Trading   │    │  Alpaca   │ │
│  │   Bots    │    │  Broker   │ │
│  └─────┬─────┘    └─────┬─────┘ │
│        │                │       │
│        └────────┬───────┘       │
│                 │               │
│         ┌───────▼──────┐        │
│         │     Redis    │        │
│         │    Server    │        │
│         └───────┬──────┘        │
│                 │               │
│       ┌─────────▼───────────┐   │
│       │  Firebase Client    │   │
│       │      Service        │   │
│       └─────────┬───────────┘   │
│                 │               │
└─────────────────┼───────────────┘
                  │
         ┌────────▼────────┐
         │     Firebase    │
         │  Realtime DB    │
         └─────────────────┘
```

## Detailed Design

### Redis Subscription
- Connect to the local Redis server
- Subscribe to the `get_ticker_channel` for each ticker being monitored
- Handle reconnection and error cases

### Message Processing
The service will process two types of messages from the Redis channels:

1. **Price Updates**:
   ```json
   {
     "type": "price",
     "timestamp": "1619712345.678",
     "price": "150.25",
     "volume": "10000",
     "symbol": "AAPL"
   }
   ```

2. **Order Updates**:
   ```json
   {
     "type": "order",
     "timestamp": "1619712345.678",
     "symbol": "AAPL",
     "order_data": {
       "event": "fill",
       "execution_id": "12345",
       "order": {
         "id": "order-id-123",
         "client_order_id": "client-order-id-123",
         "created_at": "2023-04-26T14:30:45Z",
         "updated_at": "2023-04-26T14:31:00Z",
         "submitted_at": "2023-04-26T14:30:46Z",
         "filled_at": "2023-04-26T14:31:00Z",
         "expired_at": null,
         "canceled_at": null,
         "failed_at": null,
         "replaced_at": null,
         "replaced_by": null,
         "replaces": null,
         "asset_id": "asset-id-123",
         "symbol": "AAPL",
         "asset_class": "us_equity",
         "notional": null,
         "qty": "10",
         "filled_qty": "10",
         "filled_avg_price": "150.25",
         "order_class": "simple",
         "order_type": "market",
         "side": "buy",
         "time_in_force": "day",
         "limit_price": null,
         "stop_price": null,
         "status": "filled",
         "extended_hours": false,
         "legs": null,
         "trail_percent": null,
         "trail_price": null,
         "hwm": null,
         "source": "alpaca"
       },
       "position_qty": "100",
       "price": "150.25",
       "qty": "10"
     }
   }
   ```

### Firebase Integration

#### Data Structure
Data in Firebase will be organized by ticker, with each ticker having current price and order data:

```
firebase-realtime-db/
├── tickers/
│   ├── AAPL/
│   │   ├── current_price: { 
│   │   │   price: "150.25", 
│   │   │   volume: "10000", 
│   │   │   timestamp: "1619712345.678" 
│   │   │}
│   │   └── orders/
│   │       └── order-id-123: { 
│   │           event: "fill",
│   │           timestamp: "1619712345.678",
│   │           order: {...}
│   │       }
│   └── TSLA/
│       ├── current_price: {...}
│       └── orders/
```

This structure allows for:
- Easy querying of data for specific tickers
- Separate access to price and order data
- Simple addition of more tickers without schema changes
- Minimal storage usage by only keeping current price data
- Reduced database writes by only updating when data has changed

### Docker Configuration
The service will be containerized using Docker with the following considerations:
- Alpine Linux-based image for minimal footprint
- Required Python dependencies installed via pip
- Configuration via environment variables
- Volumes for potential persistent data or configuration
- Redis connection details configured at runtime

## Implementation Plan

### Component Structure
```
firebase-client-service/
├── src/
│   ├── main.py                    # Entry point
│   ├── redis_subscriber.py        # Redis connection and subscription logic
│   ├── firebase_client.py         # Firebase connection and data storage
├── Dockerfile                     # Docker build configuration
├── requirements.txt               # Python dependencies
```

### Redis Subscriber Implementation
- Connect to Redis using existing Redis utility modules from `main/utils/redis`
- Use either blocking subscription or pub/sub pattern depending on performance needs
- Implement backpressure handling for high message volume scenarios
- Log all received messages for debugging

### Firebase Client Implementation
- Connect to Firebase using Firebase Admin SDK
- Implement price data updates with change detection to minimize database writes
- Store current price data only, and order data indefinitely
- Implement reconnection and error handling logic

### Logging and Monitoring
- Comprehensive logging with configurable levels
- Structured logs for potential future analysis
- Key metrics to monitor:
  - Number of messages received
  - Message processing time
  - Firebase update latency
  - Connection status for both Redis and Firebase

## Future Considerations
- Splitting price and order data into separate channels for better performance
- Implementing data pruning strategies if storage becomes a concern
- Supporting additional bot types and data formats
- Adding authentication if security requirements change

## Next Steps
1. Set up the project structure
- We will create the bear minimum for this service where it can run


2. Implement Redis subscriber component
- We will create a new class that will subscribe to the redis channels and listen to the messages and log the messages for now to confirm it is working, we should be able to view the prices and the orders in the logs


3. Implement Firebase client integration
- We will create a new class that will connect to the firebase database and push the data to the database

4. Create Docker configuration
- We will create a dockerfile and update generate_compose.py to include our service

5. Document usage instructions
- We will create a README.md file to document how the service works




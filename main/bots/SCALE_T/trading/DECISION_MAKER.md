# DecisionMaker: Deep Dive

## Overview

The `DecisionMaker` class is the intelligence core of the SCALE_T trading bot, responsible for making real-time trading decisions based on market data and the trading strategy defined in CSV files. It implements an event-driven, reactive architecture that processes price updates and order status changes, deciding when to place buy and sell orders according to the grid trading strategy.

## Architecture

### Event-Driven Design

The `DecisionMaker` follows a producer-consumer pattern:

```
┌────────────────┐    ┌───────────────┐    ┌────────────────┐
│                │    │               │    │                │
│ Data Producers ├───►│ Action Queue  ├───►│ Event Consumer │
│                │    │               │    │                │
└────────────────┘    └───────────────┘    └────────────────┘
```

1. **Producers**: Threads that stream data from Alpaca APIs
   - `_price_update_producer`: Streams real-time price data
   - `_order_producer`: Streams order status updates

2. **Action Queue**: Thread-safe queue for event passing
   - Collects events from producer threads
   - Centralizes all events for processing

3. **Consumer**: Main processing loop (`consume_actions`)
   - Processes events in the order they arrive
   - Routes events to appropriate handlers

## Core Components and Methods

### Initialization

```python
def __init__(self, csv_service, alpaca_interface):
    # Initialize logger, services, and state variables
    # Recover any pending orders from previous runs
    # Get initial price and queue it for processing
```

During initialization, the `DecisionMaker`:
1. Sets up connections to the CSV service and Alpaca interface
2. Initializes the action queue and state tracking
3. Checks for any pending orders from previous runs
4. Validates share counts between Alpaca and the CSV data
5. Gets the initial price and queues it for processing

### Event Producer Threads

Two background threads continuously stream data into the action queue:

#### Price Update Producer

```python
def _run_price_producer(self):
    # Create a StockDataStream
    # Subscribe to price updates for the ticker
    # Add incoming prices to the action queue
```

- Uses Alpaca's stock data stream to receive real-time price updates
- Subscribes to the configured ticker symbol
- Pushes price updates to the action queue with type 'price_update'

#### Order Update Producer

```python
def _run_order_producer(self):
    # Create a TradingStream
    # Subscribe to order updates
    # Add incoming order updates to the action queue 
```

- Uses Alpaca's trading stream to receive order status updates
- Subscribes to all order updates for the account
- Pushes order updates to the action queue with type 'ORDER_UPDATE'

### Event Handlers

#### Price Update Handler

```python
def handle_price_update(self, price):
    # Filter redundant price updates
    # Check if we need to cancel any existing orders
    # Check if we should place sell orders
    # Check if we should place buy orders
```

When a price update is received, the handler:
1. Filters out duplicate prices to reduce processing load
2. Checks if any pending orders should be cancelled due to price movement
3. Checks if any rows in the CSV qualify for sell orders at the current price
4. Checks if any rows in the CSV qualify for buy orders at the current price

#### Order Update Handler

```python
def handle_order_update(self, order):
    # Verify this is for our pending order
    # Process based on order status
    # Update CSV with filled quantities and prices
    # Reset pending order state if completed
```

When an order update is received, the handler:
1. Verifies that the update matches the pending order ID
2. Processes the order based on its status (filled, canceled, etc.)
3. Updates the CSV data with filled quantities and prices
4. Resets the pending order state if the order is completed

### Trading Decision Logic

#### Buy Order Logic

```python
def _check_place_buy_order(self, current_price):
    # Get rows eligible for buying at current price
    # If rows found and no pending order, place a buy order
    # Update CSV with pending order ID
    # Return True if order placed, False otherwise
```

The buy order logic:
1. Identifies rows in the CSV where `buy_price >= current_price` and `held_shares < target_shares`
2. If eligible rows are found and no order is pending, places a buy order
3. Updates the CSV with the pending order ID
4. Sets the system state to `OrderState.BUYING`

#### Sell Order Logic

```python
def _check_place_sell_order(self, current_price):
    # Get rows eligible for selling at current price
    # If rows found and no pending order, place a sell order
    # Update CSV with pending order ID
    # Return True if order placed, False otherwise
```

The sell order logic:
1. Identifies rows in the CSV where `sell_price <= current_price` and `held_shares > 0`
2. If eligible rows are found and no order is pending, places a sell order
3. Updates the CSV with the pending order ID
4. Sets the system state to `OrderState.SELLING`

#### Cancel Order Logic

```python
def _check_cancel_order(self, current_price):
    # Check if there's a pending order that should be cancelled
    # For buy orders: cancel if price moved above buy price
    # For sell orders: cancel if price moved below sell price
    # Return True if cancelled, False otherwise
```

The cancel order logic:
1. Checks if there's a pending order that should be cancelled due to price movement
2. For buy orders: cancels if price moved above the buy price (unfavorable)
3. For sell orders: cancels if price moved below the sell price (unfavorable)
4. Sets the system state to `OrderState.CANCELLING` if a cancellation is triggered

### Main Event Loop

```python
def consume_actions(self):
    # Infinite loop to process events
    # Get events from the action queue
    # Route to appropriate handlers
```

The main event processing loop:
1. Continuously polls the action queue for new events
2. Routes events to the appropriate handlers based on type:
   - `price_update` events go to `handle_price_update`
   - `ORDER_UPDATE` events go to `handle_order_update`
3. After processing each event, marks it as done in the queue

### Manual Order Update Mechanism

```python
def _trigger_manual_order_update(self):
    # Check if enough time has passed since last update
    # If yes, manually check order status
    # Add order update to the queue
```

To prevent missed order updates:
1. Periodically checks if a manual order refresh is needed
2. If enough time has passed, requests order status directly from Alpaca
3. Creates a synthetic order update and adds it to the queue
4. This ensures the bot can recover from missed events

## State Management

The `DecisionMaker` maintains several key state variables:

1. `order_state`: Current state of the trading system (NONE, BUYING, SELLING, CANCELLING)
2. `pending_order`: Reference to any pending order being processed
3. `pending_order_index`: Index in the CSV where the pending order is tracked
4. `_prev_price`: Previous price processed, used to filter duplicate updates

## Data Flow for Key Operations

### Placing a Buy Order

1. Price update arrives via `_price_update_producer`
2. `handle_price_update` calls `_check_place_buy_order`
3. Eligible rows are identified and buy quantity is calculated
4. Order is placed via alpaca_interface
5. CSV is updated with pending order ID
6. State changes to `OrderState.BUYING`

### Filling a Buy Order

1. Order update arrives via `_order_producer`
2. `handle_order_update` processes the filled order
3. Filled shares are distributed to eligible rows in the CSV
4. Share allocation starts from lowest index (prioritizing lower price levels)
5. Unrealized profit is calculated for each row
6. Pending order state is cleared

### Placing a Sell Order

1. Price update arrives via `_price_update_producer`
2. `handle_price_update` calls `_check_place_sell_order`
3. Eligible rows are identified and sell quantity is calculated
4. Order is placed via alpaca_interface
5. CSV is updated with pending order ID
6. State changes to `OrderState.SELLING`

### Filling a Sell Order

1. Order update arrives via `_order_producer`
2. `handle_order_update` processes the filled order
3. Sold shares are removed from eligible rows in the CSV
4. Share deallocation starts from highest index (prioritizing higher price levels)
5. Realized profit is calculated and stored for each row
6. Pending order state is cleared

## Critical Implementation Details

### Thread Safety

The `DecisionMaker` handles concurrency with:
- Thread-safe queue for event passing
- State protection through the event loop
- Sequential processing of events
- Atomic state transitions for orders

### Price Filtering

To reduce processing overhead, price updates are filtered:
- Duplicate prices are ignored
- Prices are rounded to 2 decimal places
- This prevents excessive processing of high-frequency updates

### Order Validation

Before processing order updates:
1. Verifies the order ID matches the pending order
2. Checks that the order index exists in the CSV
3. Ensures order status is valid
4. This prevents processing incorrect or duplicate updates

### Error Recovery

Several mechanisms ensure robustness:
1. Share count validation on startup
2. Manual order update checks
3. State validation before order operations
4. Exception handling at critical points

## Advanced Features

### Fractional Share Handling

For buy orders with fractional shares:
- Creates market orders instead of limit orders
- Performs current price validation before placing
- Ensures favorable execution compared to limit price

### Profit Tracking

Sophisticated profit tracking:
- Unrealized profit tracked at position level
- Realized profit recorded on sells
- Profit properly distributed across price levels

## Integration Points

### CSV Service Integration

- Reads target prices and quantities from CSV
- Updates held shares and profit metrics
- Tracks pending order IDs
- Persists trading state between runs

### Alpaca Interface Integration

- Places buy and sell orders
- Receives real-time price data
- Streams order status updates
- Manages position reconciliation

## Performance Considerations

1. **Memory Efficiency**:
   - Only maintains references to necessary objects
   - Avoids storing large datasets in memory

2. **CPU Efficiency**:
   - Filters redundant price updates
   - Processes events sequentially
   - Uses background threads efficiently

3. **I/O Efficiency**:
   - Minimizes disk operations with strategic CSV updates
   - Uses streaming APIs for real-time data
   - Batches position updates when possible

## Summary

The `DecisionMaker` is a sophisticated event-driven trading system that:

1. Processes real-time market data from Alpaca
2. Implements a grid trading strategy defined in CSV files
3. Places buy and sell orders based on price movements
4. Manages order lifecycles through completion
5. Tracks positions and profits across price levels
6. Recovers gracefully from errors and interruptions

Its event-driven architecture ensures responsive trading while maintaining state consistency, making it the central intelligence component of the SCALE_T trading bot.

# SCALE_T Trading Module

## Overview

The `trading` module is the central decision-making component of the SCALE_T trading bot. It processes real-time market data, determines when to place buy and sell orders based on the CSV configuration, and manages order lifecycle through completion.

## Components

### `DecisionMaker` (decision_maker.py)

The core trading intelligence of the SCALE_T bot that:

- Consumes real-time price and order update events via Alpaca's streaming API
- Orchestrates the trading strategy based on price movements
- Implements a non-blocking, event-driven architecture using queues
- Handles order state transitions and updates the CSV data accordingly

```python
from main.bots.SCALE_T.trading.decision_maker import DecisionMaker
from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface

# Initialize dependencies
csv_service = CSVService("AAPL", TradingType.PAPER)
alpaca = AlpacaInterface(trading_type="paper", ticker="AAPL")

# Create decision maker
decision_maker = DecisionMaker(csv_service, alpaca)

# Start processing events
decision_maker.launch_action_producer_threads()
decision_maker.consume_actions()  # This blocks and processes events continuously
```

### Trading Constants (constants.py)

Defines key enumerations used by the trading module:

- `MessageType`: Types of messages that can be processed by the decision maker
  - `PRICE_UPDATE`: Real-time price updates
  - `ORDER_UPDATE`: Order status changes

- `OrderState`: Current state of the trading system
  - `NONE`: No active orders
  - `BUYING`: Currently executing a buy order
  - `SELLING`: Currently executing a sell order
  - `CANCELLING`: In the process of cancelling an order

## Architecture

The trading module follows an event-driven architecture:

1. **Event Producers**:
   - `_price_update_producer`: Streams real-time price data
   - `_pending_order_update_producer`: Streams order updates

2. **Event Consumer**:
   - `consume_actions`: Central event loop that processes all events

3. **Event Handlers**:
   - `handle_price_update`: Processes price changes
   - `handle_order_update`: Processes order status updates

4. **Trading Logic**:
   - `_check_place_buy_order`: Determines when to place buy orders
   - `_check_place_sell_order`: Determines when to place sell orders
   - `_check_cancel_order`: Determines when to cancel existing orders

## Workflow

1. **Initialization**:
   - The `DecisionMaker` loads the current state from the CSV
   - Verifies position sizes match between Alpaca and local data
   - Initializes any pending orders from previous runs

2. **Real-time Data Processing**:
   - Price updates trigger evaluation of buy/sell conditions
   - Order updates are processed to update CSV state
   - Automatic order tracking and reconciliation occurs

3. **Trading Decisions**:
   - Buy orders are placed when current price ≤ buy price in CSV
   - Sell orders are placed when current price ≥ sell price in CSV
   - Orders are cancelled if price moves unfavorably before fill

4. **Position Management**:
   - For buy orders: Shares are distributed by price level, starting from lowest index
   - For sell orders: Shares are distributed by price level, starting from highest index
   - Profit/loss is tracked at each price level

## Integration Points

The trading module integrates with:

1. **CSV Service**:
   - Reads trading parameters from CSV files
   - Updates share allocations and profit tracking
   - Maintains order state in persistent storage

2. **Alpaca Interface**:
   - Executes trades through Alpaca's API
   - Receives real-time data through Alpaca's streaming API
   - Tracks order status and position information

## Error Handling

The `DecisionMaker` includes robust error handling:

- Share count validation to ensure CSV and broker positions match
- Order ID validation to prevent duplicate or mismatched order processing
- Periodic manual checks to catch any missed order updates
- Logging of all significant events and error conditions

## Best Practices

1. Always initialize components in this order:
   - CSV Service (strategy configuration)
   - Alpaca Interface (brokerage connection)
   - Decision Maker (trading intelligence)

2. Let the decision maker manage all order placement and cancellation:
   - Never place orders directly through the Alpaca interface
   - Don't modify CSV data while trading is active

3. Monitor logs for action sequencing:
   - Price updates should appear frequently
   - Order updates indicate trading activity
   - Error messages require immediate attention

## Thread Safety

The `DecisionMaker` uses threading to handle multiple data streams:

- The main thread runs `consume_actions` to process all events
- Background threads produce events from Alpaca's streaming APIs
- `action_queue` safely transfers data between threads

## Extending the Trading Module

When extending the trading logic:

1. Maintain the event-driven architecture
2. Add new message types to `MessageType` enum
3. Add appropriate handlers for new message types
4. Keep trading logic separate from brokerage-specific code
5. Update decision-making code (`_check_place_buy_order`, etc.) for new strategy elements

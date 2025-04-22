#!/usr/bin/env python
"""
Test script demonstrating dynamic ticker channels and registration.

This script shows:
1. How a bot registers with the broker for a specific ticker.
2. How the broker (simulated here by another publisher) publishes
   price and order updates to the ticker-specific channel.
3. How a subscriber listens to a specific ticker channel.
"""

import sys
import os
import json
import logging
import time
import threading

# Add the project root to the path so we can import utils
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our Redis library components
from main.utils.redis import (
    CHANNELS,
    MESSAGE_SCHEMAS, # Keep for registration schema
    RedisPublisher,
    RedisSubscriber,
    validate_message,
    MessageValidationError
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RedisExample")

# --- Handlers ---
def ticker_update_handler(message):
    """Handles messages received on a dynamic ticker channel."""
    logger.info(f"Received Ticker Update: Channel='{message.get('channel')}'")
    try:
        data = message.get('data', '{}') # Data is expected as JSON
        msg_type = data.get('type')
        symbol = data.get('symbol') # Symbol should be in the payload now
        timestamp = data.get('timestamp')

        logger.info(f"  -> Type: {msg_type}, Symbol: {symbol}, Timestamp: {timestamp}")

        if msg_type == 'price':
            logger.info(f"     Price: {data.get('price')}, Volume: {data.get('volume')}")
        elif msg_type == 'order':
            order_data = data.get('order_data', {})
            logger.info(f"     Order Event: {order_data.get('event')}, Order ID: {order_data.get('order', {}).get('id')}, Status: {order_data.get('order', {}).get('status')}")
        else:
            logger.warning(f"     Unknown message type in ticker channel: {msg_type}")

    except json.JSONDecodeError:
        logger.error(f"  -> Failed to decode JSON data: {message.get('data')}")
    except Exception as e:
        logger.error(f"  -> Error processing ticker update: {e}")

def registration_handler(message):
    """Simulates broker handling registration messages (for logging only)."""
    logger.info(f"Received Registration Message: Channel='{message.get('channel')}'")
    try:
        data = message.get('data', '{}')
        logger.info(f"  -> Action: {data.get('action')}, Ticker: {data.get('ticker')}, Sender: {data.get('sender')}")
    except json.JSONDecodeError:
        logger.error(f"  -> Failed to decode JSON data: {message.get('data')}")

# --- Test Functions ---

def simulate_bot_registration(publisher: RedisPublisher, ticker: str, action: str):
    """Simulates a bot sending a registration message."""
    registration_channel = CHANNELS.BROKER_REGISTRATION
    message_data = {"action": action, "ticker": ticker}
    logger.info(f"BOT: Sending '{action}' request for ticker '{ticker}' to channel '{registration_channel}'")
    try:
        # Use the standard publish which expects a dict
        publisher.publish(registration_channel, message_data, sender=f"bot_{ticker}")
    except MessageValidationError as e:
        logger.error(f"BOT: Failed to send registration message: {e}")

def simulate_broker_publishing(publisher: RedisPublisher, ticker: str):
    """Simulates the broker publishing updates to a ticker channel."""
    ticker_channel = CHANNELS.get_ticker_channel(ticker)
    logger.info(f"BROKER: Publishing updates to channel '{ticker_channel}'")

    # Publish a price update
    price_update = {
        "type": "price",
        "timestamp": str(time.time()),
        "symbol": ticker,
        "price": round(150.0 + time.time() % 10, 2), # Simulate changing price
        "volume": 1000 + int(time.time() % 100)
    }
    try:
        # Use standard publish, assuming wrapper handles schema lookup/validation
        publisher.publish(ticker_channel, price_update, sender="alpaca_broker")
    except MessageValidationError as e:
         logger.error(f"BROKER: Failed to publish price update: {e}")

    time.sleep(0.5)

    # Publish an order update
    order_update_data = { # Simulating the structure broker creates
         "event": "fill",
         "execution_id": f"exec_{int(time.time())}",
         "order": {
             "id": f"order_{int(time.time())}",
             "symbol": ticker,
             "status": "filled",
             # Add other necessary fields based on schema if needed
             "asset_class": "us_equity",
             "order_class": "simple",
             "order_type": "market",
             "side": "buy",
             "time_in_force": "day",
             "created_at": str(time.time()),
             "updated_at": str(time.time()),
             "submitted_at": str(time.time()),
             "filled_at": str(time.time()),
             "qty": "10",
             "filled_qty": "10",
             "filled_avg_price": str(price_update["price"]) # Use recent price
         },
         "timestamp": str(time.time()),
         "position_qty": "10",
         "price": str(price_update["price"]),
         "qty": "10",
     }
    order_message = {
        "type": "order",
        "timestamp": str(time.time()),
        "symbol": ticker,
        "order_data": order_update_data
    }
    try:
        publisher.publish(ticker_channel, order_message, sender="alpaca_broker")
    except MessageValidationError as e:
         logger.error(f"BROKER: Failed to publish order update: {e}")


def test_dynamic_channels():
    """Tests registration and dynamic channel pub/sub."""
    logger.info("--- Testing Dynamic Channel Workflow ---")

    # Publisher (used by both bot simulation and broker simulation)
    publisher = RedisPublisher(host='localhost', port=6379)

    # Subscriber (simulates a component listening to ticker updates)
    ticker_subscriber = RedisSubscriber(host='localhost', port=6379)

    # Subscriber (simulates the broker listening for registrations)
    registration_subscriber = RedisSubscriber(host='localhost', port=6379)
    registration_subscriber.subscribe(CHANNELS.BROKER_REGISTRATION, registration_handler)
    registration_subscriber.start_listening()
    logger.info(f"BROKER SIM: Listening on '{CHANNELS.BROKER_REGISTRATION}'")

    time.sleep(1) # Allow subscriber setup

    # 1. Bot registers for AAPL
    simulate_bot_registration(publisher, "AAPL", "subscribe")
    time.sleep(1) # Give broker time to process (in real scenario)

    # 2. Ticker Subscriber starts listening to the dynamic AAPL channel
    aapl_channel = CHANNELS.get_ticker_channel("AAPL")
    ticker_subscriber.subscribe(aapl_channel, ticker_update_handler)
    ticker_subscriber.start_listening()
    logger.info(f"TICKER LISTENER: Subscribed to '{aapl_channel}'")
    time.sleep(1)

    # 3. Broker starts publishing AAPL updates (simulated)
    simulate_broker_publishing(publisher, "AAPL")
    time.sleep(2) # Allow time for messages to be received

    # 4. Bot registers for MSFT
    simulate_bot_registration(publisher, "MSFT", "subscribe")
    time.sleep(1)

    # 5. Ticker Subscriber also listens to MSFT channel
    msft_channel = CHANNELS.get_ticker_channel("MSFT")
    ticker_subscriber.subscribe(msft_channel, ticker_update_handler)
    logger.info(f"TICKER LISTENER: Subscribed to '{msft_channel}'")
    time.sleep(1)

    # 6. Broker publishes MSFT updates (simulated)
    simulate_broker_publishing(publisher, "MSFT")
    time.sleep(2)

    # 7. Bot unsubscribes from AAPL
    simulate_bot_registration(publisher, "AAPL", "unsubscribe")
    time.sleep(1)
    # In a real scenario, the broker would stop publishing to AAPL channel
    # or the listener would unsubscribe if it no longer needs it.
    # For this example, we just simulate the request.
    logger.info("BOT: Sent unsubscribe for AAPL (Broker simulation would stop publishing)")


    # Cleanup
    logger.info("Cleaning up...")
    registration_subscriber.close()
    ticker_subscriber.close()
    publisher.close()
    logger.info("Connections closed.")

def main():
    """Run the dynamic channel test."""
    test_dynamic_channels()

if __name__ == "__main__":
    main()

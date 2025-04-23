#!/usr/bin/env python
"""
Test script for Redis library components using dynamic ticker channels.

This script demonstrates:
1. Publishing price updates to a dynamic ticker-specific channel.
2. Subscribing to that dynamic channel to receive updates.
"""

import time
import sys
import os
import json
import threading
import logging

# Add the project root to the path so we can import utils
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our Redis library components
from main.utils.redis import RedisConnection, RedisPublisher, RedisSubscriber, CHANNELS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TEST_TICKER = "AAPL" # Define the ticker for this test

def ticker_update_handler(message):
    """
    Handler for messages on the dynamic ticker channel.
    """
    logger.info(f"Received Ticker Update: Channel='{message.get('channel')}'")
    try:
        data = message.get('data', '{}') # Data is expected as JSON string
        msg_type = data.get('type')
        symbol = data.get('symbol')
        timestamp = data.get('timestamp')

        logger.info(f"  -> Type: {msg_type}, Symbol: {symbol}, Timestamp: {timestamp}")

        if msg_type == 'price':
            logger.info(f"     Price: {data.get('price')}, Volume: {data.get('volume')}")
        elif msg_type == 'order':
            # Basic logging for order data if received
            order_data = data.get('order_data', {})
            logger.info(f"     Order Event: {order_data.get('event')}, Order ID: {order_data.get('order', {}).get('id')}")
        else:
            logger.warning(f"     Unknown message type: {msg_type}")

    except json.JSONDecodeError:
        logger.error(f"  -> Failed to decode JSON data: {message.get('data')}")
    except Exception as e:
        logger.error(f"  -> Error processing ticker update: {e}")


def run_publisher():
    """Run a publisher that sends sample price data to a dynamic channel."""
    try:
        logger.info("Starting publisher...")
        publisher = RedisPublisher(host='localhost', port=6379, db=0)
        ticker_channel = CHANNELS.get_ticker_channel(TEST_TICKER)

        # Send 5 price updates
        for i in range(5):
            price_data = {
                'type': 'price', # Add type field for combined schema
                'timestamp': str(time.time()),
                'symbol': TEST_TICKER,
                'price': round(150.0 + i, 2),
                'volume': 1000 + (i * 100)
            }
            # price_data_json_str = json.dumps(price_data)

            # Publish message to the dynamic ticker channel
            publisher.publish(
                ticker_channel, # Use dynamic channel name
                price_data,
                sender='test_redis_lib' # Removed message_type argument
            )

            logger.info(f"Published price update {i+1}/5 to {ticker_channel}")
            time.sleep(1)

        publisher.close()
        logger.info("Publisher finished")
    except Exception as e:
        logger.error(f"Publisher error: {e}")

def run_subscriber():
    """Run a subscriber that listens to a dynamic ticker channel."""
    try:
        logger.info("Starting subscriber...")
        subscriber = RedisSubscriber(host='localhost', port=6379, db=0)
        ticker_channel = CHANNELS.get_ticker_channel(TEST_TICKER)

        # Subscribe to the dynamic ticker channel with our handler
        subscriber.subscribe(ticker_channel, ticker_update_handler)

        # Start listening for messages (non-blocking)
        subscriber.start_listening()

        # Keep the subscriber running for a while
        logger.info(f"Subscriber listening for messages on {ticker_channel}...")
        time.sleep(10) # Keep listening longer to catch all messages

        # Clean up
        subscriber.close()
        logger.info("Subscriber closed")
    except Exception as e:
        logger.error(f"Subscriber error: {e}")

def test_connection():
    """Test basic connection functionality."""
    try:
        logger.info("Testing connection...")
        connection = RedisConnection(host='localhost', port=6379, db=0)
        redis_conn = connection.connection
        result = redis_conn.ping()
        logger.info(f"Connection ping result: {result}")
        connection.disconnect()
        logger.info("Connection test successful")
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def main():
    """Run a complete test of the Redis library components with dynamic channels."""
    logger.info("Starting Redis library dynamic channel test")

    if not test_connection():
        logger.error("Connection test failed, aborting further tests")
        return

    # Start the subscriber in a separate thread
    subscriber_thread = threading.Thread(target=run_subscriber)
    subscriber_thread.start()

    # Wait a moment for the subscriber to start
    time.sleep(2)

    # Run the publisher in the main thread
    run_publisher()

    # Wait for the subscriber to finish
    subscriber_thread.join()

    logger.info("Redis library dynamic channel test completed")

if __name__ == "__main__":
    main()

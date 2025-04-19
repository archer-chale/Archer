#!/usr/bin/env python
"""
Test script for Redis library components.

This script demonstrates how to use the RedisConnection, RedisPublisher, and RedisSubscriber
classes together to implement a simple pub/sub system.
"""

import time
import sys
import os
import json
import threading
import logging

# Add the parent directory to the path so we can import our Redis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import our Redis library components
from utils.redis import RedisConnection, RedisPublisher, RedisSubscriber, CHANNELS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def price_handler(message):
    """
    Handler for price update messages.
    
    Args:
        message (dict): The parsed JSON message.
    """
    logger.info(f"Received price update: {json.dumps(message, indent=2)}")
    logger.info(f"Symbol: {message['data'].get('symbol')}, Price: {message['data'].get('price')}")

def run_publisher():
    """Run a publisher that sends sample price data."""
    try:
        # Create a publisher
        logger.info("Starting publisher...")
        publisher = RedisPublisher(host='localhost', port=6379, db=0)
        
        # Send 5 price updates
        for i in range(5):
            price_data = {
                'symbol': 'AAPL',
                'price': 150.00 + i,
                'volume': 1000 + (i * 100)
            }
            
            # Publish message to the PRICE_DATA channel
            publisher.publish(
                CHANNELS.PRICE_DATA,
                price_data,
                message_type='price_update',
                sender='test_redis_lib'
            )
            
            logger.info(f"Published price update {i+1}/5")
            time.sleep(1)
            
        publisher.close()
        logger.info("Publisher finished")
    except Exception as e:
        logger.error(f"Publisher error: {e}")

def run_subscriber():
    """Run a subscriber that listens for price data."""
    try:
        # Create a subscriber
        logger.info("Starting subscriber...")
        subscriber = RedisSubscriber(host='localhost', port=6379, db=0)
        
        # Subscribe to the PRICE_DATA channel with our price_handler callback
        subscriber.subscribe(CHANNELS.PRICE_DATA, price_handler, message_types=['price_update'])
        
        # Start listening for messages (non-blocking)
        subscriber.start_listening()
        
        # Keep the subscriber running for a while
        logger.info("Subscriber listening for messages...")
        time.sleep(10)
        
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
        
        # Get the connection
        redis_conn = connection.connection
        
        # Test a simple command
        result = redis_conn.ping()
        logger.info(f"Connection ping result: {result}")
        
        # Close the connection
        connection.disconnect()
        logger.info("Connection test successful")
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def main():
    """Run a complete test of the Redis library components."""
    logger.info("Starting Redis library test")
    
    # First, test the connection
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
    
    logger.info("Redis library test completed")

if __name__ == "__main__":
    main()

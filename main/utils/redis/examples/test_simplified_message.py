#!/usr/bin/env python
"""
Test script for the simplified message handling approach.

This script demonstrates how the channel-specific message validation works
and how it enforces the correct message structure for each channel.
"""

import sys
import os
import json
import logging
import time

# Add the parent directory to the path so we can import our Redis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import our Redis library components
from utils.redis import (
    CHANNELS, 
    MESSAGE_SCHEMAS,
    RedisPublisher, 
    RedisSubscriber,
    validate_message,
    MessageValidationError
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_price_schema_validation():
    """Test the validation of price data messages against the schema."""
    logger.info("Testing price data message validation")
    
    # Valid price message
    valid_price = {
        "symbol": "AAPL",
        "price": 150.00,
        "volume": 1000
    }
    
    # Invalid price messages
    invalid_tests = [
        # Missing required field (price)
        {"symbol": "AAPL"},
        
        # Wrong type for price
        {"symbol": "AAPL", "price": "not_a_number"},
        
        # Wrong type for symbol
        {"symbol": 123, "price": 150.00}
    ]
    
    # Test valid message
    try:
        validate_message(CHANNELS.PRICE_DATA, valid_price)
        logger.info("✅ Valid price message passed validation")
    except MessageValidationError as e:
        logger.error(f"❌ Valid price message failed validation: {e}")
    
    # Test invalid messages
    for i, invalid_msg in enumerate(invalid_tests):
        try:
            validate_message(CHANNELS.PRICE_DATA, invalid_msg)
            logger.error(f"❌ Invalid message {i+1} should have failed validation but passed")
        except MessageValidationError as e:
            logger.info(f"✅ Invalid message {i+1} correctly failed validation: {e}")

def price_handler(message):
    """Handler function for price data messages."""
    logger.info(f"Received price message: {json.dumps(message, indent=2)}")
    
    # Access the data directly as expected for this channel
    data = message["data"]
    logger.info(f"Symbol: {data['symbol']}, Price: {data['price']}")
    
    if "volume" in data:
        logger.info(f"Volume: {data['volume']}")

def test_publish_subscribe():
    """Test actual publishing and subscribing with the simplified message approach."""
    logger.info("Testing publish/subscribe with channel-specific message format")
    
    # Start a subscriber
    subscriber = RedisSubscriber(host='localhost', port=6379)
    subscriber.subscribe(CHANNELS.PRICE_DATA, price_handler)
    subscriber.start_listening()
    logger.info("Started subscriber listening for price data")
    
    # Wait a moment for subscription to be ready
    time.sleep(1)
    
    # Create a publisher
    publisher = RedisPublisher(host='localhost', port=6379)
    
    # Publish a valid price message
    price_data = {
        "symbol": "AAPL",
        "price": 150.00,
        "volume": 1000
    }
    
    logger.info("Publishing price message")
    publisher.publish(CHANNELS.PRICE_DATA, price_data, sender="test_script")
    
    # Wait a moment to see the response
    time.sleep(2)
    
    # Try to publish an invalid message (should raise an exception)
    try:
        invalid_data = {
            "symbol": "AAPL",
            # Missing required 'price' field
        }
        publisher.publish(CHANNELS.PRICE_DATA, invalid_data)
        logger.error("❌ Invalid message should have failed validation but was published")
    except MessageValidationError as e:
        logger.info(f"✅ Invalid message correctly failed validation: {e}")
    
    # Clean up connections
    subscriber.close()
    publisher.close()
    logger.info("Cleaned up connections")

def main():
    """Run all the tests."""
    logger.info("Starting simplified message handling tests")
    
    # First, test schema validation
    test_price_schema_validation()
    
    # Then test actual pub/sub with message validation
    test_publish_subscribe()
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()

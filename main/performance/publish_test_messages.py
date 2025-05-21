#!/usr/bin/env python
"""
Test script to manually publish performance and price messages to Redis channels
for debugging the Firebase client issues.
"""
import sys
import os
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("test_publisher")

# Add the parent directory to the path so we can import our Redis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Redis publisher and channel definitions
from main.utils.redis import RedisPublisher, CHANNELS

def publish_performance_message(symbol: str, publisher: RedisPublisher) -> None:
    """Publish a test performance message for a ticker"""
    try:
        # Create the performance channel
        channel = CHANNELS.get_ticker_performance_channel(symbol)
        logger.info(f"Publishing performance update to channel: {channel}")
        
        # Create performance data
        performance_data = {
            "symbol": symbol,
            "total": "100.50",
            "unrealized": "75.25",
            "realized": "25.25",
            "converted": "0.00",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish to Redis
        publisher.publish(
            channel=channel,
            message_data=performance_data,
            sender='test_performance_publisher'
        )
        logger.info(f"Published performance data for {symbol}: {json.dumps(performance_data, indent=2)}")
        
        # Also publish to aggregate channel if requested
        if args.aggregate:
            aggregate_channel = CHANNELS.get_ticker_performance_channel("AGGREGATE")
            publisher.publish(
                channel=aggregate_channel,
                message_data=performance_data,
                sender='test_performance_publisher'
            )
            logger.info(f"Published to aggregate channel: {aggregate_channel}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error publishing performance data: {e}")
        return False

def publish_price_message(symbol: str, publisher: RedisPublisher) -> None:
    """Publish a test price message for a ticker"""
    try:
        # Create the price channel
        channel = CHANNELS.get_ticker_channel(symbol)
        logger.info(f"Publishing price update to channel: {channel}")
        
        # Create price data
        price_data = {
            "symbol": symbol,
            "price": "350.75",
            "volume": "10000",
            "type": "price",  # Required field for the message schema
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish to Redis
        publisher.publish(
            channel=channel,
            message_data=price_data,
            sender='test_price_publisher'
        )
        logger.info(f"Published price data for {symbol}: {json.dumps(price_data, indent=2)}")
        return True
        
    except Exception as e:
        logger.error(f"Error publishing price data: {e}")
        return False

def publish_order_message(symbol: str, publisher: RedisPublisher) -> None:
    """Publish a test order message for a ticker"""
    try:
        # Create the order channel (same as price channel)
        channel = CHANNELS.get_ticker_channel(symbol)
        logger.info(f"Publishing order update to channel: {channel}")
        
        # Create an order message
        order_data = {
            "symbol": symbol,
            "type": "order",  # Required field for the message schema
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "order_data": {  # Sample order data structure
                "event": "fill",
                "execution_id": "test-execution-id",
                "order": {
                    "id": "test-order-id",
                    "client_order_id": "test-client-order",
                    "symbol": symbol,
                    "qty": "1",
                    "filled_qty": "1",
                    "filled_avg_price": "350.75",
                    "status": "filled"
                },
                "price": "350.75",
                "qty": "1.0",
                "position_qty": "1.0"
            }
        }
        
        # Publish to Redis
        publisher.publish(
            channel=channel,
            message_data=order_data,
            sender='test_order_publisher'
        )
        logger.info(f"Published order data for {symbol}: Order ID: test-order-id")
        return True
        
    except Exception as e:
        logger.error(f"Error publishing order data: {e}")
        return False

def publish_empty_channel_message(publisher: RedisPublisher) -> None:
    """
    Publish a message with an empty channel to test the error handling
    This is to help debug the 'unknown channel' warnings
    """
    try:
        logger.info("Publishing message with empty channel for testing error handling")
        
        # Testing with empty channel
        data = {"test": "data"}
        publisher.publish("", data, sender='test_publisher')
        logger.info("Published message with empty channel")
        
        # Test with None channel
        try:
            publisher.publish(None, data, sender='test_publisher')
            logger.info("Published message with None channel")
        except Exception as e:
            logger.error(f"Error publishing with None channel (expected): {e}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error in empty channel test: {e}")
        return False

def publish_custom_message(channel: str, publisher: RedisPublisher, data: Dict[str, Any]) -> None:
    """Publish a custom message to a specified channel"""
    try:
        logger.info(f"Publishing custom message to channel: {channel}")
        
        # Publish to Redis
        publisher.publish(
            channel=channel,
            message_data=data,
            sender='test_custom_publisher'
        )
        logger.info(f"Published custom data to {channel}: {json.dumps(data, indent=2)}")
        return True
        
    except Exception as e:
        logger.error(f"Error publishing custom data: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test publisher for Redis messaging")
    parser.add_argument("--symbol", type=str, default="TSLA", 
                      help="Symbol to use for test messages (default: TSLA)")
    parser.add_argument("--performance", action="store_true", 
                      help="Publish a performance message")
    parser.add_argument("--price", action="store_true", 
                      help="Publish a price message")
    parser.add_argument("--order", action="store_true", 
                      help="Publish an order message")
    parser.add_argument("--empty", action="store_true", 
                      help="Test publishing with an empty channel")
    parser.add_argument("--aggregate", action="store_true", 
                      help="Also publish to the aggregate performance channel")
    parser.add_argument("--custom-channel", type=str, 
                      help="Custom channel to publish to")
    parser.add_argument("--custom-data", type=str, 
                      help="Custom JSON data to publish (as a string)")
    parser.add_argument("--count", type=int, default=1, 
                      help="Number of messages to send (default: 1)")
    parser.add_argument("--delay", type=float, default=1.0, 
                      help="Delay between messages in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    # Create the publisher
    publisher = RedisPublisher()
    
    # Process command line arguments
    for i in range(args.count):
        if i > 0:
            logger.info(f"Waiting {args.delay} seconds before sending next message...")
            time.sleep(args.delay)
            
        if args.performance:
            publish_performance_message(args.symbol, publisher)
            
        if args.price:
            publish_price_message(args.symbol, publisher)
            
        if args.order:
            publish_order_message(args.symbol, publisher)
            
        if args.empty:
            publish_empty_channel_message(publisher)
            
        if args.custom_channel and args.custom_data:
            try:
                custom_data = json.loads(args.custom_data)
                publish_custom_message(args.custom_channel, publisher, custom_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in custom-data: {args.custom_data}")
    
    # Clean up
    publisher.close()
    logger.info("Test publisher closed")

# python publish_test_messages.py --symbol TSLA --performance
# python publish_test_messages.py --symbol TSLA --price
# python publish_test_messages.py --symbol TSLA --order
# python publish_test_messages.py --empty
# python publish_test_messages.py --symbol TSLA --performance --price --count 3 --delay 2

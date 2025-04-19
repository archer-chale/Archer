#!/usr/bin/env python
# Test Subscriber for Redis Pub/Sub using our Redis library
import sys
import os
import json
import time

# Add the parent directory to the path so we can import our Redis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import our Redis library components
from utils.redis import RedisSubscriber, CHANNELS

def price_handler(message):
    """Handle price update messages"""
    # With our library, the message is already parsed from JSON
    # and has a consistent structure
    data = message["data"]
    timestamp = message["timestamp"]
    sender = message["sender"]
    
    print("\n" + "=" * 50)
    print(f"Received price update from {sender} at {timestamp}")
    print(f"Symbol: {data['symbol']}")
    print(f"Price: ${data['price']:.2f}")
    if "volume" in data:
        print(f"Volume: {data['volume']}")
    print("=" * 50)

def main():
    print("Starting Redis Subscriber Test")
    print(f"Listening for price updates on channel: {CHANNELS.PRICE_DATA}")
    
    # Create a subscriber using our library
    subscriber = RedisSubscriber()
    
    # Subscribe to the price data channel with our handler
    subscriber.subscribe(CHANNELS.PRICE_DATA, price_handler)
    
    # Start listening for messages
    subscriber.start_listening()
    
    print("Subscriber is running. Press Ctrl+C to exit.")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down subscriber...")
    finally:
        # Clean up
        subscriber.close()
        print("Subscriber has been closed.")

if __name__ == "__main__":
    main()

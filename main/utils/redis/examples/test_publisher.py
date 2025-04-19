#!/usr/bin/env python
# Test Publisher for Redis Pub/Sub using our Redis library
import sys
import os
import time
import json

# Add the parent directory to the path so we can import our Redis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import our Redis library components
from utils.redis import RedisPublisher, CHANNELS

def main():
    print("Starting Redis Publisher Test")
    print(f"Will publish price updates to channel: {CHANNELS.PRICE_DATA}")
    
    # Create a publisher using our library
    publisher = RedisPublisher(host="redis")
    
    # Send 10 test price messages
    for i in range(10):
        # Create price data
        price_data = {
            'symbol': 'AAPL',
            'price': 150.00 + i,
            'volume': 1000 + (i * 100)
        }
        
        # Publish message using our library
        # Note how we don't need to handle JSON conversion or message structure
        publisher.publish(CHANNELS.PRICE_DATA, price_data, sender='test_publisher')
        
        # Print the message we sent
        print(f"Published price update {i+1}/10: Symbol={price_data['symbol']}, "
              f"Price=${price_data['price']:.2f}, Volume={price_data['volume']}")
        
        # Wait a second between messages
        time.sleep(1)
    
    # Clean up
    publisher.close()
    print("\nAll messages published successfully!")

if __name__ == "__main__":
    main()

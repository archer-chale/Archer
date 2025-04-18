#!/usr/bin/env python
# Test Publisher for Redis Pub/Sub
import redis
import json
import time
import datetime

def main():
    # Connect to Redis server
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Channel name
    channel = 'PRICE_DATA'
    
    # Send 5 test messages
    for i in range(5):
        # Create a message with timestamp
        message = {
            'message_type': 'price_update',
            'data': {
                'symbol': 'AAPL',
                'price': 150.00 + i,
                'volume': 1000 + (i * 100)
            },
            'timestamp': datetime.datetime.now().isoformat(),
            'sender': 'test_publisher'
        }
        
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Publish message
        r.publish(channel, message_json)
        print(f"Published message {i+1} to {channel}: {message_json}")
        
        # Wait a second between messages
        time.sleep(1)
    
    print("All messages published successfully!")

if __name__ == "__main__":
    main()

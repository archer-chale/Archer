#!/usr/bin/env python
# Test Subscriber for Redis Pub/Sub
import redis
import json
import time

def message_handler(message):
    """Process incoming messages"""
    # Decode the message data
    data = message['data'].decode('utf-8')
    channel = message['channel'].decode('utf-8')
    
    # Parse JSON
    try:
        json_data = json.loads(data)
        print(f"\nReceived message on channel '{channel}':")
        print(f"Type: {json_data.get('message_type')}")
        print(f"Data: {json_data.get('data')}")
        print(f"Timestamp: {json_data.get('timestamp')}")
        print(f"Sender: {json_data.get('sender')}")
        print("-" * 50)
    except json.JSONDecodeError:
        print(f"Received non-JSON message on channel '{channel}': {data}")

def main():
    # Connect to Redis server
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Create a pubsub object
    pubsub = r.pubsub()
    
    # Channel to subscribe to
    channel = 'PRICE_DATA'
    
    # Subscribe to the channel
    pubsub.subscribe(**{channel: message_handler})
    
    print(f"Subscribed to channel: {channel}")
    print("Waiting for messages... (press Ctrl+C to exit)")
    
    # Start the message processing loop
    try:
        pubsub.run_in_thread(sleep_time=0.001)
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Clean up
        pubsub.unsubscribe()
        pubsub.close()

if __name__ == "__main__":
    main()

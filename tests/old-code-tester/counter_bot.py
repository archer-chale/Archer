import logging
import time
import json

# Import our Redis library components
from main.utils.redis import RedisSubscriber, CHANNELS

def run_price_subscriber(service_id):
    """
    Run a price subscriber service that listens for price updates via Redis.
    
    Args:
        service_id: Unique ID for this service instance
    """
    logging.info(f"Starting price subscriber service {service_id}...")
    
    # Define a handler for Redis price updates
    def price_update_handler(message):
        """
        Handle price updates received from Redis.
        
        Args:
            message: Dictionary containing the message data
        """
        data = message.get('data', {})
        timestamp = message.get('timestamp', '')
        sender = message.get('sender', 'unknown')
        
        # Extract price data
        symbol = data.get('symbol', 'unknown')
        price = data.get('price', 0.0)
        volume = data.get('volume', 0)
        
        logging.info(f"PRICE UPDATE - Symbol: {symbol}, Price: ${price:.2f}, Volume: {volume}")
        logging.info(f"               From: {sender} at {timestamp}")
        logging.info(f"               Service: {service_id}")
    
    # Initialize our Redis subscriber for price updates
    logging.info(f"Initializing Redis subscriber for service {service_id}...")
    
    redis_subscriber = RedisSubscriber()
    
    try:
        # Subscribe to the price data channel
        redis_subscriber.subscribe(CHANNELS.PRICE_DATA, price_update_handler)
        logging.info(f"Subscribed to Redis price updates on channel: {CHANNELS.PRICE_DATA}")
        
        # Start listening for messages
        redis_subscriber.start_listening()
        logging.info("Listening for price updates...")
        
        # Keep the service running
        try:
            while True:
                # Just keep the service alive
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info(f"Price subscriber service {service_id} interrupted and stopping.")
    
    except Exception as e:
        logging.error(f"Error in price subscriber: {e}")
    
    finally:
        # Ensure we close the subscriber even if an error occurs
        if 'redis_subscriber' in locals():
            redis_subscriber.close()
            logging.info("Closed Redis subscriber")
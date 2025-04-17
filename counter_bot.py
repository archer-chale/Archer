import logging
import time
import json
from firebase_client import update_bot_count
from message_firebase_client import MessageFirebaseClient

def run_counter_bot(service_id, ticker, bot_id):
    """
    Run a counter bot service that:
    1. Increments a counter every second
    2. Updates the counter value in Firebase every 10 seconds
    3. Listens for configuration messages that can reset the counter
    
    Args:
        service_id: Unique ID for this service instance
        ticker: Stock ticker symbol this bot is monitoring
        bot_id: Unique ID for this bot
    """
    counter = 0
    last_update = 0
    logging.info(f"Starting counter bot for service {service_id}...")
    
    # Define the callback function for processing messages
    def process_message(message_id, message_data):
        """
        Process configuration messages received from Firestore.
        This callback is called whenever a new message document is added to Firestore.
        
        Args:
            message_id: ID of the message document
            message_data: Dictionary containing the message data
        """
        nonlocal counter
        
        # Log the received message
        logging.info(f"Received message: {message_id}")
        logging.info(f"Message data: {json.dumps(message_data, default=str)}")
        
        # Extract configuration from the message
        config = message_data.get('config', {})
        
        # For the counter bot POC, we only handle the startCountAt configuration
        if 'startCountAt' in config:
            try:
                new_count = int(config['startCountAt'])
                logging.info(f"Updating counter from {counter} to {new_count}")
                counter = new_count
                
                # Force an immediate update to Firebase
                update_bot_count(ticker, bot_id, counter)
            except (ValueError, TypeError) as e:
                logging.error(f"Invalid startCountAt value: {config['startCountAt']}. Error: {str(e)}")
    
    # Initialize the message client with our bot_id
    message_client = MessageFirebaseClient(bot_id)
    
    # Subscribe to messages with our callback function
    message_client.subscribe(process_message)
    logging.info(f"Subscribed to Firestore messages with bot ID: {bot_id}")
    
    try:
        while True:
            counter += 1
            current_time = time.time()
            
            # Update Firebase every 10 seconds
            if current_time - last_update >= 10:
                update_bot_count(ticker, bot_id, counter)
                last_update = current_time
                logging.info(f"Service {service_id} - Bot {bot_id} counter value: {counter}")
            
            time.sleep(1)  # simulate work by waiting 1 second
            
    except KeyboardInterrupt:
        logging.info(f"Counter bot for service {service_id} interrupted and stopping.")
        # Update one final time before stopping
        update_bot_count(ticker, bot_id, counter)
        # Stop the message client
        message_client.unsubscribe()
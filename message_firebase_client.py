import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import threading
import time
from config import load_config

class MessageFirebaseClient:
    def __init__(self, bot_id, ticker):
        """
        Initialize the MessageFirebaseClient.
        
        Args:
            bot_id: The ID of the bot
            ticker: The ticker symbol this bot is running for
        """
        self.bot_id = bot_id
        self.ticker = ticker
        self.firestore_db = firestore.client()
        self.last_processed_timestamp = time.time()
        self._subscribe_to_message_topic()
        logging.info(f"MessageFirebaseClient initialized for bot {bot_id} with ticker {ticker}")

    def _subscribe_to_message_topic(self):
        """
        Subscribe to the Firebase Cloud Messaging topic for configuration messages.
        Note: In a real implementation, we would register a device token and subscribe,
        but for server-side applications, we'll use Firestore listeners instead.
        """
        # The topic that all bots are subscribed to
        self.topic = 'config-messages'
        logging.info(f"Bot {self.bot_id} subscribed to topic: {self.topic}")

    def start_message_listener(self):
        """
        Start listening for configuration messages from Firestore.
        This method sets up a background thread to poll for new messages.
        """
        logging.info(f"Starting message listener for bot {self.bot_id}")
        
        # Create a background thread to poll for messages
        self.running = True
        self.listener_thread = threading.Thread(target=self._poll_for_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        return self.listener_thread

    def _poll_for_messages(self):
        """
        Poll Firestore for new configuration messages.
        In production, you would prefer to use a real-time listener,
        but for this simple implementation, we'll poll.
        """
        while self.running:
            try:
                # Get all messages for simplicity
                query = self.firestore_db.collection('messages')
                messages = query.get()
                
                for message in messages:
                    message_data = message.to_dict()
                    
                    # Process all messages for now, just to ensure we're getting messages
                    self._process_message(message.id, message_data)
                
                # Sleep for a few seconds before checking again
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error polling for messages: {str(e)}")
                time.sleep(10)  # Wait longer after an error
    
    def _process_message(self, message_id, message_data):
        """
        Process a configuration message.
        
        Args:
            message_id: The ID of the message
            message_data: The message data dictionary
        """
        try:
            logging.info(f"Processing message {message_id}")
            logging.info(f"Message data: {json.dumps(message_data, default=str)}")
            
            # Check if this message is targeted for this bot
            target = message_data.get('target', {})
            target_type = target.get('type')
            selected_bots = target.get('selected', [])
            
            should_process = False
            
            if target_type == 'ALL':
                # Message is for all bots
                should_process = True
                logging.info(f"Message {message_id} is for ALL bots")
            elif target_type == 'SELECTED' and self.bot_id in selected_bots:
                # Message is only for selected bots, and we're one of them
                should_process = True
                logging.info(f"Message {message_id} is for SELECTED bots including {self.bot_id}")
            else:
                logging.info(f"Message {message_id} is not targeted for this bot. Skipping.")
            
            if should_process:
                # Extract the configuration from the message
                config = message_data.get('config', {})
                logging.info(f"Configuration data: {json.dumps(config, default=str)}")
                
                # For now, just log the message content
                # In a full implementation, we would process the configuration
                # and update the bot's behavior accordingly
                
                # TODO: Implement acknowledgement in the future
                logging.info(f"Successfully processed message {message_id}")
                
        except Exception as e:
            logging.error(f"Error processing message {message_id}: {str(e)}")
    
    def stop(self):
        """Stop the message listener"""
        self.running = False
        if hasattr(self, 'listener_thread') and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2)
        logging.info(f"Message listener for bot {self.bot_id} stopped")

# Function to initialize the MessageFirebaseClient
def initialize_message_client(bot_id, ticker):
    """
    Initialize and start the message client.
    
    Args:
        bot_id: The ID of the bot
        ticker: The ticker symbol this bot is running for
        
    Returns:
        The initialized MessageFirebaseClient instance
    """
    message_client = MessageFirebaseClient(bot_id, ticker)
    message_client.start_message_listener()
    return message_client

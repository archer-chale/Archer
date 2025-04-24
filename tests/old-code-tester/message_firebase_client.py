import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

class MessageFirebaseClient:
    """
    A simplified client for subscribing to Firestore message documents.
    This client allows bots to:
    1. Subscribe to new messages in the Firestore 'messages' collection
    2. Process messages using a provided callback function
    3. Acknowledge receipt of messages
    """
    
    def __init__(self, bot_id):
        """
        Initialize the MessageFirebaseClient.
        
        Args:
            bot_id: The ID of the bot that will process messages
        """
        # Store the bot's ID for message filtering and acknowledgment
        self.bot_id = bot_id
        
        # Get a reference to the Firestore database
        self.firestore_db = firestore.client()
        
        # Initialize the listener reference to None
        self.message_listener = None
        
        logging.info(f"MessageFirebaseClient initialized for bot {bot_id}")

    def subscribe(self, callback_function):
        """
        Subscribe to new messages in the Firestore 'messages' collection.
        
        Args:
            callback_function: A function that will be called when a new message is detected.
                              This function should accept two parameters:
                              - message_id: The ID of the message
                              - message_data: The message data as a dictionary
        
        Returns:
            The Firestore listener object that can be used to unsubscribe later
        """
        logging.info(f"Setting up message subscription for bot {self.bot_id}")
        
        # Create a callback function that will be triggered when documents change
        def on_snapshot(col_snapshot, changes, read_time):
            # Iterate through each change in the collection
            for change in changes:
                # Only process newly added documents
                if change.type.name == 'ADDED':
                    # Extract the document data and ID
                    message_data = change.document.to_dict()
                    message_id = change.document.id
                    
                    logging.info(f"New message detected with ID: {message_id}")
                    
                    # Call the user-provided callback function with the message details
                    callback_function(message_id, message_data)
                    
                    # Acknowledge the message
                    self.acknowledge_message(message_id)
        
        # Set up the real-time listener on the messages collection
        messages_ref = self.firestore_db.collection('messages')
        self.message_listener = messages_ref.on_snapshot(on_snapshot)
        
        logging.info(f"Message subscription active for bot {self.bot_id}")
        
        return self.message_listener
    
    def acknowledge_message(self, message_id):
        """
        Acknowledge that this bot has received and processed the message by
        updating the acknowledgements field in Firestore.
        
        Args:
            message_id: The ID of the message to acknowledge
        """
        try:
            # Get a reference to the specific message document
            message_ref = self.firestore_db.collection('messages').document(message_id)
            
            # Add this bot's ID to the acknowledgements array
            # ArrayUnion ensures the bot ID is only added once even if called multiple times
            message_ref.update({
                'acknowledgements': firestore.ArrayUnion([self.bot_id])
            })
            
            logging.info(f"Message {message_id} acknowledged by bot {self.bot_id}")
            
        except Exception as e:
            logging.error(f"Error acknowledging message {message_id}: {str(e)}")
    
    def unsubscribe(self):
        """
        Unsubscribe from Firestore message notifications.
        Call this method when shutting down to clean up resources.
        """
        if self.message_listener:
            # Detach the listener to stop receiving updates
            self.message_listener.unsubscribe()
            self.message_listener = None
            
            logging.info(f"Message listener for bot {self.bot_id} unsubscribed")

# # Example usage:
# """
# # Initialize the client
# client = MessageFirebaseClient('my-bot-id')

# # Define your callback function
# def process_message(message_id, message_data):
#     # Process the message according to your bot's logic
#     print(f"Processing message: {message_id}")
#     # ...your processing logic here...
    
#     # Acknowledge the message when done
#     client.acknowledge_message(message_id)

# # Subscribe to messages with your callback
# listener = client.subscribe(process_message)

# # When shutting down:
# # client.unsubscribe()

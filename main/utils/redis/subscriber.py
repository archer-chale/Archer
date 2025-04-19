"""
Redis Subscriber Module

This module provides functionality for subscribing to Redis channels and processing messages.
It uses the RedisConnection class for connection management and supports callback registration
and message filtering.
"""

import logging
from .connection import RedisConnection
from .message import parse_message, MessageValidationError
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisSubscriber:
    """
    Redis subscriber class for receiving messages from channels.
    
    Provides subscription mechanisms, callback registration, and message filtering.
    """
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    
    def __init__(self, host=REDIS_HOST, port=6379, db=0, **kwargs):
        """
        Initialize a new Redis subscriber.
        
        Args:
            host (str): Redis server hostname or IP address. Defaults to 'localhost'.
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
            **kwargs: Additional arguments to pass to the Redis connection.
        """
        self.connection = RedisConnection(host, port, db, **kwargs)
        self.pubsub = None
        self.callbacks = {}
        self.message_filters = {}
        self.thread = None
        self.is_running = False
    
    def _initialize_pubsub(self):
        """
        Initialize the pubsub object if it doesn't exist.
        """
        if self.pubsub is None:
            redis_conn = self.connection.connection
            self.pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)
    
    def _message_handler(self, message):
        """
        Internal message handler that processes messages and routes them to the appropriate callbacks.
        
        Args:
            message (dict): The Redis message object.
        """
        if message is None or 'data' not in message:
            return
        
        # Get channel and decode data
        channel = message['channel'].decode('utf-8')
        data = message['data'].decode('utf-8')
        
        try:
            # Parse JSON data
            try:
                # Parse the message into a structured format
                message = parse_message(data)
                
            except MessageValidationError as e:
                logger.warning(f"Invalid message format on channel '{channel}': {e}")
                return
            
            # Log message receipt
            logger.debug(f"Received message on channel '{channel}'")
            
            # Call the registered callback for this channel with the parsed message
            if channel in self.callbacks:
                # Pass the complete message to the callback
                self.callbacks[channel](message)
            
        except json.JSONDecodeError:
            logger.error(f"Received non-JSON message on channel '{channel}': {data}")
        except Exception as e:
            logger.error(f"Error processing message on channel '{channel}': {e}")
    
    def subscribe(self, channel, callback):
        """
        Subscribe to a Redis channel with a callback function.
        
        Args:
            channel (str): The channel to subscribe to.
            callback (callable): Function to call when a message is received.
            message_types (list, optional): List of message types to filter for. If None, all messages will be processed.
                                           Defaults to None.
                                           
        Returns:
            bool: True if subscription was successful, False otherwise.
        """
        try:
            self._initialize_pubsub()
            
            # Register the callback for this channel
            self.callbacks[channel] = callback
            
            # Subscribe to the channel
            self.pubsub.subscribe(**{channel: self._message_handler})
            logger.info(f"Subscribed to channel: {channel}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to channel {channel}: {e}")
            return False
    
    def psubscribe(self, pattern, callback):
        """
        Subscribe to Redis channels matching a pattern.
        
        Args:
            pattern (str): The pattern to subscribe to (e.g., "channel.*").
            callback (callable): Function to call when a message is received.
            message_types (list, optional): List of message types to filter for. 
                                           If None, all messages will be processed.
                                           Defaults to None.
                                           
        Returns:
            bool: True if subscription was successful, False otherwise.
        """
        try:
            self._initialize_pubsub()
            
            # Register the callback for this pattern
            self.callbacks[pattern] = callback
            
            # Subscribe to the pattern
            self.pubsub.psubscribe(**{pattern: self._message_handler})
            logger.info(f"Subscribed to pattern: {pattern}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to pattern {pattern}: {e}")
            return False
    
    def unsubscribe(self, channel=None):
        """
        Unsubscribe from a channel or all channels.
        
        Args:
            channel (str, optional): The channel to unsubscribe from. If None, unsubscribe from all channels.
                                    Defaults to None.
        """
        if self.pubsub is None:
            return
        
        try:
            if channel:
                self.pubsub.unsubscribe(channel)
                if channel in self.callbacks:
                    del self.callbacks[channel]
                if channel in self.message_filters:
                    del self.message_filters[channel]
                logger.info(f"Unsubscribed from channel: {channel}")
            else:
                self.pubsub.unsubscribe()
                self.callbacks.clear()
                self.message_filters.clear()
                logger.info("Unsubscribed from all channels")
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
    
    def punsubscribe(self, pattern=None):
        """
        Unsubscribe from a pattern or all patterns.
        
        Args:
            pattern (str, optional): The pattern to unsubscribe from. If None, unsubscribe from all patterns.
                                    Defaults to None.
        """
        if self.pubsub is None:
            return
        
        try:
            if pattern:
                self.pubsub.punsubscribe(pattern)
                if pattern in self.callbacks:
                    del self.callbacks[pattern]
                if pattern in self.message_filters:
                    del self.message_filters[pattern]
                logger.info(f"Unsubscribed from pattern: {pattern}")
            else:
                self.pubsub.punsubscribe()
                # Remove only pattern subscriptions from callbacks and filters
                for key in list(self.callbacks.keys()):
                    if '*' in key:
                        del self.callbacks[key]
                for key in list(self.message_filters.keys()):
                    if '*' in key:
                        del self.message_filters[key]
                logger.info("Unsubscribed from all patterns")
        except Exception as e:
            logger.error(f"Failed to punsubscribe: {e}")
    
    def start_listening(self, sleep_time=0.001, block=False):
        """
        Start listening for messages in a thread.
        
        Args:
            sleep_time (float, optional): Time to sleep between checking for messages. Defaults to 0.001.
            block (bool, optional): If True, runs in the current thread (blocking). If False, runs in a background thread.
                                   Defaults to False.
        
        Returns:
            threading.Thread or None: The thread object if running in background, None if running in foreground or if failed.
        """
        if self.pubsub is None:
            logger.error("Cannot start listening - no channels subscribed")
            return None
        
        if self.is_running:
            logger.warning("Already listening for messages")
            return self.thread
        
        try:
            self.is_running = True
            
            if block:
                # Run in this thread (blocking)
                logger.info("Starting message listener (blocking)")
                self.pubsub.run_in_thread(sleep_time=sleep_time, daemon=False)
                return None
            else:
                # Run in a separate thread (non-blocking)
                logger.info("Starting message listener (background thread)")
                self.thread = self.pubsub.run_in_thread(sleep_time=sleep_time, daemon=True)
                return self.thread
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start message listener: {e}")
            return None
    
    def stop_listening(self):
        """
        Stop the message listener thread if it's running.
        """
        if self.thread and self.thread.is_alive():
            self.thread.stop()
            self.thread = None
            self.is_running = False
            logger.info("Stopped message listener thread")
    
    def close(self):
        """
        Clean up resources and close connections.
        """
        self.stop_listening()
        if self.pubsub:
            self.unsubscribe()
            self.punsubscribe()
            self.pubsub.close()
            self.pubsub = None
        self.connection.disconnect()
        logger.info("Closed Redis subscriber")
    
    def __enter__(self):
        """
        Support for 'with' statement.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up resources when exiting a 'with' block.
        """
        self.close()

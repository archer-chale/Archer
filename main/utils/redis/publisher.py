"""
Redis Publisher Module

This module provides functionality for publishing JSON messages to Redis channels.
It uses the RedisConnection class for connection management.
"""

import json
import logging
from datetime import datetime
from .connection import RedisConnection
from .message import format_for_channel, MessageValidationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisPublisher:
    """
    Redis publisher class for sending messages to channels.
    
    Provides a clean API for publishing JSON messages to Redis channels.
    """
    
    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        """
        Initialize a new Redis publisher.
        
        Args:
            host (str): Redis server hostname or IP address. Defaults to 'localhost'.
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
            **kwargs: Additional arguments to pass to the Redis connection.
        """
        self.connection = RedisConnection(host, port, db, **kwargs)
        
    def publish(self, channel, message_data, sender=None):
        """
        Publish a message to a Redis channel.
        
        Args:
            channel (str): The channel to publish to.
            message_data (dict): The message data to publish.
            sender (str, optional): Identifier for the message sender. Defaults to None.
            
        Returns:
            int: Number of clients that received the message.
            
        Raises:
            MessageValidationError: If the message validation fails.
            redis.RedisError: If publishing fails.
        """
        try:
            # Format and validate the message for this channel
            message_json = format_for_channel(channel, message_data, sender)
            
            # Get Redis connection and publish
            redis_conn = self.connection.connection
            result = redis_conn.publish(channel, message_json)
            
            logger.info(f"Published message to {channel}")
            logger.debug(f"Message content: {message_json}")
            return result
        except Exception as e:
            logger.error(f"Failed to publish message to {channel}: {e}")
            raise
    
    def close(self):
        """
        Close the Redis connection.
        """
        self.connection.disconnect()
    
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

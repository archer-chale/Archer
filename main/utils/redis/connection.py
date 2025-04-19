"""
Redis Connection Management Module

This module provides a centralized connection management for Redis operations.
It handles connection configuration and provides a base connection object
that can be used by publishers and subscribers.
"""

import redis
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisConnection:
    """
    Redis connection management class.
    
    Provides centralized connection handling with configurable host/port/db parameters.
    """
    
    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        """
        Initialize a new Redis connection.
        
        Args:
            host (str): Redis server hostname or IP address. Defaults to 'localhost'.
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
            **kwargs: Additional arguments to pass to the Redis client.
        """
        self.host = host
        self.port = port
        self.db = db
        self.kwargs = kwargs
        self._connection = None
        
    def connect(self):
        """
        Establish a connection to the Redis server.
        
        Returns:
            redis.Redis: Redis client connection object.
            
        Raises:
            redis.RedisError: If connection fails.
        """
        try:
            if self._connection is None:
                self._connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    **self.kwargs
                )
                # Ping to verify connection
                self._connection.ping()
                logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")
            return self._connection
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    @property
    def connection(self):
        """
        Get the Redis connection, establishing it if not already connected.
        
        Returns:
            redis.Redis: Redis client connection object.
        """
        if self._connection is None:
            return self.connect()
        return self._connection
    
    def disconnect(self):
        """
        Close the Redis connection if it exists.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from Redis")
    
    def __del__(self):
        """
        Ensure connection is closed when the object is garbage collected.
        """
        self.disconnect()

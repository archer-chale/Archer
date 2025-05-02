# Redis Subscriber Component
import time
from typing import List, Dict, Any, Callable
import sys
import os

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    # When running directly from project root
    from main.utils.redis import (
        RedisSubscriber, RedisPublisher, CHANNELS, 
        REDIS_HOST_DOCKER, REDIS_PORT, REDIS_DB
    )
except ImportError:
    # For local development, adjust this path if needed
    sys.path.append(os.path.abspath('../..'))
    from main.utils.redis import (
        RedisSubscriber, RedisPublisher, CHANNELS, 
        REDIS_HOST_DOCKER, REDIS_PORT, REDIS_DB
    )

class FirebaseRedisSubscriber:
    def __init__(self, tickers: List[str]):
        """
        Initialize the FirebaseRedisSubscriber
        
        Args:
            tickers: List of tickers to subscribe to
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing FirebaseRedisSubscriber for {len(tickers)} tickers")
        self.tickers = tickers
        self.subscriber = None
        self.max_retries = 5
        self.retry_delay = 3  # seconds
        
    def connect(self) -> bool:
        """
        Connect to Redis and subscribe to channels for all tickers
        Implements retry logic to handle cases where Redis might not be ready
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.logger.info(f"Connecting to Redis at {REDIS_HOST_DOCKER}:{REDIS_PORT} (attempt {retry_count + 1}/{self.max_retries})")
                self.subscriber = RedisSubscriber(
                    host=REDIS_HOST_DOCKER, 
                    port=REDIS_PORT, 
                    db=REDIS_DB
                )
                self.logger.info("Successfully connected to Redis")
                return True
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Failed to connect to Redis: {e}")
                if retry_count < self.max_retries:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to connect to Redis after {self.max_retries} attempts")
        return False
            
    def subscribe_to_ticker_channels(self) -> None:
        """
        Subscribe to all ticker channels
        """
        if not self.subscriber:
            self.logger.error("Cannot subscribe: Redis connection not established")
            return
            
        self.logger.info(f"Subscribing to {len(self.tickers)} ticker channels")
        for ticker in self.tickers:
            channel_name = CHANNELS.get_ticker_channel(ticker)
            success = self.subscriber.subscribe(channel_name, self._message_handler)
            if success:
                self.logger.info(f"Subscribed to channel: {channel_name}")
            else:
                self.logger.error(f"Failed to subscribe to channel: {channel_name}")
    
    def _message_handler(self, message: Dict[str, Any]) -> None:
        """
        Handle incoming messages from Redis
        
        Args:
            message: The message received from Redis
        """
        try:
            data = message.get('data', {})
            message_type = data.get('type')
            
            # Get basic message info
            timestamp = message.get('timestamp', 'unknown')
            sender = message.get('sender', 'unknown')
            
            if message_type == 'price':
                self._handle_price_update(data, timestamp, sender)
            elif message_type == 'order':
                self._handle_order_update(data, timestamp, sender)
            else:
                self.logger.warning(f"Received unknown message type: {message_type}")
                self.logger.debug(f"Raw message: {message}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            self.logger.debug(f"Raw message: {message}")
    
    def _handle_price_update(self, data: Dict[str, Any], timestamp: str, sender: str) -> None:
        """
        Handle price update messages
        
        Args:
            data: The price data from the message
            timestamp: The timestamp of the message
            sender: The sender of the message
        """
        symbol = data.get('symbol', 'unknown')
        price = data.get('price', 'unknown')
        volume = data.get('volume', 'unknown')
        
        self.logger.info(f"PRICE UPDATE [{timestamp}] from {sender}")
        self.logger.info(f"  Symbol: {symbol}, Price: {price}, Volume: {volume}")
        self.logger.debug(f"  Raw data: {data}")
    
    def _handle_order_update(self, data: Dict[str, Any], timestamp: str, sender: str) -> None:
        """
        Handle order update messages
        
        Args:
            data: The order data from the message
            timestamp: The timestamp of the message
            sender: The sender of the message
        """
        symbol = data.get('symbol', 'unknown')
        order_data = data.get('order_data', {})
        event = order_data.get('event', 'unknown')
        
        self.logger.info(f"ORDER UPDATE [{timestamp}] from {sender}")
        self.logger.info(f"  Symbol: {symbol}, Event: {event}")
        self.logger.debug(f"  Raw data: {data}")
        
    def start_listening(self) -> None:
        """
        Start listening for messages on all subscribed channels
        """
        if not self.subscriber:
            self.logger.error("Cannot start listening: Redis connection not established")
            return
            
        try:
            self.logger.info("Starting to listen for messages...")
            self.subscriber.start_listening()
            self.logger.info("Listening for messages on all channels")
        except Exception as e:
            self.logger.error(f"Error starting listener: {e}")
    
    def close(self) -> None:
        """
        Close the Redis connection
        """
        if self.subscriber:
            try:
                self.subscriber.close()
                self.logger.info("Redis subscriber closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing subscriber: {e}")
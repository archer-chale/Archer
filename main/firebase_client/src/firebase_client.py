# Firebase Client Component
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class FirebaseClient:
    """
    Firebase client for storing trading bot data in Firebase Realtime Database
    """
    def __init__(self, service_account_path: str = "configs/adminsdk.json"):
        """
        Initialize the Firebase client with service account credentials
        
        Args:
            service_account_path: Path to the Firebase service account key
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing Firebase Client")
        self.service_account_path = service_account_path
        self.firebase_app = None
        self.db_ref = None
        self.tickers_cache = {}  # Cache for storing last price to minimize writes
        
    def connect(self) -> bool:
        """
        Connect to Firebase using the service account credentials
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to Firebase using service account: {self.service_account_path}")
            
            # Check if service account file exists
            if not os.path.exists(self.service_account_path):
                self.logger.error(f"Service account file not found: {self.service_account_path}")
                return False
                
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(self.service_account_path)
            
            # Initialize the app with a database URL
            # The database URL should be in format: https://<project-id>.firebaseio.com/
            # We'll try to read it from environment variables first, then use a default
            try:
                # First try to get from environment
                database_url = os.environ.get("FIREBASE_DATABASE_URL")
                
                # If not in environment, read project_id from service account and form the URL
                if not database_url:
                    with open(self.service_account_path, 'r') as f:
                        service_account_info = json.load(f)
                    project_id = service_account_info.get('project_id')
                    if not project_id:
                        self.logger.error("Project ID not found in service account file")
                        return False
                        
                    database_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
                
                self.logger.info(f"Using database URL: {database_url}")
                self.firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                
                # Get reference to root of database
                self.db_ref = db.reference('/')
                self.logger.info("Successfully connected to Firebase")
                return True
                
            except Exception as e:
                self.logger.error(f"Error initializing Firebase Admin SDK: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to Firebase: {e}")
            return False
            
    def update_price(self, symbol: str, price_data: Dict[str, Any]) -> bool:
        """
        Update the current price for a ticker with change detection
        
        Args:
            symbol: The ticker symbol (e.g., AAPL)
            price_data: Dictionary containing price, volume, and timestamp
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if not self.db_ref:
            self.logger.error("Cannot update price: Firebase connection not established")
            return False
            
        try:
            # Format data for Firebase
            current_price = {
                "price": price_data.get("price", "0"),
                "volume": price_data.get("volume", "0"),
                "timestamp": price_data.get("timestamp", str(time.time()))
            }
            
            # Check if price has changed to avoid unnecessary writes
            cache_key = f"{symbol}_price"
            cached_price = self.tickers_cache.get(cache_key)
            
            if cached_price and cached_price["price"] == current_price["price"]:
                # Skip update if price hasn't changed
                self.logger.debug(f"Skipping price update for {symbol} - no change detected")
                return True
                
            # Update the cache with new price
            self.tickers_cache[cache_key] = current_price
            
            # Update in Firebase - path will be /services/{symbol}
            # This matches the path structure used in the old working code
            service_ref = self.db_ref.child('services').child(symbol)
            
            # Update price in the services structure
            service_ref.update({
                'price': current_price['price'],
                'volume': current_price['volume'],
                'timestamp': current_price['timestamp'],
                'last_updated': datetime.now().isoformat()
            })
            
            self.logger.info(f"Updated price for {symbol}: {current_price['price']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating price for {symbol}: {e}")
            return False
            
    def store_order(self, symbol: str, order_data: Dict[str, Any]) -> bool:
        """
        Store order data for a ticker in the orders collection
        
        Args:
            symbol: The ticker symbol (e.g., AAPL)
            order_data: Dictionary containing order details
            
        Returns:
            bool: True if storing successful, False otherwise
        """
        if not self.db_ref:
            self.logger.error("Cannot store order: Firebase connection not established")
            return False
            
        try:
            # Extract order and execution details
            order = order_data.get("order_data", {}).get("order", {})
            event = order_data.get("order_data", {}).get("event", "unknown")
            timestamp = order_data.get("timestamp", str(time.time()))
            
            # Get order ID to use as the key in Firebase
            order_id = order.get("id", f"order-{int(time.time())}")
            
            # Format order data for Firebase
            formatted_order = {
                "event": event,
                "timestamp": timestamp,
                "order": order,
                "price": order_data.get("order_data", {}).get("price", "0"),
                "qty": order_data.get("order_data", {}).get("qty", "0"),
                "position_qty": order_data.get("order_data", {}).get("position_qty", "0")
            }
            
            # Store in Firebase - path will be /services/{symbol}/orders/{order_id}
            service_ref = self.db_ref.child('services').child(symbol)
            service_ref.child('orders').child(order_id).set(formatted_order)
            
            self.logger.info(f"Stored order for {symbol}: {order_id} (event: {event})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing order for {symbol}: {e}")
            return False
    
    def close(self) -> None:
        """
        Close the Firebase connection
        """
        try:
            if self.firebase_app:
                firebase_admin.delete_app(self.firebase_app)
                self.logger.info("Firebase connection closed")
        except Exception as e:
            self.logger.error(f"Error closing Firebase connection: {e}")

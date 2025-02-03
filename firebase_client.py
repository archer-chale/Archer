import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
from datetime import datetime

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_firebase():
    try:
        cred = credentials.Certificate("adminsdk.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://candlelyt-prince-default-rtdb.firebaseio.com'  # Replace with your database URL
        })
        logging.info("Firebase initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing Firebase: {str(e)}")
        raise

def register_service(service_id, ticker):
    """Register the service with Firebase and set initial status"""
    try:
        ref = db.reference(f'/services/{ticker}')
        ref.set({
            'status': 'running',
            'bots': {}
        })
        logging.info(f"Service {service_id} registered for ticker {ticker}")
        return True
    except Exception as e:
        logging.error(f"Error registering service {service_id}: {str(e)}")
        return False

def update_bot_count(ticker, bot_id, count):
    """Update the bot count in Firebase"""
    try:
        ref = db.reference(f'/services/{ticker}/bots/{bot_id}')
        ref.update({
            'count': count,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error updating bot count for {ticker}/{bot_id}: {str(e)}")

def update_service_status(ticker, status):
    """Update the service status in Firebase"""
    try:
        ref = db.reference(f'/services/{ticker}')
        ref.update({
            'status': status
        })
        logging.info(f"Updated status for {ticker} to {status}")
    except Exception as e:
        logging.error(f"Error updating status for {ticker}: {str(e)}")

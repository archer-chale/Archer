import os
import uuid
import logging
import time

from firebase_client import register_service
from counter_bot import run_price_subscriber

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    # Read environment variables
    ticker = os.environ.get('TICKER', 'DEFAULT')
    firebase_config = os.environ.get('FIREBASE_CONFIG', '{}')

    # Generate a unique service ID
    service_id = str(uuid.uuid4())
    logging.info(f"Service starting with ticker: {ticker}, service_id: {service_id}")

    # Register service with Firebase
    registration_status = register_service(service_id, ticker, firebase_config)
    if registration_status:
        logging.info("Service registration successful")
    else:
        logging.error("Service registration failed")
        return

    # Start the price subscriber
    run_price_subscriber(service_id)


if __name__ == '__main__':
    main()

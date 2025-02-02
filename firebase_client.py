import logging
import time


def register_service(service_id, ticker, firebase_config):
    logging.info(f"Registering service with id: {service_id} for ticker: {ticker}.")
    # Simulate Firebase registration using the provided configuration
    logging.info(f"Using Firebase config: {firebase_config}")
    time.sleep(1)  # Simulate network latency during registration
    logging.info("Service successfully registered with Firebase.")
    return True

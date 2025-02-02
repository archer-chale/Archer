import logging
import time


def run_counter_bot(service_id):
    counter = 0
    logging.info(f"Starting counter bot for service {service_id}...")
    try:
        while True:
            counter += 1
            logging.info(f"Service {service_id} counter value: {counter}")
            time.sleep(1)  # simulate work by waiting 1 second
    except KeyboardInterrupt:
        logging.info(f"Counter bot for service {service_id} interrupted and stopping.")
import logging
import time
from firebase_client import update_bot_count

def run_counter_bot(service_id, ticker, bot_id):
    counter = 0
    last_update = 0
    logging.info(f"Starting counter bot for service {service_id}...")
    
    try:
        while True:
            counter += 1
            current_time = time.time()
            
            # Update Firebase every 10 seconds
            if current_time - last_update >= 10:
                update_bot_count(ticker, bot_id, counter)
                last_update = current_time
                logging.info(f"Service {service_id} - Bot {bot_id} counter value: {counter}")
            
            time.sleep(1)  # simulate work by waiting 1 second
            
    except KeyboardInterrupt:
        logging.info(f"Counter bot for service {service_id} interrupted and stopping.")
        # Update one final time before stopping
        update_bot_count(ticker, bot_id, counter)
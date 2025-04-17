import logging
import sys
import uuid
from firebase_client import initialize_firebase, register_service, update_service_status
from counter_bot import run_counter_bot

def main():
    if len(sys.argv) != 2:
        print("Usage: python service.py <ticker>")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    service_id = str(uuid.uuid4())
    bot_id = service_id

    try:
        # Initialize Firebase
        initialize_firebase()
        
        # Register service
        if not register_service(service_id, ticker):
            logging.error("Failed to register service")
            sys.exit(1)

        # Start the counter bot
        run_counter_bot(service_id, ticker, bot_id)

    except KeyboardInterrupt:
        logging.info("Service shutting down...")
        update_service_status(ticker, "stopped")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        update_service_status(ticker, "stopped")
        sys.exit(1)

if __name__ == "__main__":
    main()

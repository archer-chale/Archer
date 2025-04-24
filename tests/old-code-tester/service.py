import logging
import sys
from counter_bot import run_price_subscriber

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    if len(sys.argv) != 2:
        print("Usage: python service.py <service_name>")
        sys.exit(1)

    service_name = sys.argv[1]
    logging.info(f"Starting price subscriber service: {service_name}")

    try:
        # Start the price subscriber
        run_price_subscriber(service_name)

    except KeyboardInterrupt:
        logging.info(f"Service {service_name} shutting down...")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

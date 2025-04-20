"""
Main module for running the Alpaca broker service.
"""
import time
from main.alpaca_broker.broker import AlpacaBroker

def main():
    """Main function to start the broker service."""
    broker = AlpacaBroker()
    broker.configure_api_keys()
    broker.start()
    
    try:
        # Keep the main thread alive while producer threads run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down broker...")
        broker.stop()
        print("Broker stopped.")

if __name__ == "__main__":
    main()

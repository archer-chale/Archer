# Firebase Client Service

import os
import sys
import time

# Set up basic logging
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger for this module
logger = logging.getLogger("FirebaseClientService")

# Local import when running as a package
try:
    from .redis_subscriber import FirebaseRedisSubscriber
# Fallback for running the file directly
except ImportError:
    from redis_subscriber import FirebaseRedisSubscriber

def load_tickers():
    """
    Load tickers from tickers.txt file with retry logic
    
    Returns:
        list: List of ticker symbols
    """
    # First try in configs directory (production path)
    tickers_paths = [
        "configs/tickers.txt",
    ]
    
    # Try each path
    for tickers_path in tickers_paths:
        if os.path.exists(tickers_path):
            logger.info(f"Using tickers file: {tickers_path}")
            break
    else:
        logger.error(f"Error: Tickers file not found. Tried: {', '.join(tickers_paths)}")
        logger.error("Please ensure the tickers.txt file exists in one of these locations.")
        sys.exit(1)
    
    # Try to read the file with retries
    max_retries = 3
    retry_delay = 2
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with open(tickers_path, 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
                
            if not tickers:
                logger.error("Error: No tickers found in the tickers.txt file")
                sys.exit(1)
                
            logger.info(f"Loaded {len(tickers)} tickers: {', '.join(tickers)}")
            return tickers
        except Exception as e:
            retry_count += 1
            logger.warning(f"Error loading tickers (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to load tickers after maximum retry attempts")
                sys.exit(1)

def main():
    """
    Main application entry point
    """
    logger.info("Starting Firebase Client Service (Redis Logging Phase)")
    
    # Load tickers from config file
    tickers = load_tickers()
    
    # Create subscriber
    subscriber = FirebaseRedisSubscriber(tickers)
    
    # Connect to Redis
    if not subscriber.connect():
        logger.error("Failed to connect to Redis. Exiting...")
        sys.exit(1)
    
    # Subscribe to ticker channels
    subscriber.subscribe_to_ticker_channels()
    
    # Start listening for messages
    subscriber.start_listening()
    
    # Keep the application running
    try:
        logger.info("Firebase Client Service is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down Firebase Client Service...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        subscriber.close()
        logger.info("Firebase Client Service stopped")

if __name__ == "__main__":
    main()

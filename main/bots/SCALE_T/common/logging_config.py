import logging
import os
from logging.handlers import TimedRotatingFileHandler

# Retrieve log levels and log file path from environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()           # for file logs
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "INFO").upper()  # for console logs
LOG_FILE = os.getenv("LOG_FILE", "app.log")                     # Log file name

# Create our custom logger
scale_t_logger = logging.getLogger("scale_t_logger")
# Set the custom logger to the lowest level so that all messages are passed to handlers.
scale_t_logger.setLevel(logging.DEBUG)

# Create a TimedRotatingFileHandler (rotates at midnight, keeps backups for 10 days)
rotating_handler = TimedRotatingFileHandler(
    LOG_FILE, when='midnight', interval=1, backupCount=10
)
rotating_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
rotating_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(CONSOLE_LOG_LEVEL)
console_handler.setFormatter(
    logging.Formatter('%(asctime)s -[%(name)s][%(funcName)s]- %(levelname)s - %(message)s')
)

# Add the handlers to the custom logger
# scale_t_logger.addHandler(rotating_handler)
scale_t_logger.addHandler(console_handler)

def get_logger(name):
    """
    Return a child logger with the given name based on our custom logger.
    This allows for module-specific logging without affecting the global root logger.
    """
    return scale_t_logger.getChild(name)

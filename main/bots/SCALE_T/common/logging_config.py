import logging
import os
from .custom_logfile_handler import CustomTimedRotatingFileHandler

class LoggerConfig:
    def __init__(self, log_base_path, bot_name="Unknown_bot", log_level=None, console_level=None):
        self.bot_name = bot_name
        self.log_level = log_level or os.getenv("LOG_LEVEL", "DEBUG").upper()
        self.console_level = console_level or os.getenv("CONSOLE_LOG_LEVEL", "INFO").upper()
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.root_logger = None
        self.log_base_path = log_base_path
        self.setup_root_logger()

    def setup_root_logger(self):
        if self.root_logger is not None:
            return self.root_logger

        self.root_logger = logging.getLogger(self.bot_name)
        self.root_logger.setLevel(logging.DEBUG)

        if not self.root_logger.handlers:
            # File handler
            rotating_handler = CustomTimedRotatingFileHandler(base_dir=self.log_base_path)
            rotating_handler.setLevel(getattr(logging, self.log_level, logging.DEBUG))
            rotating_handler.setFormatter(self.formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.console_level, logging.INFO))
            console_handler.setFormatter(self.formatter)

            self.root_logger.addHandler(rotating_handler)
            self.root_logger.addHandler(console_handler)

        return self.root_logger

    def get_logger(self, name):
        """
        Create a child logger for a specific module
        """
        if not self.root_logger:
            raise Exception("Root logger not setup")
        return self.root_logger.getChild(name)


import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from .constants import NYC_TZ, LOGS_DIR, BOT_NAME

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, base_dir=LOGS_DIR, bot_name="unknown", when="midnight", interval=1, backupCount=7, encoding=None, delay=False, utc=False):
        self.base_dir = base_dir
        self.bot_name = bot_name
        self.current_date = self.get_nyc_date()
        log_file = self.get_log_filename()
        super().__init__(log_file, when, interval, backupCount, encoding, delay, utc=True)  # Force UTC to handle timezone manually

    def get_nyc_date(self):
        """Get the current date in NYC timezone."""
        return datetime.now(NYC_TZ).strftime("%Y-%m-%d")

    def get_log_filename(self):
        """Generate log file path based on the current date."""
        year = datetime.now(NYC_TZ).strftime("%Y")
        month = datetime.now(NYC_TZ).strftime("%m")
        log_dir = os.path.join(self.base_dir, year, month)
        os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
        return os.path.join(log_dir, f"{self.bot_name}-{self.current_date}.log")

    def shouldRollover(self, record):
        """Check if the log file should be rolled over based on NYC time."""
        new_date = self.get_nyc_date()
        if new_date != self.current_date:
            self.current_date = new_date
            self.baseFilename = self.get_log_filename()
            self.stream.close()
            self.stream = self._open()
        return super().shouldRollover(record)

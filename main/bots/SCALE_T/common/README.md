# SCALE_T Common Utilities

## Overview

The `common` module provides core utilities, constants, and configuration settings used throughout the SCALE_T trading bot. This directory contains fundamental building blocks that ensure consistency, configurability, and proper logging across the application.

## Files and Components

### `constants.py`

This file serves as the central repository for all constants, paths, and configuration values used by SCALE_T.

**Key Features:**
- **Path Management**: Dynamically detects whether running in Docker or local environment and adjusts paths accordingly
- **Trading Type Definitions**: Enum-based types (PAPER/LIVE) with related configurations
- **API Key Mapping**: Maps trading types to appropriate environment variable names
- **File Naming Utilities**: Functions to generate and parse standardized filenames for ticker data
- **Directory Structure**: Defines the entire application's directory structure in one place

**Usage Example:**
```python
from ..common.constants import TradingType, get_ticker_filepath

# Get file path for ticker data
file_path = get_ticker_filepath("AAPL", TradingType.PAPER)
```

### `logging_config.py`

Configures a centralized, consistent logging system for the entire application with both file and console output.

**Key Features:**
- **Hierarchical Loggers**: Creates child loggers for each module
- **Multiple Handlers**: Logs to both rotating files and console
- **Configurable Levels**: Different log levels for file vs. console output
- **Standardized Format**: Consistent timestamp and log message format

**Usage Example:**
```python
from ..common.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)
logger.info("Operation started")
logger.debug("Detailed debug information")
```

### `custom_logfile_handler.py`

Extends the standard Python logging handlers with NYC timezone awareness and daily log rotation.

**Key Features:**
- **Timezone-Aware**: Uses NYC timezone for log filenames and rotation
- **Daily Rotation**: Creates new log files at midnight NYC time
- **Date-Based Organization**: Organizes logs in year/month directories
- **Automatic Directory Creation**: Creates log directories if they don't exist

### `notify.py`

Provides notification capabilities for important events (currently configured for macOS, but commented out).

**Key Features:**
- **Desktop Notifications**: Can display system notifications for alerts
- **Cross-Platform**: Can be extended for different operating systems
- **Simple Interface**: Basic title/message notification pattern

**Usage Example:**
```python
from ..common.notify import send_notification

# Notify about important events
send_notification("Trade Executed", "Bought 10 shares of AAPL at $150")
```

## Best Practices

1. **Always use constants from `constants.py`** instead of hardcoding values
2. **Get loggers using `get_logger()`** instead of creating them directly
3. **Use appropriate log levels**:
   - DEBUG: Detailed information for diagnosing problems
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened
   - ERROR: Serious problem that prevented operation
   - CRITICAL: Very serious error that may prevent the program from continuing
4. **Path handling**: Always use the path utilities in constants.py to ensure cross-environment compatibility

## Environment Requirements

The common utilities depend on several environment variables:

```
LOG_LEVEL=DEBUG  # Level for file logging
CONSOLE_LOG_LEVEL=INFO  # Level for console output
LOG_FILE=app.log  # Base log filename
```

These can be configured in the `.env` file located at the path specified by `ENV_FILE` in constants.py.

## Extending the Common Module

When adding new utilities:

1. Place generic, widely-used constants in `constants.py`
2. For new functionality that doesn't fit existing files, create a new module
3. Update this README when adding new files or significant functionality
4. Use the logging system consistently for all new code

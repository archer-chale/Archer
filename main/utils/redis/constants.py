import logging

logger = logging.getLogger(__name__)

# Default Redis connection parameters
REDIS_HOST_DOCKER = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0

# --- Channel Definitions ---

class CHANNELS:
    """Name for channel used to register bots with the broker."""
    BROKER_REGISTRATION = "BROKER_REGISTRATION"
    PROFIT_REPORT = "PROFIT_REPORT"

    @staticmethod
    def get_ticker_channel(ticker: str) -> str:
        """Generate the dynamic channel name for a specific ticker."""
        if not ticker or not isinstance(ticker, str):
            logger.error(f"Invalid ticker provided for channel generation: {ticker}")
            raise ValueError("Ticker must be a non-empty string")
        return f"TICKER_UPDATES_{ticker.upper()}"

    @classmethod
    def get_schema(cls, channel_name: str):
        """Get the schema for a specific channel name.
        Handles dynamic ticker channels.
        """
        if channel_name == cls.BROKER_REGISTRATION:
            return MESSAGE_SCHEMAS.BROKER_REGISTRATION
        elif channel_name.startswith("TICKER_UPDATES_"):
            # All dynamic ticker channels use the same combined schema
            return MESSAGE_SCHEMAS.TICKER_UPDATES
        else:
            logger.warning(f"No schema found for channel: {channel_name}")
            return {} # Return empty schema if no match

# --- Message Schema Definitions ---

class MESSAGE_SCHEMAS:
    """Registry of message schemas associated with channels."""

    # Schema for the fixed registration channel
    BROKER_REGISTRATION = {
        "required_fields": ["action", "ticker"],
        "optional_fields": [],
        "field_types": {
            "action": str, # Expected values: 'subscribe', 'unsubscribe'
            "ticker": str
        },
        "allowed_values": {
            "action": ["subscribe", "unsubscribe"]
        }
    }
    # Schema for the profit report channel
    PROFIT_REPORT = {
        "required_fields": ["symbol", "total", "unrealized", "realized", "timestamp"],
        "optional_fields": [],
        "field_types": {
            "total": (int, float, str), # Allow string for Decimal conversion downstream
            "unrealized": (int, float, str), 
            "realized": (int, float, str), 
            "converted": (int, float, str), 
            "timestamp": str, # ISO format string preferred
            "symbol": str
        },
        "allowed_values": {}
    }

    # Combined schema for dynamic ticker update channels
    TICKER_UPDATES = {
        "required_fields": ["type", "timestamp"],
        "optional_fields": ["price", "volume", "symbol", "order_data"], # Symbol is optional here as it's in the channel name
        "field_types": {
            "type": str, # Expected values: 'price', 'order'
            "timestamp": str, # ISO format string preferred
            "price": (int, float, str), # Allow string for Decimal conversion downstream
            "volume": (int, float, str, type(None)), # Allow string for Decimal conversion downstream
            "symbol": str,
            "order_data": dict # The serialized TradeUpdate dict
        },
        "allowed_values": {
            "type": ["price", "order"]
        }
        # Note: Further validation within 'order_data' might be needed depending on requirements
    }

    @classmethod
    def get(cls, channel_name: str, default=None):
        """Get the schema based on the channel name (handles dynamic ticker channels)."""
        if channel_name == CHANNELS.BROKER_REGISTRATION:
            return cls.BROKER_REGISTRATION
        elif channel_name == CHANNELS.PROFIT_REPORT:
            return cls.PROFIT_REPORT
        elif channel_name.startswith("TICKER_UPDATES_"):
            return cls.TICKER_UPDATES
        else:
            logger.warning(f"Attempted to get schema for unknown or dynamic channel directly: {channel_name}")
            return default if default is not None else {}

# Example usage (optional, for clarity):
# price_channel = CHANNELS.get_ticker_channel("AAPL")
# order_channel = CHANNELS.get_ticker_channel("MSFT")
# registration_channel = CHANNELS.BROKER_REGISTRATION
#
# price_schema = CHANNELS.get_schema(price_channel)
# registration_schema = CHANNELS.get_schema(registration_channel)

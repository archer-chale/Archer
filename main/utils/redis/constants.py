class CHANNELS:
    PRICE_DATA = "PRICE_DATA"
    
    @classmethod
    def get_schema(cls, channel):
        """Get the schema for a specific channel.
        
        Args:
            channel (str): Channel name to get schema for
            
        Returns:
            dict: Schema definition with required/optional fields and types
        """
        return MESSAGE_SCHEMAS.get(channel, {})


class MESSAGE_SCHEMAS:
    """Registry of message schemas associated with channels.
    
    Each schema defines:
    - required_fields: List of fields that must be present
    - optional_fields: List of fields that may be present
    - field_types: Dictionary mapping field names to expected types
    """
    PRICE_DATA = {
        "required_fields": ["symbol", "price"],
        "optional_fields": ["volume"],
        "field_types": {
            "symbol": str,
            "price": (int, float),
            "volume": (int, float)
        }
    }
    
    @classmethod
    def get(cls, channel, default=None):
        """Get the schema for a channel.
        
        Args:
            channel (str): Channel name
            default (dict, optional): Default schema to return if not found. Defaults to None.
            
        Returns:
            dict: Schema for the channel or default if not found
        """
        return getattr(cls, channel, default)

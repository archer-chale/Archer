"""
Redis Message Module

This module provides message validation and formatting utilities for Redis channels.
It works with the schemas defined in constants.py to ensure messages conform to
channel-specific expected formats.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from .constants import CHANNELS, MESSAGE_SCHEMAS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageValidationError(Exception):
    """Exception raised when message validation fails."""
    pass

def validate_message(channel: str, data: Dict[str, Any]) -> bool:
    """
    Validate message data against the channel's schema.
    
    Args:
        channel (str): Channel name the message will be sent to
        data (dict): Message data to validate
        
    Returns:
        bool: True if the message is valid
        
    Raises:
        MessageValidationError: If validation fails
    """
    # Get schema for this channel
    schema = MESSAGE_SCHEMAS.get(channel)
    
    if not schema:
        # No schema defined for this channel, nothing to validate
        return True
    
    # Check required fields
    for field in schema.get("required_fields", []):
        if field not in data:
            raise MessageValidationError(f"Missing required field '{field}' for channel {channel}")
    
    # Check field types
    for field_name, field_value in data.items():
        if field_name in schema.get("field_types", {}):
            expected_types = schema["field_types"][field_name]
            
            # Convert single type to tuple for consistent handling
            if not isinstance(expected_types, tuple):
                expected_types = (expected_types,)
            
            if not isinstance(field_value, expected_types):
                type_names = " or ".join([t.__name__ for t in expected_types])
                raise MessageValidationError(
                    f"Field '{field_name}' should be of type {type_names}, "
                    f"got {type(field_value).__name__}"
                )
    
    return True

def create_message(data: Dict[str, Any], sender: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized message structure with metadata.
    
    Args:
        data (dict): The message payload
        sender (str, optional): Sender identifier. Defaults to None.
        
    Returns:
        dict: Complete message with metadata
    """
    return {
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "sender": sender or "unknown"
    }

def format_for_channel(channel: str, data: Dict[str, Any], sender: Optional[str] = None) -> str:
    """
    Validate and format a message for a specific channel.
    
    Args:
        channel (str): Channel name
        data (dict): Message data
        sender (str, optional): Sender identifier. Defaults to None.
        
    Returns:
        str: JSON-encoded message ready to send
        
    Raises:
        MessageValidationError: If validation fails
    """
    # Validate against channel schema
    validate_message(channel, data)
    
    # Create message with metadata
    message = create_message(data, sender)
    
    # Convert to JSON
    return json.dumps(message)

def parse_message(message_str: str) -> Dict[str, Any]:
    """
    Parse a JSON message string into a dictionary.
    
    Args:
        message_str (str): JSON message string
        
    Returns:
        dict: Parsed message
        
    Raises:
        MessageValidationError: If the message cannot be parsed
    """
    try:
        return json.loads(message_str)
    except json.JSONDecodeError as e:
        raise MessageValidationError(f"Invalid message format: {e}")

def extract_data(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract just the data portion from a message.
    
    Args:
        message (dict): Complete message with metadata
        
    Returns:
        dict: Just the data payload
        
    Raises:
        MessageValidationError: If the message structure is invalid
    """
    if not isinstance(message, dict):
        raise MessageValidationError("Message must be a dictionary")
        
    if "data" not in message:
        raise MessageValidationError("Message missing 'data' field")
        
    return message["data"]

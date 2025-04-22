from enum import Enum

class MessageType(Enum):
    """Message types for broker communication"""
    TRADE_UPDATE = "trade_update"
    ORDER_UPDATE = "order_update"
    ERROR = "error"

class StreamType(Enum):
    """Types of data streams managed by the broker"""
    TRADES = "trades"
    ORDERS = "orders"

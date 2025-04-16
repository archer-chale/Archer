from enum import Enum, auto


class MessageType(Enum):
    PRICE_UPDATE = auto()
    ORDER_UPDATE = 'order_update'

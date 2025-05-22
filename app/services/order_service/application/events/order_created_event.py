from dataclasses import dataclass

class BaseEvent:
    def __init__(self):
        self.event_type = self.__class__.__name__


@dataclass
class OrderCreatedEvent(BaseEvent):
    order_id: str 

    def to_dict(self):
        return {
            'event_type': self.event_type,
            'order_id': self.order_id
        }

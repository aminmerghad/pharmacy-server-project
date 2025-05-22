from enum import Enum

class OrderStatus(Enum):
    PENDING = "PENDING"       # Initial state when order is created
    CONFIRMED = "CONFIRMED"   # Order is confirmed and being processed
    COMPLETED = "COMPLETED"   # Order has been completed
    CANCELLED = "CANCELLED"   # Order has been cancelled    
    FAILED = "FAILED"  

    @classmethod
    def can_transition(cls, current: 'OrderStatus', target: 'OrderStatus') -> bool:
        transitions = {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELLED],
            cls.CONFIRMED: [cls.COMPLETED, cls.CANCELLED],
            cls.COMPLETED: [],
            cls.CANCELLED: [],
            cls.FAILED:[]
        }
        return target in transitions.get(current, [])




"""Event bus implementation."""
from typing import Dict, List, Type, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4
from enum import Enum
from sqlalchemy.orm import Session

class EventPriority(Enum):
    """Event priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class EventMetadata:
    """Enhanced event metadata"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = field(default="")
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    version: str = "1.0"
    priority: EventPriority = EventPriority.NORMAL
    source: str = ""
    user_id: Optional[int] = None

@dataclass
class Event:
    """Base event class"""
    metadata: EventMetadata = field(default_factory=EventMetadata)

    def __post_init__(self):
        self.metadata.event_type = self.__class__.__name__

class EventHandlerContext:
    """Context for event handlers"""
    def __init__(self, session: Session = None):
        self.session = session
        self.event_metadata: Optional[EventMetadata] = None
        self.error: Optional[Exception] = None
        self.retry_count: int = 0

class EventBus:
    """Enhanced application-wide event bus"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._handlers: Dict[Type[Event], List[Callable]] = {}
            self._error_handlers: List[Callable] = []
            self._middlewares: List[Callable] = []
            self._event_history: List[Dict] = []
            self._initialized = True
    
    def init(self):
        """Initialize event bus."""
        pass
    
    def publish(self, event: Event, context: Optional[EventHandlerContext] = None) -> None:
        """Publish an event."""
        
        if not context:
            context = EventHandlerContext()
        
        # Apply middlewares
        for middleware in self._middlewares:
            middleware(event, context)
        
        # Record event in history
        # self._event_history.append({
        #     'event_id': event.metadata.event_id,
        #     'event_type': event.metadata.event_type,
        #     'timestamp': event.metadata.timestamp,
        #     'correlation_id': event.metadata.correlation_id,
        #     'causation_id': event.metadata.causation_id,
        #     'version': event.metadata.version,
        #     'priority': event.metadata.priority.value,
        #     'source': event.metadata.source,
        #     'user_id': event.metadata.user_id
        # })
       
        # Handle event
        event_type = type(event)
        if event_type in self._handlers:
            try:
                for handler in self._handlers[event_type]:
                    # handler(event, context)
                    handler(event)
            except Exception as e:
                self._handle_error(e, event, context)
    
    def subscribe(self, event_type: Type[Event], handler: Callable, priority: EventPriority = EventPriority.NORMAL) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def subscribe_error(self, handler: Callable) -> None:
        """Subscribe to error events."""
        self._error_handlers.append(handler)
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to event processing pipeline."""
        self._middlewares.append(middleware)
    
    def get_history(self, 
                   event_type: Optional[Type[Event]] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Dict]:
        """Get event history with optional filters."""
        filtered_history = self._event_history
        
        if event_type:
            filtered_history = [
                event for event in filtered_history
                if event['event_type'] == event_type.__name__
            ]
        
        if start_time:
            filtered_history = [
                event for event in filtered_history
                if event['timestamp'] >= start_time
            ]
        
        if end_time:
            filtered_history = [
                event for event in filtered_history
                if event['timestamp'] <= end_time
            ]
        
        return filtered_history
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def _handle_error(self, error: Exception, event: Event, context: Optional[EventHandlerContext]) -> None:
        """Handle error in event processing."""
        if context:
            context.error = error
        
        for handler in self._error_handlers:
            try:
                # handler(error, event, context)
                handler(error, event)
            except Exception:
                # Log error handler failure
                pass 
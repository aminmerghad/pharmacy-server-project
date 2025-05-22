from typing import Dict, Type, Callable, Any, Optional
import logging
from app.services.invoice_service.application.events.invoice_events import InvoiceEvent

logger = logging.getLogger(__name__)

class EventDispatcher:
    """
    Dispatches events to registered handlers.
    Can work with direct callbacks or an event bus system.
    """
    
    def __init__(self, event_bus=None):
        """
        Initialize the event dispatcher.
        
        Args:
            event_bus: Optional event bus to publish events to external subscribers
        """
        self._handlers: Dict[Type, Callable] = {}
        self._event_bus = event_bus
        
    def register(self, event_type: Type, handler: Callable) -> None:
        """
        Register a handler for an event type.
        
        Args:
            event_type: The type of event to listen for
            handler: The function to call when the event occurs
        """
        self._handlers[event_type] = handler
        logger.debug(f"Registered handler for event: {event_type.__name__}")
        
    def dispatch(self, event: Any) -> None:
        """
        Dispatch an event to its registered handler.
        
        Args:
            event: The event to dispatch
        """
        event_type = type(event)
        
        # First dispatch to local handlers
        if event_type in self._handlers:
            try:
                self._handlers[event_type](event)
                logger.debug(f"Dispatched event {event_type.__name__} to local handler")
            except Exception as e:
                logger.error(f"Error in event handler for {event_type.__name__}: {str(e)}")
        
        # Then publish to event bus if available
        if self._event_bus:
            try:
                event_dict = event.to_dict() if hasattr(event, 'to_dict') else event
                self._event_bus.publish(event_type.__name__, event_dict)
                logger.debug(f"Published event {event_type.__name__} to event bus")
            except Exception as e:
                logger.error(f"Error publishing event {event_type.__name__} to event bus: {str(e)}") 
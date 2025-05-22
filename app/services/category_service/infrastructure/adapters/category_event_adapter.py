# import logging
# from typing import Any

# from app.shared.application.events.event_bus import EventBus
# from app.shared.application.events.event_handler import EventHandler
# from app.shared.application.events.domain_event import DomainEvent

# # Configure logger
# logger = logging.getLogger(__name__)

# class CategoryEventAdapter(EventHandler):
#     """
#     Adapter for handling category-related events.
#     """
    
#     def __init__(self, event_bus: EventBus):
#         self._event_bus = event_bus
#         self._register_handlers()
    
#     def _register_handlers(self) -> None:
#         """Register all event handlers with the event bus."""
#         pass
    
#     def handle(self, event: DomainEvent) -> None:
#         """
#         Handle a domain event.
        
#         Args:
#             event: The domain event to handle
#         """
#         logger.info(f"Handling event: {event.__class__.__name__}")
        
#         # Handle different event types
#         event_type = event.__class__.__name__
        
#         if hasattr(self, f"_handle_{event_type}"):
#             handler = getattr(self, f"_handle_{event_type}")
#             handler(event)
#         else:
#             logger.warning(f"No handler registered for event type: {event_type}")
    
 
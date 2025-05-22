# import json
# import logging
# import time
# from typing import Dict, Any, List, Optional

# import pika
# from pika.exceptions import AMQPConnectionError, AMQPChannelError

# from app.services.order_service.infrastructure.adapters.event_bus_adapter import EventBusAdapter

# logger = logging.getLogger(__name__)

# class RabbitMQEventBus(EventBusAdapter):
#     """
#     RabbitMQ implementation of the event bus adapter.
#     """
    
#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the RabbitMQ event bus adapter.
        
#         Args:
#             config: Configuration dictionary containing RabbitMQ connection parameters
#         """
#         self.config = config
#         self.connection = None
#         self.channel = None
#         self.exchange = config.get('exchange', 'pharmacy.events')
#         self.max_retries = config.get('max_retries', 3)
#         self.retry_delay = config.get('retry_delay', 1)  # seconds
#         self.connection_params = pika.ConnectionParameters(
#             host=config.get('host', 'localhost'),
#             port=config.get('port', 5672),
#             virtual_host=config.get('virtual_host', '/'),
#             credentials=pika.PlainCredentials(
#                 username=config.get('username', 'guest'),
#                 password=config.get('password', 'guest')
#             ),
#             heartbeat=config.get('heartbeat', 60)
#         )
        
#     def connect(self) -> bool:
#         """
#         Connect to RabbitMQ and create a channel.
        
#         Returns:
#             True if the connection was successful, False otherwise
#         """
#         if self.connection and self.connection.is_open:
#             return True
            
#         try:
#             logger.info("Connecting to RabbitMQ")
#             self.connection = pika.BlockingConnection(self.connection_params)
#             self.channel = self.connection.channel()
            
#             # Declare the exchange for publishing events
#             self.channel.exchange_declare(
#                 exchange=self.exchange,
#                 exchange_type='topic',
#                 durable=True
#             )
            
#             logger.info("Successfully connected to RabbitMQ")
#             return True
            
#         except AMQPConnectionError as e:
#             logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
#             return False
#         except Exception as e:
#             logger.error(f"Unexpected error connecting to RabbitMQ: {str(e)}")
#             return False
    
#     def disconnect(self) -> bool:
#         """
#         Disconnect from RabbitMQ.
        
#         Returns:
#             True if the disconnection was successful, False otherwise
#         """
#         try:
#             if self.connection and self.connection.is_open:
#                 logger.info("Disconnecting from RabbitMQ")
#                 self.connection.close()
#                 self.connection = None
#                 self.channel = None
#                 return True
#             return True
#         except Exception as e:
#             logger.error(f"Error disconnecting from RabbitMQ: {str(e)}")
#             return False
    
#     def publish(self, event: Dict[str, Any]) -> bool:
#         """
#         Publish an event to RabbitMQ.
        
#         Args:
#             event: Event to publish, as a dictionary
            
#         Returns:
#             True if the event was published successfully, False otherwise
#         """
#         event_type = event.get('type', 'unknown.event')
#         routing_key = event_type.replace('.', '_')
        
#         for attempt in range(self.max_retries):
#             try:
#                 if not self.connection or not self.connection.is_open:
#                     if not self.connect():
#                         logger.error("Failed to connect to RabbitMQ for publishing")
#                         time.sleep(self.retry_delay)
#                         continue
                
#                 self.channel.basic_publish(
#                     exchange=self.exchange,
#                     routing_key=routing_key,
#                     body=json.dumps(event),
#                     properties=pika.BasicProperties(
#                         delivery_mode=2,  # make message persistent
#                         content_type='application/json'
#                     )
#                 )
                
#                 logger.info(f"Published event {event_type} to RabbitMQ")
#                 return True
                
#             except AMQPConnectionError as e:
#                 logger.error(f"Connection error on attempt {attempt+1}: {str(e)}")
#                 self.connection = None
#                 self.channel = None
#                 time.sleep(self.retry_delay)
                
#             except AMQPChannelError as e:
#                 logger.error(f"Channel error on attempt {attempt+1}: {str(e)}")
#                 # Try to recreate channel
#                 try:
#                     self.channel = self.connection.channel()
#                 except Exception:
#                     self.connection = None
#                     self.channel = None
#                 time.sleep(self.retry_delay)
                
#             except Exception as e:
#                 logger.error(f"Unexpected error publishing to RabbitMQ on attempt {attempt+1}: {str(e)}")
#                 time.sleep(self.retry_delay)
        
#         logger.error(f"Failed to publish event {event_type} after {self.max_retries} attempts")
#         return False
    
#     def publish_batch(self, events: List[Dict[str, Any]]) -> Dict[int, bool]:
#         """
#         Publish multiple events to RabbitMQ.
        
#         Args:
#             events: List of events to publish, as dictionaries
            
#         Returns:
#             Dictionary mapping indices to success status
#         """
#         results = {}
        
#         for i, event in enumerate(events):
#             results[i] = self.publish(event)
            
#         return results 
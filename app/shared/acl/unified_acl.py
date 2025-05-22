from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

from app.shared.acl.translators import InventoryTranslator, ProductTranslator
from app.shared.domain.enums.enums import ServiceType

class ServiceResponse:
    """Standardized response format for all ACL operations"""
    def __init__(
        self, 
        success: bool, 
        data: Optional[Dict] = None, 
        error: Optional[str] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error


    

@dataclass
class ServiceContext:
    service_type: ServiceType
    operation: str
    data: Any

class UnifiedACL:
    """Centralized Anti-Corruption Layer for all services"""
    
    def __init__(self):
        self._service_providers: Dict[ServiceType, Callable] = {}       
     
        # Initialize translators
        self._translators = self._init_translators()

    def _get_service(self, service_type: ServiceType):
        """Lazy load the service when needed"""
        provider = self._service_providers.get(service_type)
        if not provider:
            raise ValueError(f"No provider registered for service: {service_type}")
        return provider()

    def register_service(self, service_type: ServiceType, provider: Callable):
        """Register a service provider that will be called lazily"""
        self._service_providers[service_type] = provider

    def _init_translators(self) -> Dict:
        """Initialize all service translators"""
        return {
            ServiceType.INVENTORY: InventoryTranslator(),
            ServiceType.PRODUCT: ProductTranslator(),
        }
    def execute_service_operation(
        self, 
        context: ServiceContext
    ) -> ServiceResponse:
        """Execute operation on target service with translated data"""
        try:
            
            
            service = self._get_service(context.service_type)
            translator = self._translators[context.service_type]
            
            # Translate incoming data to service format
            request = translator.to_service_format(context.operation,context.data)
            # Execute service operation
            result = getattr(service, context.operation.lower())(request)
            
            # Translate response back to domain format
            response_data = translator.to_response_format(context.operation,result)           
            
            
            return ServiceResponse(success=True, data=response_data)
            
        except Exception as e:
            return ServiceResponse(success=False, error=str(e))

   

    
    

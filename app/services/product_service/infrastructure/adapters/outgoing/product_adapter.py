

from typing import Any, Dict
from app.services.product_service.application.dtos.product_dto import InventoryFieldsDto
from app.services.product_service.domain.ports.outgoing_ports import ProductServicePort
from app.services.product_service.domain.requests.get_inventory_by_id_request import GetInventoryByIdRequest
from app.shared.acl.unified_acl import ServiceContext, UnifiedACL
from app.shared.domain.enums.enums import ServiceType


class ProductServiceAdapter(ProductServicePort):
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def get_inventory_by_id(self, request: GetInventoryByIdRequest) -> InventoryFieldsDto: 
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.INVENTORY,
                operation="GET_INVENTORY_BY_ID",
                data=request
            )
        )
        
            
        return result.data
   
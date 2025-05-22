from app.shared.acl.unified_acl import UnifiedACL, ServiceType, ServiceContext
from app.services.order_service.domain.ports.outgoing_ports import InventoryServicePort
from app.shared.contracts.inventory.stock_check import (
    StockCheckRequestContract,
    StockCheckItemContract,
    StockCheckResponseContract
)
from app.services.order_service.domain.enums.stock_status import OrderStockStatus

class InventoryServiceAdapter(InventoryServicePort):
    def __init__(self, acl: UnifiedACL):
        self._acl = acl

    def stock_check(self, request: StockCheckRequestContract) -> StockCheckResponseContract : 
        dict_data = request.model_dump()
        
        result = self._acl.execute_service_operation(
            ServiceContext(
                service_type=ServiceType.INVENTORY,
                operation="STOCK_CHECK",
                data={
                    "consumer_id": dict_data.get("consumer_id"),
                    "items": [
                        {
                            "product_id": item.get("product_id"),
                            "quantity": item.get("quantity")
                        } for item in dict_data.get("items")
                    ]
                }
            )
        )
        
            
        return result.data
    # def check_inventory(self, order_data: Dict[str, Any]) -> ServiceResponse:
    #     """Check inventory availability for order"""
    #     translated_data = self.translate_request(
    #         ServiceType.ORDER,
    #         ServiceType.INVENTORY,
    #         order_data
    #     )
        
    #     return self.execute_service_operation(ServiceContext(
    #         service_type=ServiceType.INVENTORY,
    #         operation='check_stock_level',
    #         data=translated_data
    #     ))

    # def request_stock_release(self, order_id: UUID, items: List[Dict[str, Any]]) -> bool:
    #     result = self._acl.execute_service_operation(
    #         ServiceContext(
    #             service_type=ServiceType.INVENTORY,
    #             operation='release_stock',
    #             data={
    #                 'order_id': str(order_id),
    #                 'items': items
    #             }
    #         )
    #     )
    #     return result.success 
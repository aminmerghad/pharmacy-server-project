from app.services.order_service.infrastructure.adapters.outgoing.inventory_adapter import InventoryServiceAdapter
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.contracts.inventory.stock_check import StockCheckRequestContract


class OrderAdapterService:
    def __init__(self, acl: UnifiedACL):
        self._acl = acl
        self._stock_check_adapter = InventoryServiceAdapter(self._acl)

    def stock_check(self, request: StockCheckRequestContract):
        return self._stock_check_adapter.stock_check(request)
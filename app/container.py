from dependency_injector import containers, providers

from app.services.invoice_service.service import InvoiceService
from app.services.order_service.service import OrderService
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus
from app.dataBase import Database
from app.services.inventory_service.service import InventoryService
from app.services.auth_service.service import AuthService
from app.services.product_service.service import ProductService
from app.services.category_service.service import CategoryService
from app.shared.domain.enums.enums import ServiceType

class Container(containers.DeclarativeContainer):
    """IoC container."""
   
    
    # Configuration
    config = providers.Configuration()
    unified_acl = providers.Singleton(UnifiedACL)
    # Core dependencies
    db = providers.Singleton(Database)
    event_bus = providers.Singleton(EventBus)
   
    
    # # Services
    inventory_service = providers.Factory(
        InventoryService,
        db=db,
        event_bus=event_bus,
        acl=unified_acl
    )
    auth_service = providers.Factory(
        AuthService,
        db=db,
        event_bus=event_bus
    )
    order_service = providers.Factory(
        OrderService,
        db=db,
        event_bus=event_bus,
        acl=unified_acl
    )
    product_service = providers.Factory(
        ProductService,
        db=db,
        event_bus=event_bus,
        acl=unified_acl
    )

    invoice_service = providers.Factory(
        InvoiceService,
        db=db,
        event_bus=event_bus,
        acl=unified_acl
    )
    
    category_service = providers.Factory(
        CategoryService,
        db=db,
        event_bus=event_bus,
        acl=unified_acl
    )

    @providers.Singleton
    def register_services(
        unified_acl: UnifiedACL,
        inventory_service: InventoryService,
        product_service: ProductService,
        category_service: CategoryService,
        # order_service: OrderService,
        # user_service: UserService,
        # payment_service: PaymentService,
    ) -> UnifiedACL:
        unified_acl.register_service(
            ServiceType.INVENTORY, 
            lambda: inventory_service
        )
        unified_acl.register_service(
            ServiceType.PRODUCT, 
            lambda: product_service
        )
        unified_acl.register_service(
            ServiceType.CATEGORY, 
            lambda: category_service
        )
        return unified_acl
    
    # Initialize services registration
    init_acl = providers.Resource(
        register_services,
        unified_acl=unified_acl,
        inventory_service=inventory_service,
        product_service=product_service,
        category_service=category_service
    )

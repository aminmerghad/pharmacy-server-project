from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetInventoryByIdRequest:
    product_id:UUID
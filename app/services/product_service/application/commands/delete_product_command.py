from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteProductCommand:
    id: UUID
    
    def __init__(self, **kwargs):
        # Extract the ID - either 'id' or 'product_id' could be provided
        self.id = kwargs.get('id') or kwargs.get('product_id')
        if not self.id:
            raise ValueError("Product ID is required for deletion")
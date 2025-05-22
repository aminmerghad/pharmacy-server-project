from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.services.order_service.domain.entities.order import OrderEntity


@dataclass
class OrderAggregator:
    orders : List[OrderEntity]
    def get_orders_by_status(self, status: str) -> List[OrderEntity]:
        return [order for order in self.orders if order.status == status]

    def generate_report(self) -> dict:
        report = {}
        for order in self.orders:
            report[order.order_id] = {
                'customer_id': order.customer_id,
                'total': order.calculate_total({'product1': 10.0, 'product2': 20.0}),  # Example prices
                'status': order.status
            }
        return report
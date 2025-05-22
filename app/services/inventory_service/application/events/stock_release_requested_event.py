from dataclasses import dataclass


@dataclass
class StockReleaseRequestedEvent():
    order_id: str
    items: list[dict]

@dataclass
class StockReleaseFailedEvent():
    order_id: str
    items: list[dict]


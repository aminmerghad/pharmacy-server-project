from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class StockReleaseProcessedEvent:
    """
    Event received when inventory service has processed a stock release request.
    Contains the results of the stock release operation.
    """
    order_id: str
    success: bool
    items: List[Dict[str, Any]]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat() 
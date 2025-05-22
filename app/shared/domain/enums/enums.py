from enum import Enum


class ServiceType(Enum):
    INVENTORY = "inventory",
    ORDER = "order",
    PRODUCT = "product",
    CATEGORY = "category"
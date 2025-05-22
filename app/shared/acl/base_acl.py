# app/shared/acl/base_acl.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ServiceTranslator(ABC):
    """Base translator for service-specific translations"""
    @abstractmethod
    def to_domain(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert external service data to domain format"""
        pass

    @abstractmethod
    def from_domain(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert domain data to external service format"""
        pass

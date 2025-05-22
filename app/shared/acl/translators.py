# app/shared/acl/translators.py
from typing import Dict, Any, List
from uuid import UUID
import logging

from pydantic import BaseModel
from app.services.product_service.application.dtos.product_dto import InventoryFieldsDto
from app.services.product_service.domain.requests.get_inventory_by_id_request import GetInventoryByIdRequest
from app.shared.contracts.inventory.enums import StockStatusContract
from app.shared.contracts.inventory.stock_check import (
    StockCheckItemContract,
    StockCheckRequestContract,
    StockCheckResponseContract
)
from app.shared.contracts.product.product_contract import (
    GetProductRequestContract,
    GetProductsRequestContract,
    SearchProductsRequestContract,
    CategoryProductsRequestContract
)
from app.shared.acl.base_acl import ServiceTranslator

# Configure logger
logger = logging.getLogger(__name__)

class StockCheckTranslator():
    def to_service_format(self, data:Dict[str,Any]) -> StockCheckRequestContract:
        return StockCheckRequestContract(
            consumer_id=data.get('consumer_id'),
            items=[StockCheckItemContract(
                product_id=item.get('product_id'),
                quantity=item.get('quantity')
            ) for item in data.get('items', [])]
        )

    def to_response_format(self, response ) -> StockCheckResponseContract:
        return response

class GetInventoryTranslator():
    def to_service_format(self, request: GetInventoryByIdRequest) -> Dict[str,Any]:

        return {
            'product_id':request.product_id
        }
        
    def to_response_format(self, data: Dict[str,Any]) -> InventoryFieldsDto:
        """Return the product data directly"""
        return InventoryFieldsDto(**data)


class GetProductTranslator():
    def to_service_format(self, data: Dict[str, Any]) -> UUID:
        """Convert external data to a product ID for the service"""
        return data.get('product_id')
        
    def to_response_format(self, response):
        """Return the product data directly"""
        return response


class GetProductsTranslator():
    def to_service_format(self, data: Dict[str, Any]) -> GetProductsRequestContract:
        """Convert external data to product listing request"""
        return GetProductsRequestContract(
            page=data.get('page', 1),
            page_size=data.get('page_size', 20),
            filters=data.get('filters', {})
        )
        
    def to_response_format(self, response):
        """Return the product list data directly"""
        return response


class SearchProductsTranslator():
    def to_service_format(self, data: Dict[str, Any]) -> SearchProductsRequestContract:
        """Convert external data to product search request"""
        return SearchProductsRequestContract(
            search_term=data.get('search_term', ''),
            page=data.get('page', 1),
            page_size=data.get('page_size', 20)
        )
        
    def to_response_format(self, response):
        """Return the search results directly"""
        return response


class CategoryProductsTranslator():
    def to_service_format(self, data: Dict[str, Any]) -> CategoryProductsRequestContract:
        """Convert external data to category products request"""
        return CategoryProductsRequestContract(
            category_id=data.get('category_id'),
            page=data.get('page', 1),
            page_size=data.get('page_size', 20)
        )
        
    def to_response_format(self, response):
        """Return the category products directly"""
        return response




class TranslatorFactory:
    def __init__(self):
        self.translators = {
            "STOCK_CHECK": StockCheckTranslator(),
            "GET_PRODUCT": GetProductTranslator(),
            "GET_PRODUCTS": GetProductsTranslator(),
            "SEARCH_PRODUCTS": SearchProductsTranslator(),
            "CATEGORY_PRODUCTS": CategoryProductsTranslator(),
            "GET_INVENTORY_BY_ID":GetInventoryTranslator()
        }

    def get_translator(self, query_type: str) -> ServiceTranslator:
        translator = self.translators.get(query_type)
        if not translator:
            raise ValueError(f"No translator found for query type: {query_type}")
        return translator


class InventoryTranslator:
    def __init__(self):
        self.translator_factory = TranslatorFactory()

    def to_service_format(self, query_type: str, external_data: Dict[str, Any]):
        translator = self.translator_factory.get_translator(query_type)
        return translator.to_service_format(external_data)

    def to_response_format(self, query_type: str, domain_data):
        translator = self.translator_factory.get_translator(query_type)
        return translator.to_response_format(domain_data)


class ProductTranslator:
    def __init__(self):
        self.translator_factory = TranslatorFactory()
        
    def to_service_format(self, query_type: str, data: Dict[str, Any]):
        """
        Translate data from external format to service-specific format
        
        Args:
            query_type: The type of operation to perform
            data: The data to transform
            
        Returns:
            Translated data in the format expected by the service
        """
        translator = self.translator_factory.get_translator(query_type)
        return translator.to_service_format(data)
        
    def to_response_format(self, query_type: str, domain_data):
        """
        Translate data from service format to external response format
        
        Args:
            query_type: The type of operation that was performed
            domain_data: The data returned by the service
            
        Returns:
            Translated data in the format expected by the caller
        """
        translator = self.translator_factory.get_translator(query_type)
        return translator.to_response_format(domain_data)
        
    def execute_product_operation(self, query_type: str, data: Dict[str, Any], product_service):
        """
        Execute a product operation through the appropriate service method
        
        Args:
            query_type: The operation type (e.g., GET_PRODUCT, SEARCH_PRODUCTS)
            data: The data for the operation
            product_service: The ProductService instance
            
        Returns:
            The result of the operation
        """
        try:
            # Convert incoming data to service format
            service_data = self.to_service_format(query_type, data)
            
            # Execute the appropriate service method based on operation type
            if query_type == "GET_PRODUCT":
                result = product_service.get_product(service_data)
            elif query_type == "GET_PRODUCTS":
                result = product_service.list_products(
                    page=service_data.page,
                    page_size=service_data.page_size,
                    filters=service_data.filters
                )
            elif query_type == "SEARCH_PRODUCTS":
                result = product_service.search_products(
                    search_term=service_data.search_term,
                    page=service_data.page,
                    page_size=service_data.page_size
                )
            elif query_type == "CATEGORY_PRODUCTS":
                result = product_service.get_products_by_category(
                    category_id=service_data.category_id,
                    page=service_data.page,
                    page_size=service_data.page_size
                )
            elif query_type == "UPDATE_PRODUCT":
                result = product_service.update_product(
                    id=service_data.get("id"),
                    **{k: v for k, v in service_data.items() if k != "id"}
                )
            elif query_type == "DELETE_PRODUCT":
                result = product_service.delete_product(service_data)
            else:
                raise ValueError(f"Unsupported operation type: {query_type}")
                
            # Convert result to response format
            return self.to_response_format(query_type, result)
            
        except Exception as e:
            # Handle exceptions and return a standardized error response
            error_message = f"Error executing product operation {query_type}: {str(e)}"
            logger.error(error_message)  
            return {"error": error_message}, 500

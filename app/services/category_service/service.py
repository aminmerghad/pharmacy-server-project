from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from app.dataBase import Database
from app.services.category_service.application.commands.create_category_command import CreateCategoryCommand
from app.services.category_service.application.commands.update_category_command import UpdateCategoryCommand
from app.services.category_service.application.commands.delete_category_command import DeleteCategoryCommand
from app.services.category_service.application.queries.get_category_by_id import GetCategoryByIdQuery
from app.services.category_service.application.queries.get_categories_by_filter import GetCategoriesByFilterQuery
from app.services.category_service.application.use_cases.create_category import CreateCategoryUseCase
from app.services.category_service.application.use_cases.update_category import UpdateCategoryUseCase
from app.services.category_service.application.use_cases.delete_category import DeleteCategoryUseCase
from app.services.category_service.application.use_cases.get_category import GetCategoryUseCase
from app.services.category_service.application.use_cases.list_categories import ListCategoriesUseCase
from app.services.category_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.category_service.infrastructure.query_services.category_query_service import CategoryQueryService
# from app.services.category_service.infrastructure.adapters.category_event_adapter import CategoryEventAdapter
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

# Configure logger
logger = logging.getLogger(__name__)

class CategoryService:
    """
    Service for managing categories in the system.
    """
    
    def __init__(self, db: Database, event_bus: EventBus, acl: UnifiedACL):
        self._db_session = db.get_session()
        self._acl = acl
        self._event_bus = event_bus
        self._init_resources()
        logger.info("Category service initialized")
        
    def _init_resources(self):
        # Normally this would come from configuration
        self._uow = SQLAlchemyUnitOfWork(
            self._db_session, 
            self._event_bus, 
            self._acl
        )
        self._query_service = CategoryQueryService(self._db_session, self._uow)
        self._create_category_use_case = CreateCategoryUseCase(self._uow)
        self._update_category_use_case = UpdateCategoryUseCase(self._uow)
        self._delete_category_use_case = DeleteCategoryUseCase(self._uow)        
        self._list_categories_use_case = ListCategoriesUseCase(self._uow)
    
    def create_category(self, command: CreateCategoryCommand):
        logger.info(f"Creating category with name: {command.category_fields.name}")
        try:
            result = self._create_category_use_case.execute(command)
            logger.info(f"Category created successfully with ID: {result.id}")
            return result
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Failed to create category: {str(e)}", exc_info=True)
            raise
    
    def update_category(self, command: UpdateCategoryCommand):
        logger.info(f"Updating category with ID: {command.id}")
        try:
            result = self._update_category_use_case.execute(command)
            logger.info(f"Category updated successfully: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            raise
    
    def delete_category(self, command: DeleteCategoryCommand):        
        logger.info(f"Deleting category with ID: {command.id}")
        try:
            result = self._delete_category_use_case.execute(command)
            logger.info(f"Category deleted successfully: {command.id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}")
            raise
    
    def get_category(self, query: GetCategoryByIdQuery):
        category_id = query.id
        logger.info(f"Getting category with ID: {category_id}")
        try:
            result = self._query_service.get_by_id(query)
            if result:
                logger.info(f"Category found: {category_id}")
            else:
                logger.info(f"Category not found: {category_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting category: {str(e)}")
            raise
    
    def list_categories(self, query: GetCategoriesByFilterQuery):        
        logger.info(f"Listing categories")
        try:
            result = self._query_service.list(query)
            return result
        except Exception as e:
            logger.error(f"Error listing categories: {str(e)}")
            raise

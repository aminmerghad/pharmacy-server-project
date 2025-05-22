# from uuid import UUID
# from app.services.inventory_service.application.commands.delete_product_command import DeleteProductCommand
# from app.services.inventory_service.domain.exceptions.inventory_errors import DeleteProductError, ProductNotFoundError
# from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork


# class DeleteProductUseCase():
#     def __init__(self,uow:UnitOfWork):
#         self._uow=uow
#     def excute(self,command:DeleteProductCommand):
#         # Check if product exists
#         self._get_product_or_not_found(command.product_id)
        
        
#         # Soft delete the product
#         success = self._uow.inventory_repository.delete(command.product_id)       
        
#         if not success:
#             raise DeleteProductError(message="Failed to delete product")
#         self._uow.commit()
#         return {
#             "product_id":command.product_id
#         }
#     def _get_product_or_not_found(self,product_id:UUID):
#         existing_product = self._uow.product_repository.get_by_id(product_id)
#         if not existing_product:
#             raise ProductNotFoundError(message=f"Product with ID {product_id} not found")

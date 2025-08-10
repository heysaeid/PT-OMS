from src.models.repositories.order.order_repository import OrderRepository
from src.models.dtos.order.order_domain_interface_dtos import (
    GetOrderByIdInputDTO,
    GetOrderByIdOutputDTO,
    SearchOrdersInputDTO,
    SearchOrdersOutputDTO,
)


class OrderLogic:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def get_order_by_id(
        self,
        input_dto: GetOrderByIdInputDTO,
    ) -> GetOrderByIdOutputDTO:
        return await self.order_repository.get_order_by_id(input_dto)

    async def search_orders(
        self,
        input_dto: SearchOrdersInputDTO,
    ) -> SearchOrdersOutputDTO:
        return await self.order_repository.search_orders(input_dto)

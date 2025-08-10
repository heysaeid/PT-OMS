from src.models.repositories.order.adapters.order_elastic_adapter import (
    OrderElasticAdapter,
)
from src.models.dtos.order.order_repository_interface_dtos import (
    GetOrderByIdQueryDTO,
    GetOrderByIdResponseDTO,
    SearchOrdersQueryDTO,
    SearchOrdersResponseDTO,
)


class OrderRepository:
    def __init__(self, elastic_adapter: OrderElasticAdapter):
        self.elastic_adapter = elastic_adapter

    async def get_order_by_id(
        self, input_dto: GetOrderByIdQueryDTO
    ) -> GetOrderByIdResponseDTO:
        return await self.elastic_adapter.get_order_by_id(input_dto)

    async def search_orders(
        self, input_dto: SearchOrdersQueryDTO
    ) -> SearchOrdersResponseDTO:
        return await self.elastic_adapter.search_orders(input_dto)

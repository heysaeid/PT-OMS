from pydantic import Field
from archipy.models.dtos.base_dtos import BaseDTO
from src.models.dtos.order.order_dto import OrderRoot
from src.models.types.base_dtos import SortType
from src.models.types.order_types import SortOrderByType


class GetOrderByIdInputDTO(BaseDTO):
    order_id: str


class GetOrderByIdOutputDTO(BaseDTO):
    order: OrderRoot


class SearchOrdersInputDTO(BaseDTO):
    national_id: str | None = None
    mobile: str | None = None
    email: str | None = None
    order_id: str | None = None
    order_status: str | None = None
    order_date: str | None = None

    page: int = Field(1, gt=0)
    size: int = Field(10, gt=0, le=100)

    sort_by: SortOrderByType = Field(
        SortOrderByType.CREATED_AT, description="Sort by field"
    )
    sort_order: SortType = Field(SortType.DESC, description="Sort order asc or desc")


class SearchOrdersOutputDTO(BaseDTO):
    total: int
    page: int
    size: int
    total_pages: int
    orders: list[OrderRoot]

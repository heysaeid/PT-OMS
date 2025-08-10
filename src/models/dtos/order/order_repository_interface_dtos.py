from pydantic import BaseModel, Field
from src.models.dtos.order.order_dto import OrderRoot
from src.models.types.base_dtos import SortType
from src.models.types.order_types import OrderStatusType, SortOrderByType


class OrderDocumentEntity(BaseModel):
    order: OrderRoot


class GetOrderByIdQueryDTO(BaseModel):
    order_id: str


class GetOrderByIdResponseDTO(BaseModel):
    order: OrderRoot


class SearchOrdersQueryDTO(BaseModel):
    order_id: str | None = None
    national_id: str | None = None
    mobile: str | None = None
    email: str | None = None
    order_status: OrderStatusType | None = None
    order_date: str | None = None
    encrypted: bool = True

    page: int = Field(1, gt=0)
    size: int = Field(10, gt=0, le=100)

    sort_by: SortOrderByType = Field(
        SortOrderByType.CREATED_AT,
        description="Sort by field",
    )
    sort_order: SortType = Field(SortType.DESC, description="Sort order asc or desc")


class SearchOrdersResponseDTO(BaseModel):
    total: int
    page: int
    size: int
    total_pages: int
    items: list[OrderRoot]

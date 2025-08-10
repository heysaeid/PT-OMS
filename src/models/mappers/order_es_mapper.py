from src.models.entities.order_index import OrderIndex
from src.models.dtos.order.order_repository_interface_dtos import OrderDocumentEntity
from src.models.dtos.order.order_repository_interface_dtos import (
    OrderDocumentEntity as POrderDocument,
)


def to_es(order_dto: POrderDocument) -> OrderIndex:
    return OrderIndex(**order_dto.model_dump())


def from_es(hit: OrderIndex) -> POrderDocument:
    return OrderDocumentEntity.model_validate(hit.to_dict())

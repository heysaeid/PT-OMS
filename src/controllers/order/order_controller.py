from typing import Annotated
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Query
from src.logics.order.order_logic import OrderLogic
from src.models.dtos.order.order_domain_interface_dtos import (
    GetOrderByIdInputDTO,
    GetOrderByIdOutputDTO,
    SearchOrdersInputDTO,
    SearchOrdersOutputDTO,
)
from src.configs.containers import ServiceContainer


router = APIRouter()


@router.get("/orders/{order_id}")
@inject
async def get_order_by_id(
    order_id: str,
    order_logic: Annotated[OrderLogic, Depends(Provide[ServiceContainer.order_logic])],
) -> GetOrderByIdOutputDTO:
    input_dto = GetOrderByIdInputDTO(order_id=order_id)
    return await order_logic.get_order_by_id(input_dto)


@router.get("/orders")
@inject
async def search_orders(
    input_dto: Annotated[SearchOrdersInputDTO, Query()],
    order_logic: Annotated[OrderLogic, Depends(Provide[ServiceContainer.order_logic])],
) -> SearchOrdersOutputDTO:
    return await order_logic.search_orders(input_dto)

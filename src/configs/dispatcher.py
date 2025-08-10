from fastapi import FastAPI
from src.controllers.order.order_controller import router as order_router


def set_dispatch_routes(app: FastAPI) -> None:
    app.include_router(order_router, prefix="/api/v1/orders", tags=["Order"])

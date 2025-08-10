"""Containers module."""

from dependency_injector import containers, providers
from archipy.adapters.elasticsearch.adapters import AsyncElasticsearchAdapter
from src.configs.config import Config
from src.models.repositories.order.adapters.order_elastic_adapter import (
    OrderElasticAdapter,
)
from src.models.repositories.order.order_repository import OrderRepository
from src.logics.order.order_logic import OrderLogic


class ServiceContainer(containers.DeclarativeContainer):
    _config = Config.global_config()

    wiring_config = containers.WiringConfiguration(
        packages=["src.controllers.order.order_controller"],
    )

    elastic_client = providers.Singleton(
        AsyncElasticsearchAdapter,
    )

    # Order
    order_elastic_adapter = providers.Singleton(
        OrderElasticAdapter,
        elastic_client=elastic_client,
    )
    order_repository = providers.Singleton(
        OrderRepository,
        elastic_adapter=order_elastic_adapter,
    )
    order_logic = providers.Singleton(
        OrderLogic,
        order_repository=order_repository,
    )

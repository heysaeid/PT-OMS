"""Containers module."""

from dependency_injector import containers
from src.configs.config import Config


class ServiceContainer(containers.DeclarativeContainer):
    _config = Config.global_config()

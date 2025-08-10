from archipy.configs.base_config import BaseConfig


class Config(BaseConfig):
    ORDER_INDEX_NAME: str = "orders-search"
    VAULT_ADDR: str = "http://vault:8200"
    VAULT_TOKEN: str = "dev-root-token"

    def customize(self) -> None:
        self.FASTAPI.PROJECT_NAME = "Order Repository Service"
        self.FASTAPI.DOCS_URL = "/docs"
        self.FASTAPI.RELOAD = True
        self.FASTAPI.WORKERS_COUNT = None


BaseConfig.set_global(Config())

settings = BaseConfig.global_config()

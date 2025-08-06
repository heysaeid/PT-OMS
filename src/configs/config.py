from archipy.configs.base_config import BaseConfig


class Config(BaseConfig):
    def customize(self) -> None:
        self.FASTAPI.PROJECT_NAME = "Order Repository Service"
        self.FASTAPI.DOCS_URL = "/docs"
        self.FASTAPI.RELOAD = True
        self.FASTAPI.WORKERS_COUNT = None


BaseConfig.set_global(Config())

import logging

import uvicorn
from src.configs.containers import ServiceContainer
from src.configs.config import Config
from archipy.helpers.utils.app_utils import AppUtils
from src.configs.dispatcher import set_dispatch_routes

container = ServiceContainer()

app = AppUtils.create_fastapi_app()
app.container = container

set_dispatch_routes(app)

if __name__ == "__main__":
    runtime_configs = Config.global_config()
    logging.basicConfig(
        level=runtime_configs.ENVIRONMENT.log_level,
        filename="../siteLogs.log",
        format="{'time':'%(asctime)s', 'name': '%(name)s', \
        'level': '%(levelname)s', 'message': '%(message)s'}",
    )

    uvicorn.run(
        "manage:app",
        access_log=runtime_configs.FASTAPI.ACCESS_LOG,
        backlog=runtime_configs.FASTAPI.BACKLOG,
        date_header=runtime_configs.FASTAPI.DATE_HEADER,
        forwarded_allow_ips=runtime_configs.FASTAPI.FORWARDED_ALLOW_IPS,
        host=runtime_configs.FASTAPI.SERVE_HOST,
        limit_concurrency=runtime_configs.FASTAPI.LIMIT_CONCURRENCY,
        limit_max_requests=runtime_configs.FASTAPI.LIMIT_MAX_REQUESTS,
        port=runtime_configs.FASTAPI.SERVE_PORT,
        proxy_headers=runtime_configs.FASTAPI.PROXY_HEADERS,
        reload=runtime_configs.FASTAPI.RELOAD,
        server_header=runtime_configs.FASTAPI.SERVER_HEADER,
        timeout_graceful_shutdown=runtime_configs.FASTAPI.TIMEOUT_GRACEFUL_SHUTDOWN,
        timeout_keep_alive=runtime_configs.FASTAPI.TIMEOUT_KEEP_ALIVE,
        workers=runtime_configs.FASTAPI.WORKERS_COUNT,
        ws_max_size=runtime_configs.FASTAPI.WS_MAX_SIZE,
        ws_per_message_deflate=runtime_configs.FASTAPI.WS_PER_MESSAGE_DEFLATE,
        ws_ping_interval=runtime_configs.FASTAPI.WS_PING_INTERVAL,
        ws_ping_timeout=runtime_configs.FASTAPI.WS_PING_TIMEOUT,
    )

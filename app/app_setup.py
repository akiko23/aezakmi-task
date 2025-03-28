from functools import partial

import uvicorn
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AppConfig, Config, HttpServerConfig
from app.depends_stub import Stub
from app.di import setup_di


def initialise_dependencies(app: FastAPI, config: Config) -> None:
    engine = create_engine(config.db.uri)
    session_factory = create_session_maker(engine)

    app.dependency_overrides[Stub(AsyncSession)] = partial(get_session, session_factory)
    app.dependency_overrides[Stub(Config)] = lambda: config
    app.dependency_overrides[Stub(NotificationService)] = get_notification_service


def create_app(app_cfg: AppConfig) -> FastAPI:
    app = FastAPI(title=app_cfg.title, description=app_cfg.description)
    return app


def create_http_server(
    app: FastAPI, http_server_cfg: HttpServerConfig
) -> uvicorn.Server:
    uvicorn_config = uvicorn.Config(
        app,
        host=http_server_cfg.host,
        port=http_server_cfg.port,
        log_level=http_server_cfg.log_level,
    )
    return uvicorn.Server(uvicorn_config)

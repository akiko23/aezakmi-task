import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from redis.asyncio import Redis

from aezakmi_task.controllers.metrics import router as metrics_router
from aezakmi_task.controllers.middlewares.metrics_middleware import (
    RequestCountMiddleware,
)
from aezakmi_task.controllers.middlewares.rate_limiting_middleware import (
    RateLimitMiddleware,
)
from aezakmi_task.controllers.notification import (
    router as notifications_router,
)
from aezakmi_task.di import setup_di


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await app_.container.close()


def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

    setup_dishka(container=ioc_container, app=application)
    application.container = ioc_container

    application.add_middleware(RequestCountMiddleware)
    application.add_middleware(RateLimitMiddleware, ioc_container=ioc_container)

    application.include_router(notifications_router, prefix="/api/v1")
    application.include_router(metrics_router)

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


container = setup_di()
app = create_app(container)

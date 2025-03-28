from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from dishka import AsyncContainer
from app.controllers.notification import router as notifications_router
from dishka.integrations.fastapi import setup_dishka

from app.di import setup_di

@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await app_.container.close()

def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

    setup_dishka(container=ioc_container, app=application)

    application.container = ioc_container
    application.include_router(notifications_router, prefix="/api/v1")

    @application.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return application


container = setup_di()
app = create_app(container)

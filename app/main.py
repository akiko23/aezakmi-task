from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from app.controllers.notification import router as notifications_router
from dishka.integrations.fastapi import setup_dishka

from app.di import setup_di

@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    app.container.close()

app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)
container = setup_di()
setup_dishka(container=container, app=app)

app.container = container
app.include_router(notifications_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

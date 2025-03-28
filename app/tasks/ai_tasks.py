import asyncio
import os

from collections.abc import AsyncGenerator

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from dishka import make_async_container, Scope, provide, Provider

from app.config import load_config
from app.repositories.notification_repository import NotificationRepository
from app.services.ai_service import analyze_text


cfg = load_config(os.getenv('AEZAKMI_TEST_CONFIG_PATH'))
celery_app = Celery('tasks', broker=cfg.redis.uri)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(cfg.db.uri, echo=True)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None, None]:
        async with sessionmaker() as session:
            yield session


container = make_async_container(DatabaseProvider())

def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@celery_app.task
def process_notification_analysis(notification_id: str):
    async def inner():
        async with container() as request_container:
            session = await request_container.get(AsyncSession)
            repo = NotificationRepository(session=session)
            notification = await repo.get(notification_id)
            if not notification:
                return

            await repo.update_status(notification_id, "processing")

            try:
                result = await analyze_text(notification.text)
                await repo.update_analysis(
                    notification_id,
                    category=result["category"],
                    confidence=result["confidence"],
                    status="completed"
                )
            except Exception as e:
                await repo.update_status(notification_id, "failed")
                raise  # Повторно выбрасываем исключение для логирования Celery

    return run_async(inner())

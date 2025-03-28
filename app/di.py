import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from dishka import make_async_container, Scope, provide, Provider
from redis.asyncio import Redis, ConnectionPool as RedisConnectionPool
from app.config import load_config, Config
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService, NotificationGateway


def config_provider() -> Provider:
    provider = Provider()

    cfg_path = os.getenv('AEZAKMI_TEST_CONFIG_PATH')
    provider.provide(lambda: load_config(cfg_path), scope=Scope.APP, provides=Config)
    return provider


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_client(self, cfg: Config) -> Redis:
        return Redis.from_url(cfg.redis.uri)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, cfg: Config) -> AsyncEngine:
        return create_async_engine(cfg.db.uri, echo=True)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None, None]:
        async with sessionmaker() as session:
            yield session


class NotificationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_notification_gateway(self, session: AsyncSession) -> NotificationGateway:
        return NotificationRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_notification_service(self, repository: NotificationGateway) -> NotificationService:
        return NotificationService(repository)


def setup_di():
    return make_async_container(
        config_provider(),
        DatabaseProvider(),
        NotificationProvider(),
        RedisProvider()
    )

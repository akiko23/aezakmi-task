import asyncio
import os
from asyncio import AbstractEventLoop

from dishka import Provider, Scope, make_async_container
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from httpx import AsyncClient, ASGITransport

from app.config import Config
from app.main import create_app
from app.models import Base
from app.di import DatabaseProvider, NotificationProvider, RedisProvider, config_provider

BASE_URL = "http://test"
TEST_CONFIG_PATH = "configs/app_test.toml"
SETUP_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/integration/scripts/setup_test_environment.sh'
RM_TEST_ENVIRONMENT_SCRIPT_PATH = 'tests/integration/scripts/rm_test_environment.sh'


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def _prepare_test_environment():
    os.system(f'chmod +x {SETUP_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{SETUP_TEST_ENVIRONMENT_SCRIPT_PATH}')
    yield
    os.system(f'chmod +x {RM_TEST_ENVIRONMENT_SCRIPT_PATH} && ./{RM_TEST_ENVIRONMENT_SCRIPT_PATH}')


# make sure that data will be lost after the end of the test
async def get_session(sessionmaker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
        await session.execute(text('truncate notifications;'))


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def ioc_container(_prepare_test_environment) -> AsyncContainer:
    mock_provider = Provider(scope=Scope.APP)
    mock_provider.provide(get_session, provides=AsyncSession, scope=Scope.REQUEST)
    container = make_async_container(
        config_provider(),
        DatabaseProvider(),
        NotificationProvider(),
        RedisProvider(),
        mock_provider,
    )
    yield container
    await container.close()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def engine(ioc_container: AsyncContainer) -> AsyncEngine:
    eng = await ioc_container.get(AsyncEngine)
    return eng


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def cfg(ioc_container: AsyncContainer) -> Config:
    cfg = await ioc_container.get(Config)
    return cfg


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def _make_migrations(engine: AsyncEngine, cfg: Config) -> None:
    async with engine.begin() as conn:
        await conn.execute(text('create schema if not exists test;'))
        await conn.execute(text('create extension if not exists "uuid-ossp";'))

        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_session(
        ioc_container: AsyncContainer, _make_migrations,
) -> AsyncGenerator[AsyncSession, None]:
    async with ioc_container() as request_container:
        session = await request_container.get(AsyncSession)
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_client(ioc_container: AsyncContainer, _make_migrations) -> AsyncClient:
    app = create_app(ioc_container)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=BASE_URL,
        headers={"Accept": "application/json"},
    ) as ac:
        yield ac

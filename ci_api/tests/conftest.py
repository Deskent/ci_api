import asyncio
from typing import Generator, Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from database.db import engine, async_session, get_db_session
from main import app

#
# @pytest.fixture(scope="session")
# def event_loop(request) -> Generator:
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope='session')
# async def db_session() -> AsyncSession:
#     async with engine.begin() as connection:
#         async with async_session(bind=connection) as session:
#             yield session
#             await session.flush()
#             await session.rollback()
#
#
# @pytest.fixture(scope='session')
# def override_get_db(db_session: AsyncSession) -> Callable:
#     async def _override_get_db():
#         yield db_session
#
#     return _override_get_db


# @pytest.fixture(scope='session')
# def get_app(override_get_db: Callable) -> FastAPI:
#     app.dependency_overrides[get_db_session] = override_get_db
#     return app


# @pytest.fixture(scope='session')
# def get_app() -> FastAPI:
#     return app


@pytest.fixture(scope='session')
def get_test_client_app() -> TestClient:
    client = TestClient(app=app)
    with client as session:
        yield session


@pytest.fixture(scope='session')
def base_url() -> str:
    return "/api/v1"

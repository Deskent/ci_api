import asyncio
from typing import Generator

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from database.db import engine, async_session


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()
#
#
# @pytest.fixture()
# def override_get_db(db_session: AsyncSession) -> Callable:
#     async def _override_get_db():
#         yield db_session
#
#     return _override_get_db
#
#
# @pytest.fixture()
# def app(override_get_db: Callable) -> FastAPI:
#     from main import app
#
#     app.dependency_overrides[get_db_session] = override_get_db
#     return app
#
#
# @pytest.fixture()
# def async_client(app: FastAPI) -> AsyncGenerator:
#     with TestClient(app=app, base_url="http://test") as ac:
#         yield ac

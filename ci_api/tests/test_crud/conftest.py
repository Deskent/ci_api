import asyncio
from typing import Generator

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from crud_class.crud import CRUD
from database.db import engine, async_session
from models.models import Video, Complex, User


@pytest.fixture
async def get_video():
    data = {
        "description": "Описание video 99",
        "name": "video 99",
        "number": 99,
        "duration": 99,
        "complex_id": 1,
        "file_name": "text_name.mp4"
    }
    video: Video = await CRUD.video.create(data)
    yield video
    await CRUD.video.delete_by_id(video.id)


@pytest.fixture
async def get_complex():
    data = {
        "description": "Описание комплекса 99",
        "name": "комплекс 99",
        "number": 99,
        "duration": 99
    }
    complex: Complex = await CRUD.complex.create(data)
    yield complex
    await CRUD.complex.delete(complex)


@pytest.fixture
def user_data():
    return {
        'username': "asddd",
        'last_name': "asdldd",
        'third_name': "asdtdd",
        'phone': "0234567890",
        'gender': 1,
        'password': "asd",
        'email': "asddd@asddd.ru",
        'rate_id': 1
    }


@pytest.fixture
async def get_user(user_data):
    user: User = await CRUD.user.get_by_email(user_data['email'])
    if user:
        await CRUD.user.delete(user)
    user: User = await CRUD.user.create(user_data)
    yield user
    await CRUD.user.delete(user)


#
#
# @pytest.fixture(scope="session")
# def event_loop(request) -> Generator:
#     """Create an instance of the default event loop for each test case."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture()
# async def db_session() -> AsyncSession:
#     async with engine.begin() as connection:
#         async with async_session(bind=connection) as session:
#             yield session
#             await session.flush()
#             await session.rollback()
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

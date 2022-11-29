# import pytest
# #
# from database.db import SQLModel, AsyncSession, engine, get_db_session
# from models.models import Complex, Video
# #
# #
# # # @pytest_asyncio.fixture
# # # def engine():
# # #     yield engine
# # #     # engine.sync_engine.dispose()
# # #
# # #
# # # @pytest_asyncio.fixture
# # # async def create(engine):
# # #     async with engine.begin() as conn:
# # #         await conn.run_sync(SQLModel.metadata.create_all)
# # #     yield
# # #     # async with engine.begin() as conn:
# # #     #     await conn.run_sync(SQLModel.metadata.drop_all)
# # #
# # #
# # @pytest.fixture
# # def session():
# #     return AsyncSession(engine)
# #     # async with AsyncSession(engine) as session:
# #     #     yield session
#
#
# @pytest.fixture
# def get_complex_data() -> dict:
#     return {
#                "description": "Описание комплекса 1",
#                "name": "комплекс 1",
#                "number": 999,
#                "next_complex_id": 2,
#                "duration": 0
#            }
#
#
# @pytest.fixture
# def get_video_data() -> dict:
#     return {
#         "description": "Описание тестового видео",
#         "name": "тест видео 1",
#         "file_name": "test_filename",
#         "complex_id": 1,
#         "duration": 30
#     }
# #
# #
# # @pytest_asyncio.fixture
# # async def session():
# #     return get_db_session
# #     # async for session in get_db_session():
# #     #     return session
# #
# #
# # # @pytest.mark.skip
# # @pytest_asyncio.mark.anyio
# async def test_add_complex(get_complex_data):
#     session = AsyncSession(engine)
#     new_complex = await Complex.add_new(session=session, **get_complex_data)
#     assert new_complex.id
#     await new_complex.delete(session=session)
#
#
# # @pytest.mark.skip
# # @pytest_asyncio.mark.anyio
# # async def test_add_video(session, get_video_data):
# #     new_video = await Video.add_new(session=session, **get_video_data)
# #
# #     assert new_video.id
# #     await new_video.delete(session=session)

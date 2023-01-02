from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.engine.result import Result

from config import db, logger, settings


DATABASE_URL: str = db.get_db_name()
engine = create_async_engine(DATABASE_URL, echo=settings.ECHO, future=True)


async def drop_db() -> None:
    logger.warning("DROP ALL tables from database.")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all, checkfirst=True)


async def create_db() -> None:
    logger.info("CREATE ALL tables to database.")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_session_response(query) -> Result:
    result = None
    async for session in get_db_session():
        result = await session.execute(query)

    return result


async def get_all(query) -> list:
    result = await get_session_response(query)

    return result.scalars().all()


async def get_first(query):
    result = await get_session_response(query)

    return result.scalars().first()

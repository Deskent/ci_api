from typing import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from config import db, logger, settings


DATABASE_URL: str = db.get_db_name()
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG, future=True)


async def drop_db() -> None:
    logger.warning("DROP ALL tables from database.")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all, checkfirst=True)


async def create_db() -> None:
    logger.info("CREATE ALL tables to database.")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

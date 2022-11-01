from typing import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel


class Database(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    RECREATE_DB: bool = False

    def get_db_name(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


env_file = './.env'
db = Database(_env_file=env_file, _env_file_encoding='utf-8')
DATABASE_URL: str = db.get_db_name()
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all, checkfirst=True)


async def create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

from pydantic import EmailStr
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from services.auth import auth_handler


class MySQLModel(SQLModel):

    async def save(self, session) -> 'MySQLModel':
        session.add(self)
        await session.commit()
        return self

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id_: int) -> 'MySQLModel':
        return await session.get(cls, id_)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list['MySQLModel']:
        response = await session.execute(select(cls).order_by(cls.id))

        return response.scalars().all()

    async def delete(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()


class UserModel(MySQLModel):

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: EmailStr) -> 'UserModel':
        query = select(cls).where(cls.email == email)
        response = await session.execute(query)

        return response.scalars().first()

    @classmethod
    async def get_by_phone(cls, session: AsyncSession, phone: str) -> 'UserModel':
        query = select(cls).where(cls.phone == phone)
        response = await session.execute(query)

        return response.scalars().first()

    @classmethod
    async def get_by_token(cls, session: AsyncSession, token: str) -> 'UserModel':
        user_id: int = auth_handler.decode_token(token)

        return await session.get(cls, user_id)

    async def is_password_valid(self, password: str) -> bool:
        return auth_handler.verify_password(password, self.password)

    async def get_user_token(self) -> str:
        return auth_handler.encode_token(self.id)

    @staticmethod
    async def get_hashed_password(password: str) -> str:
        return auth_handler.get_password_hash(password)

    @staticmethod
    async def get_user_id_from_email_token(token: str) -> str:
        return auth_handler.decode_token(token)

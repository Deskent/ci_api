from pydantic import EmailStr
from sqlmodel import SQLModel, select
from sqlmodel.engine.result import Result

from config import logger
from database.db import get_db_session
from services.auth import auth_handler


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


class MySQLModel(SQLModel):
    id: int = None

    async def save(self):
        async for session in get_db_session():
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def get_by_id(cls, id_: int) -> 'MySQLModel':
        query = select(cls).where(cls.id == id_)
        return await get_first(query)

    @classmethod
    async def get_all(cls) -> list:
        query = select(cls).order_by(cls.id)
        return await get_all(query)

    @classmethod
    async def delete_by_id(cls, id_: int) -> None:
        await cls._delete(id_)

    async def delete(self) -> None:
        await self._delete(obj=self)

    @classmethod
    async def _delete(cls, id_: int = 0, obj: SQLModel = None) -> None:
        async for session in get_db_session():
            if not obj and id_:
                obj = await cls.get_by_id(id_)
            if obj:
                await session.delete(obj)
                await session.commit()
                logger.debug(f"Object: {obj} deleted")

    @classmethod
    async def create(cls, data: dict):
        instance = cls(**data)
        return await instance.save()


class AdminModel(MySQLModel):
    email: EmailStr
    password: str

    @classmethod
    async def get_by_email(cls, email: EmailStr) -> 'User':
        query = select(cls).where(cls.email == email)
        return await get_first(query)

    @classmethod
    async def get_by_token(cls, token: str) -> 'User':
        user_id: int = auth_handler.decode_token(token)

        return await cls.get_by_id(user_id)

    @staticmethod
    async def get_hashed_password(password: str) -> str:
        return auth_handler.get_password_hash(password)

    @staticmethod
    async def get_user_id_from_email_token(token: str) -> str:
        return auth_handler.decode_token(token)

    async def is_password_valid(self, password: str) -> bool:
        return auth_handler.verify_password(password, self.password)

    async def get_user_token(self) -> str:
        return auth_handler.encode_token(self.id)

    @classmethod
    async def create(cls, data: dict) -> 'Administrator':
        data['password'] = await cls.get_hashed_password(data['password'])
        user = cls(**data)

        return await user.save()

class UserModel(AdminModel):
    phone: str
    email_code: str
    is_active: bool
    sms_message: str
    sms_call_code: str
    email_code: str
    level: int
    progress: int
    is_verified: bool

    @classmethod
    async def get_by_phone(cls, phone: str) -> 'User':
        query = select(cls).where(cls.phone == phone)
        return await get_first(query)

    @classmethod
    async def get_by_email_code(cls, email_code: str) -> 'User':
        query = select(cls).where(cls.email_code == email_code)
        return await get_first(query)

    async def activate(self) -> 'User':
        self.is_active = True
        return await self.save()

    async def deactivate(self) -> 'User':
        self.is_active = False
        return await self.save()

    async def clean_sms_code(self) -> 'User':
        self.sms_message = ''
        return await self.save()

    async def clean_sms_call_code(self) -> 'User':
        self.sms_call_code = ''
        return await self.save()

    async def clean_email_code(self) -> 'User':
        self.email_code = ''
        return await self.save()

    async def set_verified(self) -> 'User':
        if not self.is_verified:
            self.is_verified = True
            await self.save()
        return self

    async def set_not_verified(self) -> 'User':
        if self.is_verified:
            self.is_verified = False
            await self.save()
        return self

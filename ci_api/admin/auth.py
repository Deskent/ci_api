from pydantic import EmailStr
from sqladmin.authentication import AuthenticationBackend

from fastapi import Request

from config import settings, logger
from database.db import sessionmaker, engine, AsyncSession
from services.depends import check_user_credentials
from services.auth import AuthHandler

auth_handler = AuthHandler()


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username: EmailStr = form["username"]
        password: str = form["password"]
        logger.debug(f'User: {username} try to login as admin.')
        async_session = sessionmaker(
            engine, class_=AsyncSession
        )
        async with async_session() as session:
            user = await check_user_credentials(username, password, session)
            if user.is_admin:
                token: str = auth_handler.encode_token(user.id)
                request.session.update({"token": token})
                logger.debug(f'User: {username} logged as admin.')

                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token: str = request.session.get("token", None)

        return token is not None


authentication_backend = MyBackend(secret_key=settings.SECRET)

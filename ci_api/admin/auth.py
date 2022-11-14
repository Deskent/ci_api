from pydantic import EmailStr
from sqladmin.authentication import AuthenticationBackend

from fastapi import Request

from config import settings
from database.db import sessionmaker, engine, AsyncSession
from services.depends import check_user_exists
from services.auth import AuthHandler

auth_handler = AuthHandler()


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username: EmailStr = form["username"]
        password: str = form["password"]
        async_session = sessionmaker(
            engine, class_=AsyncSession
        )
        async with async_session() as session:
            user = await check_user_exists(username, password, session)
            if user.is_admin:
                token: str = auth_handler.encode_token(user.id)
                print(f"TOKEN: {token}")
                request.session.update({"token": token})

                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token: str = request.session.get("token", None)

        return token is not None
        # async_session = sessionmaker(
        #     engine, class_=AsyncSession
        # )
        # async with async_session() as session:
        #     if await verify_email_token(session, token):
        #         return True


authentication_backend = MyBackend(secret_key=settings.SECRET)

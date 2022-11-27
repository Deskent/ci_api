from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from config import settings, logger
from models.models import Administrator
from services.depends import check_admin_credentials
from services.user import validate_logged_user_data


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        user_login, errors = await validate_logged_user_data(form)
        logger.debug(f'User: {user_login.email} try to login as admin.')
        admin: Administrator = await check_admin_credentials(user_login)
        if admin:
            token: str = await admin.get_user_token()
            request.session.update({"token": token})
            logger.debug(f'Administrator: {admin.email} logged as admin.')

            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token: str = request.session.get("token", None)

        return token is not None


authentication_backend = MyBackend(secret_key=settings.SECRET)

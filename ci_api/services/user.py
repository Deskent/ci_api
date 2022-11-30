import datetime

import pydantic
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import FormData

from config import logger
from models.models import User, Administrator
from schemas.user import UserRegistration, UserLogin
from services.emails import send_verification_mail, EmailException


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


async def user_login(session: AsyncSession, user_data: UserLogin) -> User:
    if user_found := await User.get_by_email(session, user_data.email):
        if await user_found.is_password_valid(user_data.password):
            return user_found


async def check_email_exists(session: AsyncSession, email: EmailStr) -> bool:
    user: User = await User.get_by_email(session, email)
    admin: Administrator = await Administrator.get_by_email(session, email)

    return True if user or admin else False


async def check_user_phone_exists(session: AsyncSession, phone: str) -> User:
    if user := await User.get_by_phone(session, phone):
        return user


async def register_new_user(
        session: AsyncSession,
        user_data: UserRegistration,
):
    errors = {}
    email_exists: bool = await check_email_exists(session, user_data.email)
    if email_exists:
        errors = {'error': 'User with this email already exists'}
        return None, errors

    phone_exists: User = await check_user_phone_exists(session, user_data.phone)
    if phone_exists:
        errors = {'error': 'User with this phone already exists'}
        return None, errors

    user_data.password = await User.get_hashed_password(user_data.password)
    expired_at = datetime.datetime.now(tz=None) + datetime.timedelta(days=30)
    user = User(
        **user_data.dict(), is_verified=False,
        current_complex=1, is_admin=False, is_active=True, expired_at=expired_at
    )
    try:
        code: str = await send_verification_mail(user)
        user.email_code = code
    except EmailException:
        errors = {'error': "Неверный адрес почты"}
        return None, errors

    await user.save(session)
    logger.info(f"User with id {user.id} created")

    return user, errors


async def validate_logged_user_data(
        form: FormData
) -> tuple[UserLogin | None, dict]:

    try:
        user_data = UserLogin(email=form['email'], password=form['password'])

        return user_data, {}
    except pydantic.error_wrappers.ValidationError as err:
        logger.debug(err)

        return None, {'error': "Invalid email or password"}

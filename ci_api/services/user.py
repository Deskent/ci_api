import datetime

from fastapi.background import BackgroundTasks
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.user import UserRegistration
from models.models import User, Administrator
from services.auth import auth_handler
from services.emails import send_verification_mail
from config import logger


def get_login_token(user_id: int) -> str:
    return auth_handler.encode_token(user_id)


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


def check_password_correct(existing_password, entered_password) -> bool:
    return auth_handler.verify_password(entered_password, existing_password)


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
        tasks: BackgroundTasks
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

    user_data.password = auth_handler.get_password_hash(user_data.password)
    expired_at = datetime.datetime.now(tz=None) + datetime.timedelta(days=30)
    user = User(
        **user_data.dict(), is_verified=False,
        current_complex=1, is_admin=False, is_active=True, expired_at=expired_at
    )
    await user.save(session)
    tasks.add_task(send_verification_mail, user)
    logger.info(f"User with id {user.id} created")

    return user, errors

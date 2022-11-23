import dataclasses
import datetime

import pydantic
from fastapi import Request
from fastapi.background import BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import FormData
from fastapi.templating import Jinja2Templates

from config import logger
from models.models import User, Administrator
from schemas.user import UserRegistration, UserLogin
from services.auth import auth_handler
from services.emails import send_verification_mail


@dataclasses.dataclass
class EntryProfile:
    request: Request
    context: dict
    session: AsyncSession
    templates: Jinja2Templates

    async def user_entry(self):
        self.context.update({
            "request": self.request
        })
        form: FormData = await self.request.form()
        user_data, errors = await validate_logged_user_data(form)
        if not user_data and errors:
            self.context.update(**errors)
            logger.info(f'Login validation error: {errors["error"]}')

            return self.templates.TemplateResponse("entry.html", context=self.context)

        if user := await user_login(self.session, user_data):
            login_token: str = get_login_token(user.id)
            headers: dict[str, str] = get_bearer_header(login_token)
            self.request.session.update(token=login_token)

            return RedirectResponse('/profile', headers=headers)

        errors = {'error': "Invalid user or password"}
        self.context.update(**errors)

        return self.templates.TemplateResponse("entry.html", context=self.context)

    async def enter_profile(self):
        self.context.update({
            "request": self.request,
            "title": "Профиль",
            "head_title": "Личный кабинет"
        })
        token = self.request.session.get('token')
        if not token:
            return self.templates.TemplateResponse("entry.html", context=self.context)

        if not (user := await get_user_by_token(self.session, token)):
            self.context.update(errors="User not found")

            return self.templates.TemplateResponse("entry.html", context=self.context)

        self.context.update({
            "username": user.username,
            "last_name": user.last_name,
            "user_phone": user.phone,
            "user_email": user.email,
            "level": user.level,
            "subscribe_day": user.expired_at
        })
        return self.templates.TemplateResponse("profile.html", context=self.context)


def get_login_token(user_id: int) -> str:
    return auth_handler.encode_token(user_id)


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


def check_password_correct(existing_password, entered_password) -> bool:
    return auth_handler.verify_password(existing_password, entered_password)


async def user_login(session: AsyncSession, user_data: UserLogin) -> User:
    user_found: User = await User.get_by_email(session, user_data.email)
    password_correct: bool = check_password_correct(user_data.password, user_found.password)
    if user_found and password_correct:
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


async def get_user_by_token(
        session: AsyncSession,
        token: str
):
    user_id: int = auth_handler.decode_token(token)
    return await User.get_by_id(session, user_id)


async def validate_register_form(form: FormData) -> tuple[UserRegistration | None, dict]:
    try:
        user_data = UserRegistration(
            username=form['username'],
            last_name=form['last_name'],
            third_name=form['third_name'],
            phone=form['user_phone'],
            email=form['user_email'],
            password=form['password'],
            password2=form['password2'],
            gender=True if form['gender'] == 'male' else False,
            rate_id=1
        )
        return user_data, {}
    except pydantic.error_wrappers.ValidationError as err:
        logger.debug(err)
        error_text: str = err.errors()[0]['loc'][0]
        text = f'Invalid {error_text}'
        return None, {'error': text}


async def validate_logged_user_data(form: FormData) -> tuple[UserLogin | None, dict]:
    try:
        user_data = UserLogin(email=form['user_email'], password=form['password'])
        return user_data, {}
    except pydantic.error_wrappers.ValidationError as err:
        logger.debug(err)
        return None, {'error': "Invalid email or password"}

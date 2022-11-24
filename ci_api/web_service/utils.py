import dataclasses

import pydantic
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from schemas.user import UserRegistration, UserLogin
from services.user import user_login, get_login_token, get_bearer_header, get_user_by_token


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

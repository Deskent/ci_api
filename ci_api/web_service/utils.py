import dataclasses

import pydantic
from fastapi import Depends
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from database.db import get_db_session
from models.models import User, Video, Complex
from schemas.user import UserRegistration
from services.user import user_login, get_login_token, get_bearer_header, get_user_by_token, \
    validate_logged_user_data


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


async def get_session_token(request: Request) -> str:
    return request.session.get('token', '')


async def get_session_user(
        token: str = Depends(get_session_token),
        session: AsyncSession = Depends(get_db_session)
) -> User:
    if token:
        return await get_user_by_token(session, token)


async def get_session_context(
        user: User = Depends(get_session_user)
) -> dict:
    context = {}
    if user:
        context.update({
            "username": user.username,
            "last_name": user.last_name,
            "user_phone": user.phone,
            "user_email": user.email,
            "level": user.level,
            "subscribe_day": user.expired_at
        })
    return context


async def get_current_user_complex(
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session),
) -> Complex:
    return await Complex.get_by_id(session, user.current_complex)


async def get_complex_videos_list(
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session),
):
    return await Video.get_all_by_complex_id(session, user.current_complex)


async def get_session_video_by_id(
        video_id: int,
        session: AsyncSession = Depends(get_db_session),
) -> Video:
    return await Video.get_by_id(session, video_id)


#
# async def load_page(
#         request: Request,
#         session_context: dict = Depends(get_session_context)
# ):
#     page_name: str = str(request.url).split('/')[-1] + '.html'
#     if not session_context:
#         return templates.TemplateResponse("entry.html", context=context)
#     context.update(**session_context)
#     return templates.TemplateResponse(page_name, context=context)

from fastapi import Depends, Form, APIRouter
from pydantic import EmailStr
from starlette.responses import HTMLResponse

from config import templates
from models.models import User
from web_service.utils.title_context_func import update_title
from web_service.utils.titles_context import get_base_context, get_logged_user_context

router = APIRouter(tags=['web', 'check_email'])


@router.get("/check_email", response_class=HTMLResponse)
@router.post("/check_email", response_class=HTMLResponse)
async def check_email(
        context: dict = Depends(get_base_context),
        email: EmailStr = Form(...),
        email_token: str = Form(...)
):
    user: User = await User.get_by_email(email)
    if not user:
        error = 'Пользователь не найден'
        context.update(error=error)
        return templates.TemplateResponse(
            "index.html", context=update_title(context, 'index'))

    if user.email_code != email_token:
        error = 'Введен неверный токен'
        context.update(error=error)
        return templates.TemplateResponse(
            "check_email.html", context=update_title(context, "check_email.html"))

    if not user.is_verified:
        user.is_verified = True
        await user.save()

    context: dict = await get_logged_user_context(user=user, context=context)
    context.update(success='Аккаунт верифицирован')

    return templates.TemplateResponse(
        "profile.html", context=update_title(context, 'profile'))

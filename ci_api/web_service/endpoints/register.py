from fastapi import Depends, HTTPException, APIRouter
from loguru import logger
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config import templates
from schemas.user import UserRegistration
from services.user import register_new_user
from web_service.utils.title_context_func import update_title
from web_service.utils.titles_context import get_base_context
from web_service.utils.web_utils import redirect_logged_user_to_entry

router = APIRouter(tags=['web', 'register'])


@router.get("/registration", response_class=HTMLResponse)
async def web_register(
        context: dict = Depends(get_base_context)
):
    context.update(personal_data="/personal_data_info")
    return templates.TemplateResponse(
        "registration.html", context=update_title(context, "registration.html"))


@router.post("/registration", response_class=HTMLResponse)
async def web_register_post(
        request: Request,
        context: dict = Depends(get_base_context),
        form_data: UserRegistration = Depends(UserRegistration.as_form)
):
    if not form_data:
        errors = {'error': 'Пароли не совпадают'}
        context.update(**errors)
        logger.info(f'Field validation error: {errors["error"]}')

        return templates.TemplateResponse(
            "registration.html", context=update_title(context, "registration.html"))

    user, errors = await register_new_user(form_data)
    if user:
        return await redirect_logged_user_to_entry(user, request)

    if errors:
        context.update(**errors)
        return templates.TemplateResponse(
            "registration.html", context=update_title(context, "registration.html"))

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='New user registration unrecognized error'
    )

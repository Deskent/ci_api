from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from schemas.user_schema import UserRegistration
from services.user import register_new_user_web_context
from misc.web_context_class import WebContext
from web_service.utils.get_contexts import get_base_context

router = APIRouter(tags=['web', 'register'], include_in_schema=False)


@router.get("/registration", response_class=HTMLResponse)
async def web_register(
        context: dict = Depends(get_base_context)
):
    context.update(personal_data="/personal_data_info")
    web_context: WebContext = WebContext(context)
    web_context.template = "registration.html"
    return web_context.web_render()


@router.post("/registration", response_class=HTMLResponse)
async def web_register_post(
        context: dict = Depends(get_base_context),
        form_data: UserRegistration = Depends(UserRegistration.as_form)
):

    web_context: WebContext = await register_new_user_web_context(context, form_data)
    return web_context.web_render()

from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from config import templates
from web_service.handlers.common import restore_password
from web_service.utils.title_context_func import update_title
from web_service.utils.get_contexts import get_base_context

router = APIRouter(tags=['web', 'recover'])


@router.get("/forget1", response_class=HTMLResponse)
async def forget1(
        context: dict = Depends(get_base_context),
):
    return templates.TemplateResponse(
        "forget1.html", context=update_title(context, "forget_password.html"))


@router.post("/forget1", response_class=HTMLResponse)
async def forget1_post(
        restore_password: dict = Depends(restore_password),
):
    return restore_password


@router.get("/forget2", response_class=HTMLResponse)
async def forget2(
        context: dict = Depends(get_base_context),
):
    return templates.TemplateResponse(
        "forget2.html", context=update_title(context, "forget2.html"))


@router.get("/forget3", response_class=HTMLResponse)
async def forget3(
        context: dict = Depends(get_base_context),
):
    return templates.TemplateResponse(
        "forget3.html", context=update_title(context, "forget3.html"))

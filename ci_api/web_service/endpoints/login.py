from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from config import templates
from web_service.handlers.common import user_entry, set_new_password
from web_service.handlers.enter_with_sms import approve_sms_code, enter_by_sms
from web_service.utils.title_context_func import update_title
from web_service.utils.titles_context import get_base_context

router = APIRouter(tags=['web', 'login'])


@router.post("/entry", response_class=HTMLResponse)
async def entry(
        access_approved: templates.TemplateResponse = Depends(user_entry),
):
    return access_approved


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    if 'token' in request.session:
        request.session.clear()

    return RedirectResponse('/index')


@router.post("/newPassword", response_class=HTMLResponse)
async def newPassword(
        set_new_password: dict = Depends(set_new_password),
):
    return set_new_password


@router.get("/entry_sms", response_class=HTMLResponse)
async def entry_sms(
        context: dict = Depends(get_base_context),
):
    return templates.TemplateResponse(
        "entry_sms.html", context=update_title(context, "entry_sms.html"))


@router.post("/entry_sms", response_class=HTMLResponse)
async def entry_sms_posts(
        enter_by_sms: templates.TemplateResponse = Depends(enter_by_sms),
):
    return enter_by_sms


@router.post("/forget2", response_class=HTMLResponse)
@router.post("/forget3", response_class=HTMLResponse)
async def login_with_sms(
        check_sms_code: dict = Depends(approve_sms_code),
):
    return check_sms_code



from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from services.response_manager import WebContext, WebServiceResponser
from web_service.handlers.common import user_login_via_phone, set_new_password
from web_service.handlers.enter_with_sms import approve_sms_code, entry_via_sms_or_call
from web_service.utils.get_contexts import get_base_context

router = APIRouter(tags=['web', 'login'])


@router.post("/entry", response_class=HTMLResponse)
async def entry(
        web_context: WebContext = Depends(user_login_via_phone),
):
    return WebServiceResponser(web_context).render()


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
    web_context = WebContext(context=context)
    web_context.template = "entry_sms.html"
    return WebServiceResponser(web_context).render()


@router.post("/entry_sms", response_class=HTMLResponse)
async def entry_sms_posts(
        web_context: WebContext = Depends(entry_via_sms_or_call),
):
    return WebServiceResponser(web_context).render()


@router.post("/forget2", response_class=HTMLResponse)
@router.post("/forget3", response_class=HTMLResponse)
async def login_with_sms(
        web_context: WebContext = Depends(approve_sms_code),
):
    return WebServiceResponser(web_context).render()

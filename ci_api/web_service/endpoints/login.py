from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from schemas.user_schema import SmsCode
from misc.web_context_class import WebContext
from web_service.handlers.common import user_login_via_phone, set_new_password
from web_service.handlers.enter_with_sms import approve_sms_code_or_call_code, entry_via_sms_or_call
from web_service.utils.get_contexts import get_base_context, get_profile_page_context, \
    get_logged_user_context

router = APIRouter(tags=['web', 'login'])


@router.get("/entry", response_class=HTMLResponse)
async def entry_get(
        context: dict = Depends(get_profile_page_context),
):
    web_context = WebContext(context=context)
    web_context.template = "profile.html"
    return web_context.web_render()


@router.post("/entry", response_class=HTMLResponse)
async def entry_post(
        web_context: WebContext = Depends(user_login_via_phone),
):
    return web_context.web_render()


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    if 'token' in request.session:
        request.session.clear()

    return RedirectResponse('/index')


@router.post("/newPassword", response_class=HTMLResponse)
async def newPassword(
        context: dict = Depends(get_logged_user_context),
        old_password: str = Form(...),
        password: str = Form(...),
        password2: str = Form(...)
):
    web_context: WebContext = await set_new_password(
        context=context, old_password=old_password, password=password, password2=password2)
    web_context.context = await get_profile_page_context(web_context.context)

    return web_context.web_render()


@router.get("/entry_sms", response_class=HTMLResponse)
async def entry_sms(
        context: dict = Depends(get_base_context),
):
    web_context = WebContext(context=context)
    web_context.template = "entry_sms.html"

    return web_context.web_render()


@router.post("/entry_sms", response_class=HTMLResponse)
async def entry_sms_posts(
        web_context: WebContext = Depends(entry_via_sms_or_call),
):
    return web_context.web_render()


@router.post("/forget2", response_class=HTMLResponse)
@router.post("/forget3", response_class=HTMLResponse)
async def login_with_sms(
        request: Request,
        sms_input_1: str = Form(...),
        sms_input_2: str = Form(...),
        sms_input_3: str = Form(...),
        sms_input_4: str = Form(...),
        user_id: int = Form(...),
        context: dict = Depends(get_base_context)
):
    code: SmsCode = SmsCode(code=''.join((sms_input_1, sms_input_2, sms_input_3, sms_input_4)))
    web_context: WebContext = await approve_sms_code_or_call_code(
        request=request, context=context, user_id=user_id, code=code.code)
    web_context.context = await get_profile_page_context(web_context.context)

    return web_context.web_render()

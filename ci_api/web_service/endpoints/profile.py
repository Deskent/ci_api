from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from database.models import User
from schemas.user_schema import UserEditProfile
from misc.web_context_class import WebContext
from web_service.handlers.profile_web_contexts import get_edit_profile_web_context
from web_service.utils.get_contexts import get_logged_user_context, get_profile_page_context, \
    get_user_browser_session

router = APIRouter(tags=['web', 'profile'])


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
async def profile(
        context: dict = Depends(get_profile_page_context),
):
    web_context = WebContext(context=context)
    web_context.template = "profile.html"
    return web_context.web_render()


@router.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile(
        context: dict = Depends(get_logged_user_context),
):
    web_context = WebContext(context=context)
    web_context.template = "edit_profile.html"
    return web_context.web_render()


@router.post("/edit_profile", response_class=HTMLResponse)
async def edit_profile_post(
        username: str = Form(),
        last_name: str = Form(),
        third_name: str = Form(),
        email: EmailStr = Form(),
        phone: str = Form(),
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_browser_session)
):
    user_data = UserEditProfile(
        username=username, last_name=last_name, third_name=third_name, email=email, phone=phone)
    web_context: WebContext = await get_edit_profile_web_context(
        context=context, user_data=user_data, user=user)
    web_context.context = await get_profile_page_context(web_context.context)

    return web_context.web_render()

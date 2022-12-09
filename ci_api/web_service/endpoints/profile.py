from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from services.response_manager import WebContext, WebServiceResponser
from web_service.handlers.profile_web_contexts import get_edit_profile_web_context
from web_service.utils.get_contexts import get_logged_user_context, get_profile_page_context

router = APIRouter(tags=['web', 'profile'])


# TODO привести к единому АПИ
# TODO сделать отписку ?


@router.get("/profile", response_class=HTMLResponse)
@router.post("/profile", response_class=HTMLResponse)
async def profile(
        context: dict = Depends(get_profile_page_context),
):
    web_context = WebContext(context=context)
    web_context.template = "profile.html"
    return WebServiceResponser(web_context).render()


@router.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile(
        context: dict = Depends(get_logged_user_context),
):
    web_context = WebContext(context=context)
    web_context.template = "edit_profile.html"
    return WebServiceResponser(web_context).render()


@router.post("/edit_profile", response_class=HTMLResponse)
async def edit_profile_post(
    web_context: WebContext = Depends(get_edit_profile_web_context)
):
    return WebServiceResponser(web_context).render()


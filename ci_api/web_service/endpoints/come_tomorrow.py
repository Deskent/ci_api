from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from services.web_context_class import WebContext
from web_service.utils.get_contexts import get_logged_user_context


router = APIRouter(tags=['web', 'tomorrow'])


@router.get("/come_tomorrow", response_class=HTMLResponse)
async def come_tomorrow(
        context: dict = Depends(get_logged_user_context),
):
    web_context = WebContext(context)
    web_context.template = "come_tomorrow.html"

    return web_context.web_render()

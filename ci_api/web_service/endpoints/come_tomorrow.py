from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from config import templates
from web_service.utils.title_context_func import get_page_titles
from web_service.utils.get_contexts import get_logged_user_context


router = APIRouter(tags=['web', 'tomorrow'])


@router.get("/come_tomorrow", response_class=HTMLResponse)
async def come_tomorrow(
        context: dict = Depends(get_logged_user_context),
):
    return templates.TemplateResponse(
        "come_tomorrow.html", context=get_page_titles(context, "come_tomorrow.html")
    )

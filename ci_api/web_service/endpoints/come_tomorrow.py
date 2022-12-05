from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from config import templates
from web_service.utils.title_context_func import update_title
from web_service.utils.titles_context import get_logged_user_context


router = APIRouter(tags=['web', 'tomorrow'])


@router.get("/come_tomorrow", response_class=HTMLResponse)
async def come_tomorrow(
        context: dict = Depends(get_logged_user_context),
):
    return templates.TemplateResponse(
        "come_tomorrow.html", context=update_title(context, "come_tomorrow.html")
    )

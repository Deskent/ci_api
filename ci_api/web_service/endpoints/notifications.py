from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse, RedirectResponse

from config import templates
from crud_class.crud import CRUD
from database.models import User
from web_service.utils.title_context_func import get_page_titles
from web_service.utils.get_contexts import get_user_browser_session, get_logged_user_context

router = APIRouter(tags=['web', 'notifications'])


@router.get("/delete_notification/{notification_id}", response_class=HTMLResponse)
async def delete_notification(
        notification_id: int,
):
    await CRUD.notification.delete_by_id(notification_id)

    return RedirectResponse("/complexes_list")


@router.get("/notifications", response_class=HTMLResponse)
async def notifications_get(
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_browser_session)
):
    notifications: list = await CRUD.notification.get_all_by_user_id(user.id)
    context.update(notifications=notifications)

    return templates.TemplateResponse(
        "notifications.html", context=get_page_titles(context, "notifications.html"))

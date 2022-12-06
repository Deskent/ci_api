from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse, RedirectResponse

from config import templates
from models.models import User, Notification
from web_service.utils.title_context_func import update_title
from web_service.utils.get_contexts import get_user_from_context, get_logged_user_context

router = APIRouter(tags=['web', 'notifications'])


@router.get("/delete_notification/{notification_id}", response_class=HTMLResponse)
async def delete_notification(
        notification_id: int,
):
    await Notification.delete_by_id(notification_id)

    return RedirectResponse("/complexes_list")


@router.get("/notifications", response_class=HTMLResponse)
async def notifications_get(
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_from_context)
):
    notifications: list = await Notification.get_all_by_user_id(user.id)
    context.update(notifications=notifications)

    return templates.TemplateResponse(
        "notifications.html", context=update_title(context, "notifications.html"))

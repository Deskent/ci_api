import datetime

from fastapi import APIRouter, status, Depends, UploadFile

from api.web_api_utils import set_avatar_from_file_web_context
from config import logger
from models.models import User, Mood
from schemas.complexes_videos import ComplexesListWithViewedAndNot
from schemas.user_schema import EntryModalWindow, UserMood
from services.complexes_web_context import get_complexes_list_web_context
from crud_class.crud import CRUD
from services.utils import get_current_datetime
from services.videos_methods import get_viewed_complex_response
from services.web_context_class import WebContext
from web_service.utils.get_contexts import get_user_browser_session

router = APIRouter(prefix="/web", tags=['WebApi'])


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed_web(
        complex_id: int,
        user: User = Depends(get_user_browser_session)
):
    return await get_viewed_complex_response(user=user, complex_id=complex_id)


@router.get("/complex/list", response_model=ComplexesListWithViewedAndNot)
async def get_complexes_list_web(
        user: User = Depends(get_user_browser_session)
):
    """Return viewed_complexes, today_complex, not_viewed_complexes, user"""

    web_context: WebContext = await get_complexes_list_web_context({}, user)
    return web_context.api_render()


@router.post(
    "/upload_avatar_as_file",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_avatar_as_file(
        file: UploadFile,
        user: User = Depends(get_user_browser_session)
):
    logger.debug(f"File received: {file.filename}")
    web_context: WebContext = await set_avatar_from_file_web_context(
        context={}, user=user, file=file)
    return web_context.api_render()


@router.get(
    "/check_first_entry",
    status_code=status.HTTP_200_OK,
    response_model=EntryModalWindow
)
async def check_first_entry_or_new_user(
        user: User = Depends(get_user_browser_session)
):
    """
    Return new_user = True if user registered now have first entry.

    Return today_first_entry = True and list of emojies if user first time entry today.

    Return user as JSON else.

    :param user: Logged user
    :return: {
            user: dict
            emojies: list[dict] = []
            new_user: bool = False
            today_first_entry: bool = False
        }
    """
    new_user: bool = user.last_entry is None
    if new_user:
        await CRUD.user.set_subscribe_to(days=7, user=user)

        return EntryModalWindow(user=user, new_user=True)

    today_first_entry: bool = user.last_entry.date() != get_current_datetime().date()
    if today_first_entry and user.is_active and user.level > 6:
        await CRUD.user.set_last_entry_today(user)
        emojies: list[Mood] = await CRUD.mood.get_all()

        return EntryModalWindow(user=user, emojies=emojies, today_first_entry=True)

    user: User = await CRUD.user.set_last_entry_today(user)
    return EntryModalWindow(user=user)


@router.post(
    "/set_user_mood",
    status_code=status.HTTP_202_ACCEPTED
)
async def set_user_mood(
        mood: UserMood,
        user: User = Depends(get_user_browser_session)
):
    """
    Set mood for user

    :param mood: {
               "mood_id": 0
           }
    :param user: Logged user
    :return: null
    """
    await CRUD.user.set_mood(mood.mood_id, user=user)

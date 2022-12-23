from fastapi import APIRouter, status, Depends, UploadFile

from api.web_api_utils import set_avatar_from_file_web_context
from config import logger
from crud_class.crud import CRUD
from database.models import User, Mood, Video
from schemas.complexes_videos import ComplexesListWithViewedAndNot, ComplexViewedCheckLevelUp
from schemas.user_schema import EntryModalWindow, UserMood
from services.complexes_web_context import get_complexes_list_web_context
from services.videos_methods import get_viewed_complex_response
from misc.web_context_class import WebContext
from web_service.utils.get_contexts import get_user_browser_session

router = APIRouter(prefix="/web", tags=['WebApi'])


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=ComplexViewedCheckLevelUp
)
async def complex_viewed_web(
        complex_id: int,
        user: User = Depends(get_user_browser_session)
):
    """Return

    if complex first time viewed

        {

            "level_up": True,

            "new_level": integer - User level,

            "next_complex_duration": integer - next complex duration

        }

    else

        {

            "level_up": False

        }
    """

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
    Return today_first_entry = True and list of emojies if user
    entered first time today and user level > 6.

    Return new_user = True if user registered now have first entry and
    object 'hello_video' with hello video data.

    Return is_expired = True if user subscribe expired.

    Return user as JSON else.

    :param user: Logged user

    :return: JSON
    """


    if await CRUD.user.is_new_user(user):
        user: User = await CRUD.user.set_last_entry_today(user)
        await CRUD.user.set_subscribe_to(days=7, user=user)
        hello_video: Video = await CRUD.video.get_hello_video()

        return EntryModalWindow(user=user, new_user=True, hello_video=hello_video)

    if await CRUD.user.is_first_entry_today(user):
        user: User = await CRUD.user.set_last_entry_today(user)
        if not await CRUD.user.check_is_active(user):
            return EntryModalWindow(user=user, is_expired=True)
        elif user.level > 6:
            emojies: list[Mood] = await CRUD.mood.get_all()

            return EntryModalWindow(
                user=user, emojies=emojies, today_first_entry=True)

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

    :return: null
    """
    await CRUD.user.set_mood(mood.mood_id, user=user)

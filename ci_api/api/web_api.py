import datetime

from fastapi import APIRouter, status, Depends, UploadFile

from api.web_api_utils import set_avatar_from_file_web_context
from config import logger
from models.models import User, Mood
from schemas.complexes_videos import ComplexesListWithViewedAndNot
from schemas.user_schema import EntryModalWindow
from services.complexes_web_context import get_complexes_list_web_context
from crud_class.crud import CRUD
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


@router.post(
    "/check_first_entry",
    status_code=status.HTTP_200_OK,
    response_model=EntryModalWindow
)
async def check_first_entry(
    user: User = Depends(get_user_browser_session)
):
    new_user: bool = user.last_entry is None
    if new_user:
        emojies: list[Mood] = await CRUD.mood.all()
        run_modal_window: bool = True
        await CRUD.user.set_subscribe_to(days=7, user=user)

        return EntryModalWindow(user=user, emojies=emojies, run_modal_window=run_modal_window)

    today_first_entry: bool = user.last_entry.day == datetime.datetime.today().day
    if today_first_entry and user.is_active and user.level > 6:
        await CRUD.user.set_last_entry_today(user)
        emojies: list[Mood] = await CRUD.mood.all()
        run_modal_window: bool = True

        return EntryModalWindow(user=user, emojies=emojies, run_modal_window=run_modal_window)

    return EntryModalWindow(user=user)

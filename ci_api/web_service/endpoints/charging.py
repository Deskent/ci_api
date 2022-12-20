from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from config import templates
from models.models import User, Complex, Video
from services.complexes_and_videos import (
    get_viewed_videos_ids, calculate_videos_to_next_level
)
from services.models_cache.crud import CRUD
from services.utils import convert_seconds_to_time, convert_to_minutes
from web_service.utils.get_contexts import get_logged_user_context, get_user_from_context
from web_service.utils.title_context_func import get_page_titles

router = APIRouter(tags=['web', 'charging'])


@router.get("/complexes_list", response_class=HTMLResponse)
async def complexes_list_web(
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_from_context)
):
    videos: list[Video] = await CRUD.video.get_all_by_complex_id(user.current_complex)

    complexes: list[Complex] = await CRUD.complex.get_all()
    viewed_complexes_ids: list[int] = await CRUD.viewed_complex.get_all_viewed_complexes_ids(user.id)
    for complex_ in complexes:
        complex_.duration = convert_to_minutes(complex_.duration)
    videos_to_next_level: int = calculate_videos_to_next_level(user, videos)

    context.update(
        viewed_complexes=viewed_complexes_ids, complexes=complexes,
        to_next_level=videos_to_next_level
    )
    return templates.TemplateResponse(
        "complexes_list.html", context=get_page_titles(context, "complexes_list.html")
    )


@router.get("/videos_list/{complex_id}", response_class=HTMLResponse)
@router.post("/videos_list/{complex_id}", response_class=HTMLResponse)
async def videos_list_web(
        complex_id: int,
        context: dict = Depends(get_logged_user_context),
        user: User = Depends(get_user_from_context),
):
    current_complex: Complex = await CRUD.complex.get_by_id(complex_id)
    next_complex: Complex = await CRUD.complex.next_complex(current_complex)
    next_complex.duration = convert_seconds_to_time(next_complex.duration)

    # Calculate video number to next level for current complex
    videos: list[Video] = await CRUD.video.get_all_by_complex_id(complex_id)
    if videos:
        viewed_videos: tuple[int] = await get_viewed_videos_ids(user)

        videos_to_next_level: int = calculate_videos_to_next_level(user, videos)

        context.update(
            to_next_level=videos_to_next_level,
            viewed_videos=viewed_videos
        )
    for video in videos:
        video.duration = convert_seconds_to_time(video.duration)
    context.update(current_complex=current_complex, videos=videos, next_complex=next_complex)

    return templates.TemplateResponse(
        "videos_list.html", context=get_page_titles(context, "videos_list.html"))

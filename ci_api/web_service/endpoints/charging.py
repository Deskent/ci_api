from fastapi import APIRouter
from starlette.responses import HTMLResponse

from services.complexes_and_videos import get_viewed_videos_ids, get_not_viewed_videos_ids, \
    calculate_viewed_videos_duration, calculate_videos_to_next_level, set_video_viewed, \
    check_level_up
from services.utils import convert_seconds_to_time
from web_service.utils import *
from web_service.utils import get_current_user_complex, get_complex_videos_list, \
    get_session_context, get_profile_context, get_session_video, get_session_user

router = APIRouter(tags=['web', 'charging'])


@router.get("/charging", response_class=HTMLResponse)
@router.post("/charging", response_class=HTMLResponse)
async def charging(
        current_complex: Complex = Depends(get_current_user_complex),
        videos: list = Depends(get_complex_videos_list),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
        session: AsyncSession = Depends(get_db_session)
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    user: User = session_context['user']

    # Calculate video number to next level for current complex
    if videos:
        viewed_videos: tuple[int] = await get_viewed_videos_ids(session, user)
        not_viewed_videos: tuple[int] = await get_not_viewed_videos_ids(videos, viewed_videos)
        not_viewed_videos_duration: int = await calculate_viewed_videos_duration(
            session, not_viewed_videos
        )
        complex_less_time: int = convert_seconds_to_time(
            current_complex.duration - not_viewed_videos_duration
        ).minute

        videos_to_next_level: int = calculate_videos_to_next_level(user, videos)

        context.update(
            to_next_level=videos_to_next_level, complex_less_time=complex_less_time,
            viewed_videos=viewed_videos
        )
    for video in videos:
        video.duration = convert_seconds_to_time(video.duration)
    context.update(current_complex=current_complex, videos=videos, **session_context)

    return templates.TemplateResponse("videos_list.html", context=context)


@router.get("/startCharging/{video_id}", response_class=HTMLResponse)
async def start_charging(
        video: Video = Depends(get_session_video),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context)
):
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    context.update(video=video, **session_context)
    return templates.TemplateResponse("startCharging.html", context=context)


@router.post("/finish_charging", response_class=HTMLResponse)
async def finish_charging(
        current_complex: Complex = Depends(get_current_user_complex),
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
        user: User = Depends(get_session_user),
        session: AsyncSession = Depends(get_db_session),
        video_id: int = Form()
):
    if not await set_video_viewed(session, user, video_id):
        return RedirectResponse("/charging")

    old_user_level = user.level
    new_user: User = await check_level_up(session, user)
    context.update(**session_context, current_complex=current_complex)
    if new_user.level <= old_user_level:
        return RedirectResponse("/charging")

    current_complex: Complex = await Complex.get_by_id(session, user.current_complex)
    context.update(user=new_user, current_complex=current_complex)
    return templates.TemplateResponse("new_level.html", context=context)




# @router.get("/complexes_list", response_class=HTMLResponse)
# async def complexes_list(
#         current_complex: Complex = Depends(get_current_user_complex),
#         videos: list = Depends(get_complex_videos_list),
#         session_context: dict = Depends(get_session_context),
#         context: dict = Depends(get_profile_context),
# ):
#     print(current_complex)
#     return templates.TemplateResponse("videos_list.html", context=context)

from fastapi import APIRouter
from starlette.responses import HTMLResponse

from models.models import ViewedComplex, Notification
from services.complexes_and_videos import (
    get_viewed_videos_ids, get_not_viewed_videos_ids,
    calculate_viewed_videos_duration, calculate_videos_to_next_level, is_video_viewed,
    check_level_up
)
from services.utils import convert_seconds_to_time, convert_to_minutes
from web_service.utils import *
from web_service.utils import (
    get_current_user_complex, get_complex_videos_list,
    get_session_context, get_profile_context, get_session_video, get_session_user
)

router = APIRouter(tags=['web', 'charging'])


@router.get("/videos_list/{complex_id}", response_class=HTMLResponse)
@router.post("/videos_list/{complex_id}", response_class=HTMLResponse)
async def videos_list(
        complex_id: int,
        session_context: dict = Depends(get_session_context),
        context: dict = Depends(get_profile_context),
):
    current_complex: Complex = await Complex.get_by_id(complex_id)
    if not session_context:
        return templates.TemplateResponse("entry.html", context=context)
    user: User = session_context['user']

    # Calculate video number to next level for current complex
    videos: list[Video] = await Video.get_all_by_complex_id(complex_id)
    if videos:
        viewed_videos: tuple[int] = await get_viewed_videos_ids(user)
        not_viewed_videos: tuple[int] = await get_not_viewed_videos_ids(videos, viewed_videos)
        not_viewed_videos_duration: int = await calculate_viewed_videos_duration(
            not_viewed_videos
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
@router.post("/startCharging/{video_id}", response_class=HTMLResponse)
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
        context: dict = Depends(get_full_context),
        user: User = Depends(get_session_user),
        video_id: int = Form()
):
    if not user:
        return templates.TemplateResponse("entry.html", context=context)
    current_video: Video = await Video.get_by_id(video_id)
    next_video_id: int = await current_video.get_next_video_id()

    if not next_video_id:
        return templates.TemplateResponse("come_tomorrow.html", context=context)

    context.update(video=next_video_id)

    if not await is_video_viewed(user, video_id):
        return RedirectResponse(f"/startCharging/{id}")

    old_user_level = user.level
    new_user: User = await check_level_up(user)
    context.update(current_complex=current_complex)
    if new_user.level <= old_user_level:
        return RedirectResponse(f"/startCharging/{next_video_id}")

    current_complex: Complex = await Complex.get_by_id(user.current_complex)
    context.update(user=new_user, current_complex=current_complex)

    return templates.TemplateResponse("new_level.html", context=context)


@router.get("/complexes_list", response_class=HTMLResponse)
async def complexes_list(
        context: dict = Depends(get_full_context),
        videos: list = Depends(get_complex_videos_list),
):
    user: User = context['user']
    if not user:
        return templates.TemplateResponse("entry.html", context=context)
    if await ViewedComplex.is_last_viewed_today(user.id):
        return RedirectResponse("/come_tomorrow")

    complexes: list[Complex] = await Complex.get_all()
    viewed_complexes: list[
        ViewedComplex] = await ViewedComplex.get_all_viewed_complexes(user.id)
    for complex_ in complexes:
        complex_.duration = convert_to_minutes(complex_.duration)
    viewed_complexes_ids: tuple[int] = tuple(elem.complex_id for elem in viewed_complexes)
    videos_to_next_level: int = calculate_videos_to_next_level(user, videos)

    context.update(
        viewed_complexes=viewed_complexes_ids, complexes=complexes,
        to_next_level=videos_to_next_level
    )

    return templates.TemplateResponse("complexes_list.html", context=context)


@router.get("/delete_notification/{notification_id}", response_class=HTMLResponse)
async def delete_notification(
        notification_id: int,
        context: dict = Depends(get_full_context),
):
    user: User = context['user']
    if not user:
        return templates.TemplateResponse("entry.html", context=context)
    await Notification.delete_by_id(notification_id)

    return RedirectResponse(f"/videos_list/{user.current_complex}")


@router.get("/come_tomorrow", response_class=HTMLResponse)
async def come_tomorrow(
        context: dict = Depends(get_full_context),
):
    user: User = context['user']
    if not user:
        return templates.TemplateResponse("entry.html", context=context)
    return templates.TemplateResponse("come_tomorrow.html", context=context)

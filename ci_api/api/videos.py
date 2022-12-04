from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.responses import FileResponse

from config import settings, logger
from exc.payment.exceptions import UserNotFoundError
from models.models import Video, User
from schemas.complexes_videos import VideoViewed
from services.complexes_and_videos import is_video_viewed
from services.depends import is_user_active, get_logged_user

router = APIRouter(prefix="/videos", tags=['Videos'])


@router.get("/{video_id}", dependencies=[Depends(is_user_active)])
async def get_video(
        video_id: int,
):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """
    logger.debug(f"Video requested: {video_id}")
    video: Video = await Video.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    full_path: Path = settings.MEDIA_DIR / video.file_name
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {video.file_name} not found")
    logger.debug(f"Video requested: {video_id}:  OK")

    return FileResponse(path=str(full_path), media_type='video/mp4')


@router.post("/viewed", status_code=status.HTTP_200_OK)
async def viewed_video(
        viewed: VideoViewed = Body(...),
):
    result = {}
    logger.debug(f"VIEWED: {viewed}")
    video: Video = await Video.get_by_id(viewed.video_id)
    if video:
        next_video = await video.next_video_id()
        if next_video:
            result.update(next_video=next_video)

    phone = viewed.user_tel.strip()[1:].replace('(', '').replace(')', '').replace('-', '')
    print("PHONE:", phone)
    user: User = await User.get_by_phone(phone)
    print("USER:", user)
    if user:
        result.update(user=user)
    return result
#
#
# async def get_viewed_video_response(user: User, video_id: int):
#     context = {}
#     if not user:
#         context.update(
#             template="entry.html",
#             to_raise=UserNotFoundError
#         )
#         return context
#
#     current_video: Video = await Video.get_by_id(video_id)
#     next_video_id: int = await current_video.next_video_id()
#
#     if not next_video_id:
#         context.update(
#             template="come_tomorrow.html",
#             api_data=dict(data="come tomorrow")
#         )
#         return context
#
#     context.update(video=next_video_id)
#
#     if not await is_video_viewed(user, video_id):
#         context.update(
#             redirect=f"/startCharging/{next_video_id}",
#             api_data=dict(data="come tomorrow")
#         )
#         return context
#
#     old_user_level = user.level
#     new_user: User = await check_level_up(user)
#     context.update(current_complex=current_complex)
#     if new_user.level <= old_user_level:
#         return RedirectResponse(f"/startCharging/{next_video_id}")
#
#     current_complex: Complex = await Complex.get_by_id(user.current_complex)
#     context.update(user=new_user, current_complex=current_complex)
#
#     return templates.TemplateResponse("new_level.html", context=context)

from pathlib import Path

from fastapi import Depends, HTTPException, status
from starlette.responses import RedirectResponse

from config import settings
from exc.payment.exceptions import UserNotFoundError, ComplexNotFoundError, VideoNotFoundError
from models.models import User, Video, Complex
from services.user import get_bearer_header
from web_service.utils.titles_context import get_session_user


async def get_current_user_complex(
        user: User = Depends(get_session_user),
) -> Complex:
    if user:
        return await Complex.get_by_id(user.current_complex)

    raise ComplexNotFoundError


async def get_complex_videos_list(
        user: User = Depends(get_session_user),
) -> list[Video]:
    if user:
        return await Video.get_all_by_complex_id(user.current_complex)

    raise UserNotFoundError


async def get_session_video_by_id(
        video_id: int,
) -> Video:
    if video_id:
        return await Video.get_by_id(video_id)

    raise VideoNotFoundError


async def get_session_video(
        video: Video = Depends(get_session_video_by_id),
) -> Video:
    file_path: Path = settings.MEDIA_DIR / video.file_name
    if file_path.exists():
        return video

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'File {video.file_name} not found'
    )


async def login_user(user, request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/entry', headers=headers)

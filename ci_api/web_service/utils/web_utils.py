from pathlib import Path

from fastapi import HTTPException, status
from starlette.responses import RedirectResponse

from config import settings
from models.models import Video
from services.user import get_bearer_header


async def get_session_video(video_id: int) -> Video:
    video: Video = await Video.get_by_id(video_id)
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

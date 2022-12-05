from pathlib import Path

from fastapi import Request
from starlette.responses import RedirectResponse

from config import settings
from exc.exceptions import FileNotFound
from models.models import Video, User
from services.user import get_bearer_header


async def get_checked_video(video_id: int) -> Video:
    video: Video = await Video.get_by_id(video_id)
    file_path: Path = settings.MEDIA_DIR / video.file_name
    if file_path.exists():
        return video

    raise FileNotFound
    # raise HTTPException(
    #     status_code=status.HTTP_404_NOT_FOUND,
    #     detail=f'File {video.file_name} not found'
    # )


async def redirect_logged_user_to_entry(user: User, request: Request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/entry', headers=headers)

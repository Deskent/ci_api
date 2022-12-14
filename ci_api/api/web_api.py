from pathlib import Path

from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import FileResponse

from config import settings, logger
from models.models import Video, User, ViewedComplex, Complex
from schemas.complexes_videos import VideoViewed
from schemas.user_schema import slice_phone_to_format
from services.depends import get_logged_user
from services.videos_methods import get_viewed_video_response, get_viewed_complex_response
from services.web_context_class import WebContext
from web_service.utils.get_contexts import get_user_from_context
from web_service.utils.web_utils import get_checked_video

router = APIRouter(prefix="/web", tags=['WebApi'])


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed(
        complex_id: int,
        user: User = Depends(get_user_from_context)
):
    return await get_viewed_complex_response(user=user, complex_id=complex_id)


@router.get("/list", response_model=dict)
async def get_complexes_list(
        user: User = Depends(get_user_from_context)
):
    """Return complexes list"""
    complexes: list[Complex] = await Complex.get_all()

    return dict(user=user, complexes=complexes)

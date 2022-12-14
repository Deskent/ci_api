from fastapi import APIRouter, Depends, HTTPException, status, Request

from models.models import User, Complex, Video
from schemas.complexes_videos import ComplexData
from schemas.user_schema import UserProgress
from services.depends import get_logged_user
from web_service.utils.get_contexts import get_user_from_context

router = APIRouter(prefix="/complex", tags=['Complexes'])



@router.get("/", response_model=UserProgress)
async def current_progress(
        user: User = Depends(get_logged_user)
):
    """
    Return current user views progress
    """
    return user


@router.get("/{complex_id}", response_model=ComplexData)
async def complex_data(
        complex_id: int,
):
    """Return complex info"""

    if not (complex_ := await Complex.get_by_id(complex_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complex not found")
    videos: list[Video] = await Video.get_all_by_complex_id(complex_id)

    return ComplexData(**complex_.dict(), videos=videos)

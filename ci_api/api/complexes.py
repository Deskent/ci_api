from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db_session
from models.models import User, Complex, Video
from schemas.complexes_videos import ComplexData
from schemas.user import UserProgress
from services.complexes_and_videos import check_level_up
from services.depends import get_logged_user

router = APIRouter(prefix="/complex", tags=['Complexes'])


@router.get("/", response_model=UserProgress)
async def current_progress(
        user: User = Depends(get_logged_user)
):
    """
    Return current user views progress
    """
    return user


@router.put("/", response_model=UserProgress)
async def video_viewed(
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_db_session)
):
    """
    Calculate and return current progress and level after video viewed. Need authorization.

    :return: Current user view progress
    """

    return await check_level_up(user=user, session=session)


@router.get("/{complex_id}", response_model=ComplexData)
async def complex_data(
        complex_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    """Return complex info"""

    if not (complex_ := await Complex.get_by_id(session, complex_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complex not found")
    videos: list[Video] = await Video.get_all_by_complex_id(session, complex_id)

    return ComplexData(**complex_.dict(), videos=videos)

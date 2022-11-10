from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import User, Complex, Video
from schemas.schemas import UserProgress, ComplexData
from services.depends import get_logged_user
from config import LEVEL_UP

router = APIRouter(prefix="/complex", tags=['Complexes'])


@router.get("/", response_model=UserProgress)
async def current_progress(
        user: User = Depends(get_logged_user)
):
    """
    Return current user wiews progress
    """

    return user


@router.put("/", response_model=UserProgress)
async def video_viewed(
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Calculate and return current progress and level.

    :return: Current user view progress
    """

    current_complex: Complex = await session.get(Complex, user.current_complex)
    videos: list[Video] = await Video.get_all_complex_videos(session, user.current_complex)
    level_up: bool = False
    if not videos:
        return UserProgress(**user.dict(), level_up=level_up)
    percent = round(1 / len(videos), 1) * 100
    user.progress = user.progress + percent
    if user.progress >= LEVEL_UP:
        if user.level < 10:
            user.level = user.level + 1
        user.progress = 0
        level_up = True
        user.current_complex = current_complex.next_complex_id
    session.add(user)
    await session.commit()

    return UserProgress(**user.dict(), level_up=level_up)


@router.get("/{complex_id}", response_model=ComplexData)
async def complex_data(
    complex_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Return complex info"""

    complex_: Complex = await session.get(Complex, complex_id)
    if not complex_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complex not found")
    videos: list[Video] = await Video.get_all_complex_videos(session, complex_id)
    result = ComplexData(**complex_.dict(), videos=videos)

    return result

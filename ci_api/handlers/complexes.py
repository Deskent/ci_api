from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database.db import get_session
from models.models import User, Complex, Video
from schemas.complexes_videos import ComplexData
from schemas.user import UserProgress
from services.depends import get_logged_user
from config import LEVEL_UP, logger

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
        session: AsyncSession = Depends(get_session)
):
    """
    Calculate and return current progress and level after video viewed. Need authorization.

    :return: Current user view progress
    """

    current_complex: Complex = await session.get(Complex, user.current_complex)
    query = select(Video).where(Video.complex_id == user.current_complex)
    videos_row = await session.execute(query)
    videos: list[Video] = videos_row.scalars().all()
    if not videos:
        return UserProgress(**user.dict())
    percent: float = round(1 / len(videos), 1) * 100
    user.progress = user.progress + percent
    if user.progress >= LEVEL_UP:
        if user.level < 10:
            user.level = user.level + 1
        user.progress = 0
        user.current_complex = current_complex.next_complex_id
    session.add(user)
    await session.commit()
    logger.debug(f"User with id {user.id} viewed video in complex {current_complex.id}")

    return user


@router.get("/{complex_id}", response_model=ComplexData)
async def complex_data(
    complex_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Return complex info"""

    complex_: Complex = await session.get(Complex, complex_id)
    if not complex_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complex not found")
    query = select(Video).where(Video.complex_id == complex_id)
    videos_row = await session.execute(query)
    videos: list[Video] = videos_row.scalars().all()
    result = ComplexData(**complex_.dict(), videos=videos)

    return result

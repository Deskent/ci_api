from fastapi import APIRouter, Depends, HTTPException, status

from models.models import User, Complex, Video
from schemas.complexes_videos import ComplexData
from schemas.user_schema import UserProgress, UserOutput
from services.depends import get_logged_user
from services.videos_methods import get_viewed_complex_response

router = APIRouter(prefix="/complex", tags=['Complexes'])


@router.get("/", response_model=UserProgress)
async def current_progress(
        user: User = Depends(get_logged_user)
):
    """
    Return current user views progress
    """
    return user


@router.get("/list", response_model=dict)
async def complexes_list_get(
        user: User = Depends(get_logged_user)
):
    """Return complexes list"""
    complexes: list[Complex] = await Complex.get_all()

    return dict(user=UserOutput(**user.dict()), complexes=complexes)


@router.get("/{complex_id}", response_model=ComplexData)
async def complex_data(
        complex_id: int,
):
    """Return complex info"""

    if not (complex_ := await Complex.get_by_id(complex_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complex not found")
    videos: list[Video] = await Video.get_all_by_complex_id(complex_id)

    return ComplexData(**complex_.dict(), videos=videos)


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed_api(
        complex_id: int,
        user: User = Depends(get_logged_user)
):
    return await get_viewed_complex_response(user=user, complex_id=complex_id)

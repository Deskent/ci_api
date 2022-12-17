from fastapi import APIRouter, status, Depends

from models.models import User, Complex
from schemas.user_schema import UserOutput
from services.videos_methods import get_viewed_complex_response
from web_service.utils.get_contexts import get_user_from_context

router = APIRouter(prefix="/web", tags=['WebApi'])


@router.get(
    "/complex_viewed/{complex_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def complex_viewed_web(
        complex_id: int,
        user: User = Depends(get_user_from_context)
):
    return await get_viewed_complex_response(user=user, complex_id=complex_id)


@router.get("/complex/list", response_model=dict)
async def get_complexes_list_web(
        user: User = Depends(get_user_from_context)
):
    """Return complexes list"""

    complexes: list[Complex] = await Complex.get_all()

    return dict(user=UserOutput(**user.dict()), complexes=complexes)


from fastapi import APIRouter, Depends, status

from crud_class.crud import CRUD
from database.models import User, Rate
from services.depends import get_logged_user

router = APIRouter(prefix="/rates", tags=['Rates'])


@router.get(
    "/",
    response_model=list[Rate],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_logged_user)]
)
async def get_all_rates():
    """Return list of all rates. Need authorization."""

    return await CRUD.rate.get_all()


@router.get(
    "/get_user_rate",
    response_model=Rate,
    status_code=status.HTTP_200_OK,
)
async def get_user_rate(
        user: User = Depends(get_logged_user),
):
    """Return user rate info. Need authorization.

    :return: Rate as JSON
    """

    return await CRUD.rate.get_by_id(user.rate_id)

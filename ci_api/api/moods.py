from fastapi import APIRouter, Depends
from starlette import status

from crud_class.crud import CRUD
from database.models import User, Mood
from services.depends import get_logged_user

router = APIRouter(prefix="/moods", tags=['Moods'])


@router.get(
    "/",
    response_model=list[Mood],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_logged_user)]
)
async def get_all_moods():
    """Return list of all moods. Need authorization.

    :return: list[Mood] as JSON
    """

    return await CRUD.mood.get_all()


@router.get(
    "/get_user_mood",
    response_model=Mood,
    status_code=status.HTTP_200_OK,
)
async def get_user_avatar(
        user: User = Depends(get_logged_user),
):
    """Return user mood info. Need authorization.

    :return: Mood as JSON
    """

    return await CRUD.mood.get_by_id(user.avatar)


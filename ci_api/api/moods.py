from fastapi import APIRouter, Depends
from starlette import status

from crud_class.crud import CRUD
from database.models import User, Mood
from schemas.user_schema import UserMood
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
    status_code=status.HTTP_200_OK,
)
async def get_user_mood(
        user: User = Depends(get_logged_user),
):
    """Return user mood info. Need authorization.

    :return: Mood as JSON
    """

    user_mood: Mood = await CRUD.mood.get_by_id(user.mood)
    if user_mood:
        return user_mood
    return await CRUD.mood.get_by_id(1)


@router.put(
    "/set_user_mood",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)
async def set_user_mood(
        mood: UserMood,
        user: User = Depends(get_logged_user)
):
    """
    Set mood for user. Need authorization.

    :return: null
    """

    await CRUD.user.set_mood(mood.mood_id, user=user)

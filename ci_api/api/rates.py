from fastapi import APIRouter, Depends, status

from crud_class.crud import CRUD
from database.models import User, Rate
from misc.web_context_class import WebContext
from schemas.rates import RateLink
from schemas.user_schema import UserSchema
from services.depends import get_logged_user
from web_service.utils.payments_context import get_subscribe_by_rate_id, \
    get_cancel_subscribe_context

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


@router.get(
    "/{rate_id}",
    response_model=RateLink,
    status_code=status.HTTP_200_OK
)
async def get_rate_by_id_api(
        rate_id: int,
        user: User = Depends(get_logged_user),
):
    """
    Return link for pay subscribe. Need authorization.

    :return: JSON with link
    """

    context = dict(user=user)
    web_context: WebContext = await get_subscribe_by_rate_id(context, rate_id)
    return web_context.api_render()


@router.delete(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserSchema
)
async def cancel_subscribe(
    user: User = Depends(get_logged_user),
):
    """Unsubscribe user. Need authorization.

    :return: User as JSON
    """

    context = dict(user=user)
    web_context: WebContext = await get_cancel_subscribe_context(context)
    return web_context.api_render()

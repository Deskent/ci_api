from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from services.response_manager import WebServiceResponser
from web_service.utils.get_contexts import get_logged_user_context
from web_service.utils.payments_context import *

router = APIRouter(tags=['web', 'subscribe'])


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_subscribe_context(context)
    return WebServiceResponser(web_context).render()


@router.get("/get_subscribe/{rate_id}", response_class=HTMLResponse)
async def get_subscribe(
        rate_id: int,
        context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_subscribe_by_rate_id(context, rate_id)
    return WebServiceResponser(web_context).render()


@router.get("/cancel_subscribe", response_class=HTMLResponse)
async def cancel_subscribe(
    context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_cancel_subscribe_context(context)
    return WebServiceResponser(web_context).render()

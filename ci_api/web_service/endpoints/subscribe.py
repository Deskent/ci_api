from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from web_service.utils.get_contexts import get_logged_user_context
from web_service.utils.payments_context import (
    WebContext, get_subscribe_context, get_subscribe_by_rate_id, get_cancel_subscribe_context)

router = APIRouter(tags=['web', 'subscribe'])


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_subscribe_context(context)
    return web_context.web_render()


@router.get("/get_subscribe/{rate_id}", response_class=HTMLResponse)
async def get_subscribe(
        rate_id: int,
        context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_subscribe_by_rate_id(context, rate_id)
    return web_context.web_render()


@router.get("/cancel_subscribe", response_class=HTMLResponse)
async def cancel_subscribe(
    context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_cancel_subscribe_context(context)
    return web_context.web_render()

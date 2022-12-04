from fastapi import APIRouter
from starlette.responses import HTMLResponse

from services.response_manager import WebServiceResponser
from web_service.utils.payments_context import *

router = APIRouter(tags=['web', 'sybscribe'])


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        context: dict = Depends(subscribe_context),
):
    return await WebServiceResponser(context).render()


@router.get("/get_subscribe/{rate_id}", response_class=HTMLResponse)
async def get_subscribe(
        context: dict = Depends(get_subscribe_by_rate_id)
):
    return await WebServiceResponser(context).render()


@router.get("/payment_result", response_class=HTMLResponse)
async def payment_result(
        context: dict = Depends(check_payment_result)
):
    return await WebServiceResponser(context).render()

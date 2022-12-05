from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from services.response_manager import WebServiceResponser
from web_service.utils.titles_context import get_logged_user_context
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


@router.get("/payment_result", response_class=HTMLResponse)
async def payment_result(
        context: dict = Depends(get_logged_user_context),
        _payform_status: str = None,
        _payform_id: int = None,
        _payform_order_id: int = None,
        _payform_sign: str = None
):
    web_context: WebContext = await check_payment_result(
        context=context, payform_status=_payform_status, payform_id=_payform_id,
        payform_order_id=_payform_order_id, payform_sign=_payform_sign
    )
    return WebServiceResponser(web_context).render()


@router.get("/cancel_subscribe", response_class=HTMLResponse)
async def cancel_subscribe(
    context: dict = Depends(get_logged_user_context),
):
    web_context: WebContext = await get_cancel_subscribe_context(context)
    return WebServiceResponser(web_context).render()

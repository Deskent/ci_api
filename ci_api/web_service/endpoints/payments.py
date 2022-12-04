from fastapi import APIRouter
from starlette.responses import HTMLResponse

from services.response_manager import WebServiceResponser
from web_service.utils import load_self_page
from web_service.utils.payments_context import *

router = APIRouter(tags=['web', 'subscribe'])


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe(
        context: WebContext = Depends(subscribe_context),
):
    return WebServiceResponser(context).render()


@router.get("/get_subscribe/{rate_id}", response_class=HTMLResponse)
async def get_subscribe(
        context: WebContext = Depends(get_subscribe_by_rate_id)
):
    return WebServiceResponser(context).render()


@router.get("/payment_result", response_class=HTMLResponse)
async def payment_result(
        context: WebContext = Depends(check_payment_result)
):
    return WebServiceResponser(context).render()


@router.get("/cancel_subscribe", response_class=HTMLResponse)
async def cancel_subscribe(
        self_page: dict = Depends(load_self_page),
):
    # TODO переделать
    return self_page

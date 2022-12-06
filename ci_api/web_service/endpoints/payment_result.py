from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from services.response_manager import WebContext, WebServiceResponser
from web_service.utils.payments_context import check_payment_result
from web_service.utils.get_contexts import get_logged_user_context

router = APIRouter(tags=['web', 'payments'])


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

from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse, FileResponse

from database.models import User
from misc.web_context_class import WebContext
from web_service.handlers.form_checks_report import form_payments_report
from web_service.utils.payments_context import check_payment_result
from web_service.utils.get_contexts import get_user_browser_session, \
    get_profile_page_context
from config import settings

router = APIRouter(tags=['web', 'payments'], include_in_schema=False)


@router.get("/payment_result", response_class=HTMLResponse)
async def payment_result(
        context: dict = Depends(get_profile_page_context),
        _payform_status: str = None,
        _payform_id: int = None,
        _payform_order_id: int = None,
        _payform_sign: str = None
):
    web_context: WebContext = await check_payment_result(
        context=context, payform_status=_payform_status, payform_id=_payform_id,
        payform_order_id=_payform_order_id, payform_sign=_payform_sign
    )
    return web_context.web_render()


@router.get("/payment_report", response_class=HTMLResponse)
async def payment_report(
        context: dict = Depends(get_profile_page_context),
        user: User = Depends(get_user_browser_session)
):
    web_context: WebContext = await form_payments_report(context=context, user=user)
    return web_context.web_render()


@router.get("/download_checks/{file_path}")
async def get_video(
        file_path: str,
):
    """
    Return video by video id. Need active user.

    :param video_id: int - Video database ID

    :return: Video data as JSON

    """
    full_path = settings.PAYMENTS_DIR / 'reports' / file_path
    return FileResponse(path=full_path)

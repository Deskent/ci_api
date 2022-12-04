import json

import requests
from fastapi import APIRouter
from starlette.responses import HTMLResponse

from models.models import Rate
from web_service.utils import *
from config import logger

router = APIRouter(tags=['web', 'sybscribe'])


@router.get("/get_subscribe/{rate_id}", response_class=HTMLResponse)
async def get_subscribe(
        rate_id: int,
        context: dict = Depends(get_full_context),
):
    user: User = context['user']
    rate: Rate = await Rate.get_by_id(rate_id)
    link: str = get_payment_link(user, rate)
    if link:
        return RedirectResponse(link)

    context.update(error="Ошибка ответа сервиса оплаты")

    return templates.TemplateResponse("subscribe.html", context=context)


@router.get("/payment_result")
async def payment_result(
        context: dict = Depends(get_full_context),
        _payform_status: str = None,
        _payform_id: int = None,
        _payform_order_id: int = None,
        _payform_sign: str = None
):
    user: User = context['user']
    if _payform_status == 'success':
        if not user.is_active:
            logger.debug(f"Activating user: {user.email}")
            rate_id = int(_payform_order_id)
            if not await Rate.get_by_id(rate_id):
                context.update(error="Тариф не найден")
                return templates.TemplateResponse("subscribe.html", context=context)
            user.rate_id = rate_id
            user.is_active = True
            await user.save()

        context.update(success="Подписка успешна оформлена")

        return templates.TemplateResponse("profile.html", context=context)

    logger.error(
        f"Payform status: {_payform_status}\n"
        f"Payform id: {_payform_id}\n"
        f"Payform order id: {_payform_order_id}\n"
        f"Payform status: {_payform_sign}\n"
    )
    context.update(error="При попытке подписки произошла ошибка")
    return templates.TemplateResponse("subscribe.html", context=context)


def get_payment_link(user: User, rate: Rate) -> str:
    params: str = (
        f"&order_id={rate.id}"
        f"&customer_phone={user.phone}"
        f"&customer_extra={user.id}"
        f"&order_sum={rate.price}"
        f"&products[0][price]={rate.price}"
        f"&products[0][quantity]=1"
        f"&products[0][name]={rate.name}"
        f"&demo_mode=1"  # TODO  <- ТЕСТОВЫЙ РЕЖИМ!
    )

    url = (
        f"https://box.payform.ru/?"
        f"do=link"
        f"&type=json"
        f"&callbackType=json"
        f"&currency=rub"
        f"&acquiring=sbrf"
        f"&sys={settings.PRODAMUS_SYS_KEY}"
    )
    url += params
    headers = {
        "Content-type": "text/plain",
        "charset": "utf-8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data: dict = response.json()
            return data['payment_link']
        except json.JSONDecodeError as err:
            logger.error(f"Json error: {err}")

    return ''

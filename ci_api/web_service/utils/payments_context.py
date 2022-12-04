import json

import requests
from fastapi import Depends
from loguru import logger

from config import settings
from exc.payment.exceptions import PaymentServiceError, UserNotFoundError, RateNotFound
from models.models import User, Rate, Payment
from services.response_manager import WebContext
from web_service.utils import get_full_context


async def subscribe_context(
        context: dict = Depends(get_full_context),

) -> WebContext:
    obj = WebContext(context=context)
    if not (user := obj.context.get('user')):
        obj.template = "entry.html"
        obj.to_raise = UserNotFoundError
        return obj

    rates: list[Rate] = await Rate.get_all()
    current_rate: Rate = await Rate.get_by_id(user.rate_id)

    api_data = dict(rates=rates, current_rate=current_rate)
    obj.api_data = dict(payload=api_data)
    obj.template = "subscribe.html"
    obj.context.update(**api_data)

    return obj


async def get_subscribe_by_rate_id(
        rate_id: int,
        context: dict = Depends(get_full_context),
) -> WebContext:
    obj = WebContext(context=context)
    user: User = context['user']
    rate: Rate = await Rate.get_by_id(rate_id)

    if await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=rate.id):
        obj.error = PaymentServiceError.detail
        obj.template = "subscribe.html"
        obj.to_raise = PaymentServiceError

        return obj
    link: str = get_payment_link(user, rate)
    if link:
        obj.redirect = link
        obj.api_data = dict(payload=link)
        return obj

    obj.error = PaymentServiceError.detail
    obj.template = "subscribe.html"
    obj.to_raise = PaymentServiceError

    return obj


async def check_payment_result(
        context: dict = Depends(get_full_context),
        _payform_status: str = None,
        _payform_id: int = None,
        _payform_order_id: int = None,
        _payform_sign: str = None
) -> WebContext:

    obj = WebContext(context=context)
    if _payform_status != 'success':
        logger.error(
            f"\nPayform status: {_payform_status}"
            f"\nPayform id: {_payform_id}"
            f"\nPayform order id: {_payform_order_id}"
            f"\nPayform status: {_payform_sign}"
        )
        obj.error = "При попытке подписки произошла ошибка"
        obj.template = "subscribe.html"
        obj.to_raise = PaymentServiceError

        return obj

    rate_id: int = _payform_order_id

    if not await Rate.get_by_id(rate_id):
        obj.error = "Тариф не найден",
        obj.template = "subscribe.html",
        obj.to_raise = RateNotFound

        return obj

    user: User = context['user']
    if not user.is_active:
        logger.debug(f"Activating user: {user.email}")
        user.rate_id = rate_id
        user.is_active = True
        await user.save()

        payment: Payment = Payment(
            payment_id=_payform_id, payment_sign=_payform_sign,
            user_id=user.id, rate_id=user.rate_id
        )
        await payment.save()

    obj.api_data = dict(payload=user)
    obj.success = "Подписка успешна оформлена"
    obj.template = "profile.html"

    return obj


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

from fastapi import Depends
from loguru import logger

from exc.payment.exceptions import PaymentServiceError, UserNotFoundError, RateNotFound, \
    SubscribeExistsError
from models.models import User, Rate, Payment
from services.response_manager import WebContext
from web_service.utils import get_full_context
from web_service.utils.payment_request import get_payment_link


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
    user: User = context['user']
    current_rate: Rate = await Rate.get_by_id(user.rate_id)
    rates: list[Rate] = await Rate.get_all()
    context.update(current_rate=current_rate, rates=rates)
    obj = WebContext(context=context)
    rate: Rate = await Rate.get_by_id(rate_id)

    if await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=rate.id):
        obj.error = SubscribeExistsError.detail
        obj.template = "subscribe.html"
        obj.to_raise = SubscribeExistsError

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



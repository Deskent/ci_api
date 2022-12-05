import json

import requests
from loguru import logger

from config import settings
from models.models import User, Rate


async def get_payment_link(user: User, rate: Rate) -> str:
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
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            try:
                data: dict = response.json()
                return data['payment_link']
            except json.JSONDecodeError as err:
                logger.error(f"Json error: {err}")
    except requests.exceptions.Timeout as err:
        logger.error(f"Prodamus request timeout error: {err}")

    return ''

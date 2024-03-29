import json

import requests
from loguru import logger

from config import prodamus
from database.models import User, Rate


REQUEST_TIMEOUT = 15


async def get_payment_link(user: User, rate: Rate) -> str:
    params: str = (
        f"&order_id={rate.id}"
        f"&customer_phone={user.phone}"
        f"&customer_extra={user.id}"
        f"&customer_email={user.email}"
        f"&order_sum={rate.price}"
        f"&products[0][price]={rate.price}"
        "&products[0][quantity]=1"
        f"&products[0][name]={rate.name}"
        f"&urlNotification={prodamus.NOTIFICATION_URL}"
        f"&urlSuccess={prodamus.SUCCESS_URL}"
        f"&urlReturn={prodamus.RETURN_URL}"
        f"&sys={prodamus.PRODAMUS_SYS_KEY}"
    )
    if prodamus.PRODAMUS_MODE == 'test':
        params += "&demo_mode=1"
    url = (
        "https://box.payform.ru/?"
        "do=link"
        "&type=json"
        "&callbackType=json"
        "&currency=rub"
        "&acquiring=sbrf"
    )
    url += params
    headers = {
        "Content-type": "text/plain",
        "charset": "utf-8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            try:
                data: dict = response.json()
                return data['payment_link']
            except json.JSONDecodeError as err:
                logger.exception(f"Prodamus get link: JSON error: {err}")
    except requests.exceptions.Timeout as err:
        logger.exception(f"Prodamus request timeout error: {err}")

    return ''

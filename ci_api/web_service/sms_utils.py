import asyncio
import secrets

import requests
from config import settings, logger


class SMSException(Exception):
    pass


class SMSru:
    """Class for send sms and calls authorizations to user
    using sms.ru service"""

    token: str = settings.SMS_TOKEN

    def __init__(self, phone: str):
        self.phone: str = phone

    async def send_sms(self, message: str):
        """
        Send sms message to user phone

        {
        "status": "OK", // Запрос выполнен успешно (нет ошибок в авторизации, проблем с отправителем, итд...)
        "status_code": 100, // Успешный код выполнения
        "sms": {
            "79255070602": {
                "status": "OK", // Возможные варианты: OK или ERROR.
                "status_code": 100, // Успешный код выполнения, сообщение принято на отправку
                "sms_id": "000000-10000000" // ID сообщения
            },
            "74993221627": {
                "status": "ERROR",
                "status_code": 207, // Код ошибки
                "status_text": "На этот номер (или один из номеров) нельзя отправлять сообщения, либо указано более 100 номеров в списке получателей" // Описание ошибки
            }
        } ,
        "balance": 4122.56 // Ваш баланс после отправки
    }
        """
        url = (
            f"https://sms.ru/sms/send?"
            f"api_id={self.token}&"
            f"to={self.phone}"
            f"&msg={message}"
            f"&json=1"
        )
        logger.debug(f"Send sms message {message} to phone: {self.phone}")
        response = requests.get(url)
        if response.status_code == 200:
            data: dict = response.json()

            if data['status'] == "OK":
                sms_id: str = data['sms']['sms_id']
                if not sms_id:
                    raise SMSException(f"SMS service error: No sms_id received.")

                return sms_id

            status_text: str = data.get('status_text', "Sms status text not defined")
            raise SMSException(f"SMS service error: {status_text}")

    async def send_call(self):
        """
        Send call to user phone
        {
            "status": "OK", // Запрос выполнен успешно (нет ошибок в авторизации, проблем с отправителем, итд...)
            "code": "1435", // Последние 4 цифры номера, с которого мы совершим звонок пользователю
            "call_id": "000000-10000000", // ID звонка
            "cost": 0.4, // Стоимость звонка
            "balance": 4122.56 // Ваш баланс после совершения звонка
        }
        """
        url = (
            f"https://sms.ru/code/call?"
            f"phone={self.phone}"
            f"&ip=-1"
            f"&api_id={self.token}"
            f"&json=1"
        )
        logger.debug(f"Send call code to phone: {self.phone}")

        response = requests.get(url)
        if response.status_code == 200:
            data: dict = response.json()
            if data['status'] == "OK":
                return data['code']

            status_text: str = data.get('status_text', "Sms status text not defined")
            raise SMSException(f"SMS service error: {status_text}")

        raise SMSException(f"SMS service error")


sms_service = SMSru(settings.SMS_TOKEN)

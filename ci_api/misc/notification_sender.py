#pip install exponent_server_sdk

import asyncio

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError, PushTicket,
)
from requests.exceptions import ConnectionError, HTTPError
from config import logger


def _create_push_messages(message: str, tokens: list[str], extra=None) -> list[PushMessage]:
    return [
        PushMessage(to=token, body=message, data=extra)
        for token in tokens
    ]


async def send_push_messages(message: str, tokens: list[str], extra=None) -> None:
    logger.info(f'Send push message {message} to tokens: {tokens}')
    push_messages: list[PushMessage] = _create_push_messages(message, tokens, extra)

    try:
        response: list[PushTicket] = PushClient().publish_multiple(push_messages=push_messages)
        logger.info(response)
        for ticket in response:
            logger.info(f'Response: {ticket.validate_response()}')
    except PushServerError as exc:
        logger.error(f'PushServerError: {exc}')
    except (ConnectionError, HTTPError) as exc:
        logger.error(f'PushServer ConnectionError, HTTPError: {exc}')
    except DeviceNotRegisteredError as exc:
        logger.error(f'DeviceNotRegisteredError: {exc}')
    except PushTicketError as exc:
        logger.error(f'PushTicketError: {exc}')

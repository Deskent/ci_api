#pip install exponent_server_sdk

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


async def send_push_messages(message: str, tokens: list[str], extra=None) -> list[PushTicket]:
    logger.info(f'Send push message {message} to tokens: {tokens}')
    push_messages: list[PushMessage] = _create_push_messages(message, tokens, extra)

    try:
        responses: list[PushTicket] = PushClient().publish_multiple(push_messages=push_messages)
        logger.info(responses)
        for ticket in responses:
            logger.info(f'Response: {ticket.validate_response()}')
        return responses
    except PushServerError as exc:
        logger.error(f'PushServerError: {exc}')
    except (ConnectionError, HTTPError) as exc:
        logger.error(f'PushServer ConnectionError, HTTPError: {exc}')
    except DeviceNotRegisteredError as exc:
        logger.error(f'DeviceNotRegisteredError: {exc}')
    except PushTicketError as exc:
        logger.error(f'PushTicketError: {exc}')

    return []

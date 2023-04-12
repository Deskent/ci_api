# pip install exponent_server_sdk

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
    # Mobile developer said set it
    push_string: str = 'mobile-ci:///AlarmWork'
    return [
        PushMessage(to=token, body=message, data={'url': push_string})
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
        logger.exception(f'PushServerError: {exc}')
    except (ConnectionError, HTTPError) as exc:
        logger.exception(f'PushServer ConnectionError, HTTPError: {exc}')
    except DeviceNotRegisteredError as exc:
        logger.exception(f'DeviceNotRegisteredError: {exc}')
    except PushTicketError as exc:
        logger.exception(f'PushTicketError: {exc}')
    except ValueError as exc:
        logger.exception(f'ValueError: {exc}')

    return []


def send_push():
    extra = {'url': 'mobile-ci:///AlarmWork'}
    token = r"ExponentPushToken[Si28gRPdXFSFysUfoN03Ul]"
    text = "Hello, Julia"
    push = PushMessage(to=token, body=text, data=extra)
    result = PushClient().publish(push)
    print(result)


if __name__ == '__main__':
    # token = "ExponentPushToken[etDQ--NvdQf5GlgZIx9pQp]"
    token = "ExponentPushToken[7e8B0BIU1dsaFV767ZcMQO]"
    text = "Hello, Julia"
    # asyncio.run(send_push_messages(message=text, tokens=tokens))
    send_push()

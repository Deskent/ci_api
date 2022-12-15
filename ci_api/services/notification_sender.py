#pip install exponent_server_sdk

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.



async def send_push_messages(message: str, tokens: list[str], extra=None) -> None:
    pusher = PushClient()
    push_messages = [
        PushMessage(token=token, message=message, data=extra)
        for token in tokens
    ]

    try:
        # responses = pusher.publish_multiple(push_messages=push_messages)
        response = pusher.publish(push_messages[0])
        print(response)
        print(response.validate_response())
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        # rollbar.report_exc_info(
        #     extra_data={
        #         'token': token,
        #         'message': message,
        #         'extra': extra,
        #         'errors': exc.errors,
        #         'response_data': exc.response_data,
        #     })
        print(exc)
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        # rollbar.report_exc_info(
        #     extra_data={'token': token, 'message': message, 'extra': extra})
        print(exc)

    except DeviceNotRegisteredError as exc:
        print(exc)
        # Mark the push token as inactive
        # from notifications.models import PushToken
        # PushToken.objects.filter(token=token).update(active=False)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        # rollbar.report_exc_info(
        #     extra_data={
        #         'token': token,
        #         'message': message,
        #         'extra': extra,
        #         'push_response': exc.push_response._asdict(),
        #     })
        print(exc)

from starlette.requests import Request
from starlette.responses import RedirectResponse

from models.models import User
from services.user import get_bearer_header


async def redirect_created_user_to_verify_code(user: User, request: Request):
    login_token: str = await user.get_user_token()
    headers: dict[str, str] = get_bearer_header(login_token)
    request.session.update(token=login_token)

    return RedirectResponse('/entry', headers=headers)


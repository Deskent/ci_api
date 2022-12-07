import json

from loguru import logger

from config import settings
from models.models import PaymentCheck, User
from services.response_manager import WebContext


def save_json(checks: list[PaymentCheck], user: User) -> str:
    # TODO сохранять в нужный формат
    file_dir = settings.PAYMENTS_DIR / 'reports'
    if not file_dir.exists():
        file_dir.mkdir(parents=True)
    filename = f"{user.phone}.json"
    file_path = file_dir / filename
    data = [check.json() for check in checks]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return filename


async def form_payments_report(
        context: dict,
        user: User
) -> WebContext:
    obj = WebContext(context=context)
    checks: list[PaymentCheck] = await PaymentCheck.get_all_by_user_id(user.id)
    logger.info(checks)
    download_file_link: str = save_json(checks, user)

    obj.api_data = dict(payload=checks)
    obj.template = 'payment_report.html'
    obj.context.update(checks=checks, download_file_link=download_file_link)

    return obj

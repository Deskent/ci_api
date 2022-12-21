import json
from pathlib import Path

import xlsxwriter
from loguru import logger

from config import settings
from database.models import PaymentCheck, User, Rate
from crud_class.crud import CRUD
from services.utils import to_isoformat
from misc.web_context_class import WebContext


async def form_payments_report(
        context: dict,
        user: User
) -> WebContext:
    obj = WebContext(context=context)
    checks: list[PaymentCheck] = await CRUD.payment_check.get_all_by_user_id(user.id)
    rates: list[Rate] = await CRUD.rate.get_all()

    logger.info(checks)
    download_file_link: str = save_to_excel_file(checks, rates, user)

    obj.api_data.update(payload=checks)
    obj.template = 'payment_report.html'
    obj.context.update(checks=checks, download_file_link=download_file_link)

    return obj


def save_to_excel_file(checks: list[PaymentCheck], rates: list[Rate], user: User) -> str:
    """Save payments checks to xlsx format file. Returns file name"""

    filepath = _get_filepath(user, format='xlsx')
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format()
    cell_format.set_center_across()
    worksheet.write(f'A1', "Телефон", cell_format)
    worksheet.write(f'B1', "Сумма", cell_format)
    worksheet.write(f'C1', "Тариф", cell_format)
    worksheet.write(f'D1', "Дата", cell_format)
    worksheet.write(f'E1', "Номер ордера", cell_format)
    for index, check in enumerate(checks, start=2):
        worksheet.write(f'A{index}', check.customer_phone.strip("'"), cell_format)
        worksheet.set_column('A:A', len(check.customer_phone) + 5)
        worksheet.write(f'B{index}', check.sum, cell_format)
        worksheet.set_column('B:B', len(check.sum) + 5)
        rate_name = _get_rate_name(rates, check.rate_id)
        worksheet.write(f'C{index}', rate_name, cell_format)
        worksheet.set_column('C:C', len(rate_name) + 5)
        payment_date = to_isoformat(check.date)
        worksheet.write(f'D{index}', payment_date, cell_format)
        worksheet.set_column('D:D', len(payment_date) + 5)
        order_id = str(check.order_id)
        worksheet.write(f'E{index}', order_id, cell_format)
        worksheet.set_column('E:E', len(order_id) + 5)
    workbook.close()

    return filepath.name


def _get_rate_name(rates: list[Rate], rate_id: int) -> str:
    """Return rate name from rates list"""

    for rate in rates:
        if rate.id == rate_id:
            return rate.name
    return "Тариф не указан"


def _get_filepath(user: User, format: str = 'json') -> Path:
    """Return absolute path to payment file"""

    file_dir = settings.PAYMENTS_DIR / 'reports'
    if not file_dir.exists():
        file_dir.mkdir(parents=True)
    filename = f"{user.phone}.{format}"
    file_path = file_dir / filename

    return file_path


def save_to_json(checks: list[PaymentCheck], user: User) -> str:
    """Save payments checks to json format file. Returns file name"""

    file_path: Path = _get_filepath(user, format='json')
    data = [check.json() for check in checks]
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return file_path.name

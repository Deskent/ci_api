from fastapi import Depends, APIRouter
from starlette.responses import HTMLResponse

from config import templates
from web_service.utils.title_context_func import update_title
from web_service.utils.get_contexts import get_base_context


router = APIRouter(tags=['web', 'index'])


@router.get("/", response_class=HTMLResponse)
@router.get("/index", response_class=HTMLResponse)
async def index(
        context: dict = Depends(get_base_context)
):
    return templates.TemplateResponse(
        "index.html", context=update_title(context, 'index'))


@router.get("/user_agree", response_class=HTMLResponse)
async def user_agree(
        context: dict = Depends(get_base_context)
):
    context.update(
        title='Пользовательское соглашение',
        head_title='Пользовательское соглашение'
    )

    return templates.TemplateResponse('user_agree.html', context=context)


@router.get("/confidential", response_class=HTMLResponse)
async def confidential(
        context: dict = Depends(get_base_context)
):
    context.update(
        title='Политика',
        head_title='Политика в отношении обработки персональных данных'
    )

    return templates.TemplateResponse('confidential.html', context=context)

from fastapi.responses import RedirectResponse
from pydantic import validator

from config import logger
from config import templates
from exc.exceptions import ApiRequestError, UserNotFoundError, UserNotFoundErrorApi
from models.models import User
from web_service.utils.title_context_func import get_page_titles


class WebContext:

    def __init__(self, context: dict):
        self.context: dict = context
        self._template: str = ''
        self.redirect: str = ''
        self.error: str = ''
        self.success: str = ''
        self.to_raise: object = None
        self.api_data: dict = {}

    @validator('to_raise')
    def to_raise_must_be_exception_or_none(cls, value):
        if value and not isinstance(value, Exception):
            raise ValueError('Must be an Exception type')
        return value

    def is_user_in_context(self) -> User:
        if user := self.context.get('user'):
            return user

        logger.warning(f"User is not in context:\n{self.context}")
        self.template = "entry_sms.html"
        self.to_raise = UserNotFoundErrorApi

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        self.context.update(**get_page_titles(self.context, value))

    def web_render(self):
        if self.error:
            self.context.update(error=self.error)
        if self.success:
            self.context.update(success=self.success)

        if self.template:
            return templates.TemplateResponse(self.template, context=self.context)
        elif self.redirect:
            return RedirectResponse(self.redirect)
        return templates.TemplateResponse("error_page.html", context={})

    def api_render(self) -> dict:
        if self.to_raise is not None:
            raise self.to_raise
        elif self.api_data:
            return self.api_data['payload']
        raise ApiRequestError

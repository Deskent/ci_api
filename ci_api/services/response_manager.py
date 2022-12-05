import abc
from abc import abstractmethod

from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, validator

from config import logger
from config import templates
from exc.payment.exceptions import ApiRequestError, UserNotFoundError
from models.models import User
from web_service.utils.title_context_func import update_title


class WebContext:

    def __init__(self, context: dict):
        self.context: dict = context
        self._template: str = ''
        self._redirect: str = ''
        self._error: str = ''
        self._success: str = ''
        self._to_raise: object = None
        self.api_data: dict = {}

    @validator('to_raise')
    def to_raise_must_be_exception_or_none(cls, value):
        if value and not isinstance(value, Exception):
            raise ValueError('Must be an Exception type')
        return value

    def is_user_in_context(self) -> User:
        if user := self.context.get('user'):
            logger.warning("User is not in context")
            return user
        self._template = "entry.html"
        self._to_raise = UserNotFoundError

    @property
    def redirect(self) -> str:
        return self._redirect

    @property
    def error(self) -> str:
        return self._error

    @property
    def success(self) -> str:
        return self._success

    @property
    def to_raise(self) -> object:
        return self._to_raise

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value):
        self._template = value
        self.context.update(**update_title(self.context, value))


class ResponseManager(abc.ABC):

    def __init__(self, context: WebContext):
        self._obj: WebContext = context

    @abstractmethod
    def render(self):
        raise NotImplementedError


class WebServiceResponser(ResponseManager):

    def __init__(self, context: WebContext):
        super().__init__(context)

    def render(self) -> HTMLResponse | RedirectResponse:
        if self._obj.error:
            self._obj.context.update(error=self._obj.error)
        if self._obj.success:
            self._obj.context.update(success=self._obj.success)

        if self._obj.template:
            return templates.TemplateResponse(self._obj.template, context=self._obj.context)
        elif self._obj.redirect:
            return RedirectResponse(self._obj.redirect)
        return templates.TemplateResponse("error_page.html", context={})


class ApiServiceResponser(ResponseManager):
    def __init__(self, context: WebContext):
        super().__init__(context)

    def render(self) -> dict:
        if self._obj.to_raise is not None:
            raise self._obj.to_raise
        elif self._obj.api_data:
            return self._obj.api_data['payload']
        raise ApiRequestError

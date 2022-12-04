import abc
from abc import abstractmethod
from types import NoneType
from typing import Any

from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, validator

from config import templates
from exc.payment.exceptions import ApiRequestError


class WebContext(BaseModel):
    context: dict = {}
    template: str = ''
    redirect: str = ''
    error: str = ''
    success: str = ''
    to_raise: object = None
    api_data: dict = {}

    @validator('to_raise')
    def to_raise_must_be_exception_or_none(cls, value):
        if value and not isinstance(value, Exception):
            raise ValueError('Must be an Exception type')
        return value


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

import abc
from abc import abstractmethod

from fastapi.responses import RedirectResponse, HTMLResponse

from config import templates
from exc.payment.exceptions import ApiRequestError


class ResponseManager(abc.ABC):

    def __init__(self, context: dict):
        self._context: dict = context

    @abstractmethod
    async def render(self):
        raise NotImplementedError


class WebServiceResponser(ResponseManager):

    def __init__(self, context: dict):
        super().__init__(context)
        self._template: str = context.get('template', '')
        self._error: str = context.get('error', '')
        self._success: str = context.get('success', '')
        self._redirect: str = context.get('redirect', '')

    async def render(self) -> HTMLResponse | RedirectResponse:
        if self._template:
            return templates.TemplateResponse(self._template, context=self._context)
        elif self._redirect:
            return RedirectResponse(self._redirect)
        return templates.TemplateResponse("error_page.html", context={})


class ApiServiceResponser(ResponseManager):
    def __init__(self, context: dict):
        super().__init__(context)

        self._to_raise: Exception = context.get("to_raise", None)
        self._api_data: dict = context.get("api_data", {})

    async def render(self) -> dict:
        if self._to_raise:
            raise self._to_raise
        elif self._api_data:
            return self._api_data
        raise ApiRequestError

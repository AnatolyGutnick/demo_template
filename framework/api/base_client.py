"""Base API client on Playwright's APIRequestContext.

Every request/response is an Allure step with the body attached, so a failed
test shows exactly what was sent and returned. Credentials are masked: the
report is public (GitHub Pages).
"""

from __future__ import annotations

import json
from typing import Any

import allure
from playwright.sync_api import APIRequestContext, APIResponse


class BaseClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _call(self, method: str, path: str, **kwargs: Any) -> APIResponse:
        with allure.step(f"{method.upper()} {path}"):
            if "data" in kwargs:
                _attach("request body", kwargs["data"])
            response = self.request.fetch(path, method=method.upper(), **kwargs)
            _attach(f"response {response.status}", _safe_body(response))
            return response

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self._call("get", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> APIResponse:
        return self._call("post", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> APIResponse:
        return self._call("put", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> APIResponse:
        return self._call("patch", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        return self._call("delete", path, **kwargs)


def _safe_body(response: APIResponse) -> Any:
    try:
        return response.json()
    except Exception:
        return response.text()


SENSITIVE_KEYS = {"token", "uid-token", "access-key", "access_key", "prv_key", "password"}


def _mask(body: Any) -> Any:
    if isinstance(body, dict):
        return {k: "***" if k in SENSITIVE_KEYS else _mask(v) for k, v in body.items()}
    if isinstance(body, list):
        return [_mask(v) for v in body]
    return body


def _attach(name: str, body: Any) -> None:
    body = _mask(body)
    if isinstance(body, (dict, list)):
        allure.attach(json.dumps(body, indent=2, default=str), name, allure.attachment_type.JSON)
    else:
        allure.attach(str(body), name, allure.attachment_type.TEXT)

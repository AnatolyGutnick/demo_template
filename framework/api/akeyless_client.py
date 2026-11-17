"""Akeyless REST API client (https://docs.akeyless.io/reference).

Every command is `POST /<command>` with a JSON body; the auth token goes in the body (`token`),
not in a header. Errors come back as `{"error": "..."}`. Field names follow the API exactly.
Methods return the raw APIResponse - the test decides what is expected.
"""

from __future__ import annotations

from typing import Any

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from framework.api.base_client import BaseClient


class AkeylessClient(BaseClient):
    def __init__(self, request: APIRequestContext, token: str | None = None) -> None:
        super().__init__(request)
        self.token = token

    def with_token(self, token: str) -> AkeylessClient:
        """Same connection, another identity."""
        return AkeylessClient(self.request, token)

    def command(self, name: str, body: dict[str, Any] | None = None, *, auth: bool = True) -> APIResponse:
        payload = {k: v for k, v in (body or {}).items() if v is not None}
        if auth and self.token is not None:
            payload.setdefault("token", self.token)
        return self.post(name, data=payload)

    # ---------- auth ----------

    @allure.step("API: auth (access key)")
    def auth(self, access_id: str, access_key: str) -> APIResponse:
        return self.command(
            "auth", {"access-type": "access_key", "access-id": access_id, "access-key": access_key}, auth=False
        )

    # ---------- static secrets ----------

    @allure.step("API: create secret {name}")
    def create_secret(self, name: str, value: str, **extra: Any) -> APIResponse:
        return self.command("create-secret", {"name": name, "value": value, **extra})

    @allure.step("API: get secret value {names}")
    def get_secret_value(self, names: list[str], version: int | None = None) -> APIResponse:
        return self.command("get-secret-value", {"names": names, "version": version})

    @allure.step("API: update secret value {name}")
    def update_secret_val(self, name: str, value: str, keep_prev_version: bool = True) -> APIResponse:
        # the API takes this flag as a string "true"/"false"
        return self.command(
            "update-secret-val", {"name": name, "value": value, "keep-prev-version": str(keep_prev_version).lower()}
        )

    @allure.step("API: list items in {path}")
    def list_items(self, path: str) -> APIResponse:
        return self.command("list-items", {"path": path})

    @allure.step("API: delete item {name}")
    def delete_item(self, name: str) -> APIResponse:
        return self.command("delete-item", {"name": name, "version": -1})  # -1 = whole item, all versions

    # ---------- access ----------

    @allure.step("API: create role {name}")
    def create_role(self, name: str) -> APIResponse:
        return self.command("create-role", {"name": name})

    @allure.step("API: set role rule {role} {capability} on {path}")
    def set_role_rule(self, role: str, path: str, capability: list[str]) -> APIResponse:
        return self.command("set-role-rule", {"role-name": role, "path": path, "capability": capability})

    @allure.step("API: delete role {name}")
    def delete_role(self, name: str) -> APIResponse:
        return self.command("delete-role", {"name": name})

    @allure.step("API: create API key auth method {name}")
    def create_api_key_auth_method(self, name: str) -> APIResponse:
        return self.command("auth-method-create-api-key", {"name": name})

    @allure.step("API: delete auth method {name}")
    def delete_auth_method(self, name: str) -> APIResponse:
        return self.command("delete-auth-method", {"name": name})

    @allure.step("API: associate role {role} with auth method {auth_method}")
    def assoc_role_am(self, role: str, auth_method: str) -> APIResponse:
        return self.command("assoc-role-am", {"role-name": role, "am-name": auth_method})

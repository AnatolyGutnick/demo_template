"""Example resource client - shows the pattern. Replace with the real endpoints."""

from __future__ import annotations

import allure
from playwright.sync_api import APIResponse

from framework.api.base_client import BaseClient


class ExampleUsersClient(BaseClient):
    @allure.step("API: create user {payload[name]}")
    def create(self, payload: dict) -> APIResponse:
        return self.post("users", data=payload)

    @allure.step("API: get user {user_id}")
    def get_by_id(self, user_id: str) -> APIResponse:
        return self.get(f"users/{user_id}")

    @allure.step("API: delete user {user_id}")
    def remove(self, user_id: str) -> APIResponse:
        return self.delete(f"users/{user_id}")

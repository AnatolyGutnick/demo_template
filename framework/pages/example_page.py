"""Example page object - shows the pattern. Replace with the real pages of the system under test."""

from __future__ import annotations

import allure

from framework.pages.base_page import BasePage


class ExampleLoginPage(BasePage):
    path = "/login"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.user_name = page.get_by_label("Username")
        self.password = page.get_by_label("Password")
        self.submit = page.get_by_role("button", name="Log in")
        self.error = page.get_by_role("alert")

    def wait_until_loaded(self) -> None:
        self.submit.wait_for()

    @allure.step("Log in as {user_name}")
    def login(self, user_name: str, password: str) -> ExampleHomePage:
        self.user_name.fill(user_name)
        self.password.fill(password)
        self.submit.click()
        return ExampleHomePage(self.page)


class ExampleHomePage(BasePage):
    path = "/"

    def __init__(self, page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", level=1)

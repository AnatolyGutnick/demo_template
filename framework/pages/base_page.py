"""Base class for all page objects.

POM rules (also in CLAUDE.md):
- A page object holds locators and user actions. No assertions - those live in tests.
- Locators: get_by_role / get_by_label / get_by_test_id. No XPath, no sleeps.
- Actions that navigate return the next page object.
- Every public action is an Allure step, so the report reads as a user story.
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from framework.config import settings


class BasePage:
    #: Path relative to base_url. Override in subclasses.
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def url(self) -> str:
        return f"{settings.base_url.rstrip('/')}{self.path}"

    def open(self):
        with allure.step(f"Open {type(self).__name__} ({self.path})"):
            self.page.goto(self.url)
            self.wait_until_loaded()
        return self

    def wait_until_loaded(self) -> None:
        """Override with a page-specific readiness check (a key element visible)."""
        self.page.wait_for_load_state("domcontentloaded")

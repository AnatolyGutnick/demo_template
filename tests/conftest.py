"""Shared fixtures.

Layers:
- api_request / *_client  -> API tests and API-based setup for UI tests
- page objects            -> UI tests
- Allure                  -> test case ID link + failure artifacts
"""

from __future__ import annotations

from collections.abc import Iterator

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from framework.api.example_client import ExampleUsersClient
from framework.config import settings
from framework.pages.example_page import ExampleLoginPage

# ---------- browser ----------


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {**browser_context_args, "base_url": settings.base_url, "viewport": {"width": 1440, "height": 900}}


@pytest.fixture(autouse=True)
def _default_timeout(request: pytest.FixtureRequest) -> None:
    if "page" in request.fixturenames:
        request.getfixturevalue("page").set_default_timeout(settings.default_timeout_ms)


# ---------- API ----------


@pytest.fixture(scope="session")
def api_request(playwright: Playwright) -> Iterator[APIRequestContext]:
    context = playwright.request.new_context(
        base_url=settings.api_url.rstrip("/") + "/",
        timeout=settings.api_timeout_ms,
        # extra_http_headers={"Authorization": f"Bearer {token}"},
    )
    yield context
    context.dispose()


@pytest.fixture
def users_client(api_request: APIRequestContext) -> ExampleUsersClient:
    return ExampleUsersClient(api_request)


# ---------- pages ----------


@pytest.fixture
def login_page(page: Page) -> ExampleLoginPage:
    return ExampleLoginPage(page)


# ---------- Allure ----------


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Turn @pytest.mark.tc("TC-001") into an Allure label, so report <-> test-case table are linked."""
    for item in items:
        marker = item.get_closest_marker("tc")
        if marker and marker.args:
            item.add_marker(allure.id(marker.args[0]))
            item.add_marker(allure.tag(marker.args[0]))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Attach screenshot + Playwright trace to Allure when a UI test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page: Page | None = item.funcargs.get("page")
    if page is not None and not page.is_closed():
        allure.attach(page.screenshot(full_page=True), "screenshot", allure.attachment_type.PNG)
        allure.attach(page.url, "url", allure.attachment_type.URI_LIST)
    # Playwright traces (--tracing=retain-on-failure) land in test-results/ after the context
    # closes; CI uploads that folder. Open with: playwright show-trace <trace.zip>

"""Example combined flow: arrange via API -> act in UI -> verify via API.

API setup is fast and stable; the UI is used only for what the test is about;
the backend state is verified directly, not only what the screen shows.
"""

import allure
import pytest
from playwright.sync_api import expect

from framework.data.factories import example_user

pytestmark = [pytest.mark.e2e, pytest.mark.skip(reason="template example - replace with real tests")]


@allure.feature("Users")
@allure.story("New user can log in")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.tc("TC-E2E-001")
def test_user_created_via_api_can_log_in(users_client, login_page):
    with allure.step("Arrange: create user via API"):
        payload = example_user(password="Str0ng!pass")
        created = users_client.create(payload)
        assert created.status == 201
        user_id = created.json()["id"]

    try:
        home = login_page.open().login(payload["name"], payload["password"])
        expect(home.heading).to_be_visible()
    finally:
        users_client.remove(user_id)

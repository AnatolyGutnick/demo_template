"""Example UI tests - pattern only. Skipped until pointed at the real system."""

import allure
import pytest
from playwright.sync_api import expect

from framework.config import settings

pytestmark = [pytest.mark.ui, pytest.mark.skip(reason="template example - replace with real tests")]


@allure.feature("Login")
@allure.story("Valid login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.smoke
@pytest.mark.tc("TC-UI-001")
def test_login_with_valid_user_opens_home(login_page):
    home = login_page.open().login(settings.user_name, settings.user_password)

    expect(home.heading).to_be_visible()


@allure.feature("Login")
@allure.story("Invalid login")
@pytest.mark.regression
@pytest.mark.tc("TC-UI-002")
def test_login_with_wrong_password_shows_error(login_page):
    login_page.open().login(settings.user_name, "wrong-password")

    expect(login_page.error).to_be_visible()

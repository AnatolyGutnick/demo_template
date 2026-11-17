"""Identity -> token: access key auth."""

import allure
import pytest

from framework.config import settings
from framework.models.akeyless import ApiError, AuthOutput

pytestmark = [allure.feature("Auth"), allure.story("Access key auth")]


@pytest.mark.smoke
@pytest.mark.tc("TC-API-001")
def test_valid_access_key_returns_token(akeyless, admin):  # admin: skips if no test account
    response = akeyless.auth(settings.akeyless_access_id, settings.akeyless_access_key.get_secret_value())

    assert response.status == 200
    assert AuthOutput.model_validate(response.json()).token


@pytest.mark.smoke
@pytest.mark.tc("TC-API-002")
def test_wrong_access_key_is_rejected(akeyless, admin):
    response = akeyless.auth(settings.akeyless_access_id, "wrong-key")

    assert response.status == 401
    assert ApiError.model_validate(response.json()).error
    assert "token" not in response.json()

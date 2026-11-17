"""Identity -> token: access key auth."""

import allure
import pytest

from framework.config import settings
from framework.models.akeyless import ApiError, AuthOutput

pytestmark = [allure.feature("Auth"), allure.story("Access key auth")]


@pytest.mark.smoke
@pytest.mark.tc("TC-API-001")
def test_valid_access_key_returns_token(akeyless, admin):  # admin: skips if no test account
    # Arrange: nothing to create - the admin access ID / key of the test account come from settings

    # Act: sign in with the valid access ID and key
    response = akeyless.auth(settings.akeyless_access_id, settings.akeyless_access_key.get_secret_value())

    # Assert: 200 and a token, matching the response contract
    assert response.status == 200
    assert AuthOutput.model_validate(response.json()).token


@pytest.mark.smoke
@pytest.mark.tc("TC-API-002")
def test_wrong_access_key_is_rejected(akeyless, admin):
    # Arrange: a real access ID with a wrong key

    # Act: try to sign in
    response = akeyless.auth(settings.akeyless_access_id, "wrong-key")

    # Assert: 401, an error message in the documented shape, and no token
    assert response.status == 401
    assert ApiError.model_validate(response.json()).error
    assert "token" not in response.json()

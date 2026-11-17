"""Category: auth - the first stage of the pipeline (identity -> token)."""

import allure
import pytest

from framework.config import settings
from framework.models.akeyless import ApiError, AuthOutput
from framework.steps.akeyless_api import create_secret

pytestmark = [pytest.mark.api, pytest.mark.auth, allure.feature("Auth")]


@allure.story("Access key auth")
@pytest.mark.smoke
@pytest.mark.tc("TC-API-001")
def test_valid_access_key_returns_token(akeyless, admin):  # admin: skips if no test account
    response = akeyless.auth(settings.akeyless_access_id, settings.akeyless_access_key.get_secret_value())

    assert response.status == 200
    assert AuthOutput.model_validate(response.json()).token


@allure.story("Access key auth")
@pytest.mark.smoke
@pytest.mark.tc("TC-API-002")
def test_wrong_access_key_is_rejected(akeyless, admin):
    response = akeyless.auth(settings.akeyless_access_id, "wrong-key")

    assert response.status == 401
    assert ApiError.model_validate(response.json()).error
    assert "token" not in response.json()


@allure.story("Token required")
@pytest.mark.smoke
@pytest.mark.tc("TC-API-004")
@pytest.mark.parametrize("token", [None, "", "garbage-token"], ids=["no-token", "empty-token", "garbage-token"])
def test_secret_cannot_be_read_without_valid_token(flow, akeyless, token):
    flow.then(create_secret()).run()
    secret = flow.ctx["secret"]

    client = akeyless if token is None else akeyless.with_token(token)
    response = client.get_secret_value([secret.name])

    assert not response.ok
    assert secret.value not in response.text()

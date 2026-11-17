"""No valid token -> no secret."""

import allure
import pytest

from framework.steps.akeyless_api import create_secret

pytestmark = [allure.feature("Auth"), allure.story("Token required")]


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

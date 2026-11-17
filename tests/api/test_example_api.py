"""Example API tests - pattern only. Skipped until pointed at the real system."""

import allure
import pytest

from framework.data.factories import example_user
from framework.models.example_models import ExampleUser

pytestmark = [pytest.mark.api, pytest.mark.skip(reason="template example - replace with real tests")]


@allure.feature("Users")
@allure.story("Create user")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.tc("TC-API-001")
def test_create_user_returns_valid_contract(users_client):
    payload = example_user()

    response = users_client.create(payload)

    assert response.status == 201
    user = ExampleUser.model_validate(response.json())
    assert user.name == payload["name"]


@allure.feature("Users")
@allure.story("Create user - validation")
@pytest.mark.regression
@pytest.mark.tc("TC-API-002")
@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("email", "", "empty"),
        ("email", "no-at-sign", "invalid format"),
        ("name", "x" * 256, "above max length"),
    ],
    ids=lambda v: v if isinstance(v, str) and len(v) < 20 else None,
)
def test_create_user_rejects_invalid_input(users_client, field, value, reason):
    response = users_client.create(example_user(**{field: value}))

    assert response.status == 400, f"{field} {reason} should be rejected"

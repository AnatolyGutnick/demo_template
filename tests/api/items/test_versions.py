"""Updating a value keeps the previous version."""

import allure
import pytest

from framework.steps.akeyless_api import create_secret

pytestmark = [allure.feature("Static secrets"), allure.story("Versions")]


@pytest.mark.smoke
@pytest.mark.tc("TC-API-005")
def test_update_keeps_previous_version(flow):
    flow.then(create_secret()).run()
    admin, secret = flow.ctx["admin"], flow.ctx["secret"]

    assert admin.update_secret_val(secret.name, "new-value", keep_prev_version=True).ok

    latest = admin.get_secret_value([secret.name])
    first = admin.get_secret_value([secret.name], version=1)
    assert latest.json()[secret.name] == "new-value"
    assert first.json()[secret.name] == secret.value

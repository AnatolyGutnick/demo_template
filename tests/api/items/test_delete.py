"""A deleted secret is gone: not readable, not listed."""

import allure
import pytest

from framework.steps.akeyless_api import create_secret

pytestmark = [allure.feature("Static secrets"), allure.story("Delete")]


@pytest.mark.smoke
@pytest.mark.tc("TC-API-006")
def test_deleted_secret_cannot_be_read(flow):
    flow.then(create_secret()).run()
    admin, secret = flow.ctx["admin"], flow.ctx["secret"]

    assert admin.delete_item(secret.name).ok

    response = admin.get_secret_value([secret.name])
    assert not response.ok
    assert secret.value not in response.text()
    listed = admin.list_items(flow.ctx["root"]).json().get("items") or []
    assert secret.name not in [item["item_name"] for item in listed]

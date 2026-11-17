"""Category: items - is the value stored and returned exactly, for each kind of value?

Same pipeline every time (admin creates, admin reads); only the item varies.
"""

import json

import allure
import pytest

from framework.steps.akeyless_api import create_secret

pytestmark = [pytest.mark.api, pytest.mark.items, allure.feature("Static secrets")]

VALUES = [
    pytest.param({}, id="text-random"),
    pytest.param({"value": "line 1\nline 2\nline 3", "multiline_value": True}, id="multiline"),
    pytest.param({"value": json.dumps({"user": "app", "password": "p@ss"}), "format": "json"}, id="json"),
    pytest.param({"value": "pässwörd-秘密-🔑"}, id="unicode"),
    pytest.param({"value": " spaces around "}, id="leading-trailing-spaces"),
]


@allure.story("Create and read")
@pytest.mark.smoke
@pytest.mark.tc("TC-API-003")
@pytest.mark.parametrize("item", VALUES)
def test_created_secret_value_is_returned_exactly(flow, item):
    flow.then(create_secret(**item)).run()
    secret = flow.ctx["secret"]

    response = flow.ctx["admin"].get_secret_value([secret.name])

    assert response.status == 200
    # assumption (01-system-review Q11): the response maps secret name -> value
    assert response.json()[secret.name] == secret.value


@allure.story("Versions")
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


@allure.story("Delete")
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

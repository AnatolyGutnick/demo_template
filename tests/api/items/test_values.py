"""Is the value stored and returned exactly, for each kind of value?

Same pipeline every time (admin creates, admin reads); only the item varies.
"""

import json

import allure
import pytest

from framework.steps.akeyless_api import create_secret

pytestmark = [allure.feature("Static secrets"), allure.story("Create and read")]

VALUES = [
    pytest.param({}, id="text-random"),
    pytest.param({"value": "line 1\nline 2\nline 3", "multiline_value": True}, id="multiline"),
    pytest.param({"value": json.dumps({"user": "app", "password": "p@ss"}), "format": "json"}, id="json"),
    pytest.param({"value": "pässwörd-秘密-🔑"}, id="unicode"),
    pytest.param({"value": " spaces around "}, id="leading-trailing-spaces"),
]


@pytest.mark.smoke
@pytest.mark.tc("TC-API-003")
@pytest.mark.parametrize("item", VALUES)
def test_created_secret_value_is_returned_exactly(flow, item):
    # Arrange: admin creates a secret with this row's value (text, multiline, JSON, unicode, spaces)
    flow.then(create_secret(**item)).run()
    secret = flow.ctx["secret"]

    # Act: admin reads it back
    response = flow.ctx["admin"].get_secret_value([secret.name])

    # Assert: the same value, character for character
    assert response.status == 200
    # assumption (01-system-review Q11): the response maps secret name -> value
    assert response.json()[secret.name] == secret.value

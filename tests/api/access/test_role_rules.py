"""The access rules decision table from docs/03-test-cases.md.

Pipeline per row: admin creates the secret -> new identity with only the row's rules ->
that identity tries one action. One test, many variations.
"""

import allure
import pytest

from framework.steps.akeyless_api import create_secret, limited_identity

pytestmark = allure.feature("Access roles")

ACTIONS = {
    "read": lambda client, secret: client.get_secret_value([secret.name]),
    "update": lambda client, secret: client.update_secret_val(secret.name, "changed-by-limited-identity"),
    "delete": lambda client, secret: client.delete_item(secret.name),
}


def tc(n: str) -> pytest.MarkDecorator:
    """Test case ID per row of the decision table."""
    return pytest.mark.tc(f"TC-API-{n}")


# (rules [(capabilities, path)], secret folder, action, allowed)
DECISION_TABLE = [
    pytest.param([(["read"], "{root}/app/*")], "app", "read", True, id="read-rule-allows-read", marks=tc("016")),
    pytest.param([(["read"], "{root}/app/*")], "app", "update", False, id="read-rule-blocks-update", marks=tc("016")),
    pytest.param([(["read"], "{root}/app/*")], "app", "delete", False, id="read-rule-blocks-delete", marks=tc("016")),
    pytest.param(
        [(["read", "update"], "{root}/app/*")], "app", "update", True, id="update-rule-allows-update", marks=tc("016")
    ),
    pytest.param([(["list"], "{root}/app/*")], "app", "read", False, id="list-rule-blocks-read", marks=tc("018")),
    pytest.param(
        [(["read"], "{root}/app/*"), (["deny"], "{root}/app/locked/*")],
        "app/locked",
        "read",
        False,
        id="deny-wins",
        marks=tc("017"),
    ),
    pytest.param([(["read"], "{root}/team-a/*")], "team-b", "read", False, id="other-folder-blocked", marks=tc("019")),
    pytest.param([(["read"], "{root}/team/*")], "team-x", "read", False, id="prefix-trap-blocked", marks=tc("019")),
]


@allure.story("Role rules decision table")
@pytest.mark.smoke
@pytest.mark.parametrize(("rules", "folder", "action", "allowed"), DECISION_TABLE)
def test_role_rules_decide_access(flow, rules, folder, action, allowed):
    # Arrange: admin creates the secret, then a new user with ONLY this row's rules
    flow.then(create_secret(folder=folder)).then(limited_identity(rules)).run()
    secret, identity = flow.ctx["secret"], flow.ctx["identity"]

    # Act: that limited user tries the row's action
    response = ACTIONS[action](identity, secret)

    # Assert: allowed or denied, as the table says; a denied response must not leak the value
    assert response.ok is allowed, f"{action} expected {'allowed' if allowed else 'denied'}: {response.status}"
    if not allowed:
        assert secret.value not in response.text(), "denied response must not leak the value"

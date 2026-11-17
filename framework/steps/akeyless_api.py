"""Akeyless API steps for the flow - the "secret access pipeline":

    identity (auth method) -> token -> role rules -> item (secret) -> read / update / delete

Each step creates what it needs through the admin client (`ctx["admin"]`), under the run folder
(`ctx["root"]`), puts the result in the context and registers its own cleanup.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import APIResponse

from framework.api.akeyless_client import AkeylessClient
from framework.data.factories import secret_value, unique_suffix
from framework.flow import FlowContext, Step, StepError
from framework.models.akeyless import AuthOutput, CreateAuthMethodOutput


@dataclass(frozen=True)
class Secret:
    name: str
    value: str


def _ok(response: APIResponse, what: str) -> APIResponse:
    if not response.ok:
        raise StepError(f"{what} failed: {response.status} {response.text()}")
    return response


def create_secret(key: str = "secret", folder: str = "", value: str | None = None, **extra) -> Step:
    """Static secret at <root>/<folder>/<key>-<uuid>. Extra fields go to create-secret as is."""

    def action(ctx: FlowContext) -> None:
        admin: AkeylessClient = ctx["admin"]
        name = "/".join(p for p in (ctx["root"], folder, f"{key}-{unique_suffix()}") if p)
        val = value if value is not None else secret_value()
        _ok(admin.create_secret(name, val, **extra), f"create secret {name}")
        ctx.defer(f"delete secret {name}", admin.delete_item, name)
        ctx[key] = Secret(name, val)

    return Step(f"Create secret '{key}'", action)


def limited_identity(rules: list[tuple[list[str], str]], key: str = "identity") -> Step:
    """New API-key identity whose only role has `rules`: [(capabilities, path), ...].

    A path may use `{root}`, e.g. `{root}/team-a/*`. The authenticated client goes to ctx[key].
    """

    def action(ctx: FlowContext) -> None:
        admin: AkeylessClient = ctx["admin"]
        suffix = unique_suffix()
        role, auth_method = f"{ctx['root']}/role-{suffix}", f"{ctx['root']}/am-{suffix}"

        _ok(admin.create_role(role), "create role")
        ctx.defer(f"delete role {role}", admin.delete_role, role)
        for capability, path in rules:
            _ok(admin.set_role_rule(role, path.format(root=ctx["root"]), capability), "set role rule")

        created = _ok(admin.create_api_key_auth_method(auth_method), "create auth method")
        ctx.defer(f"delete auth method {auth_method}", admin.delete_auth_method, auth_method)
        keys = CreateAuthMethodOutput.model_validate(created.json())
        _ok(admin.assoc_role_am(role, auth_method), "associate role with auth method")

        token = AuthOutput.model_validate(_ok(admin.auth(keys.access_id, keys.access_key), "auth").json()).token
        ctx[key] = admin.with_token(token)

    return Step(f"Create limited identity '{key}' with rules {rules}", action)

"""Akeyless API steps for the flow - the "secret access pipeline":

    identity (auth method) -> token -> role rules -> item (secret) -> read / update / delete

Each step creates what it needs through the admin client (`ctx["admin"]`), under the run folder
(`ctx["root"]`), puts the result in the context and registers its own cleanup.
"""

from __future__ import annotations

from collections.abc import Callable
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


# ---------- identity types ----------
# Each identity type knows how to create its auth method (with cleanup) and returns a
# `sign_in()` function that gives a token. Adding a type = one function + one entry in
# IDENTITY_TYPES; every test that uses the `identity_type` fixture then runs for it too.


def _api_key_identity(admin: AkeylessClient, ctx: FlowContext, name: str) -> Callable[[], str]:
    created = _ok(admin.create_api_key_auth_method(name), "create API key auth method")
    ctx.defer(f"delete auth method {name}", admin.delete_auth_method, name)
    keys = CreateAuthMethodOutput.model_validate(created.json())

    def sign_in() -> str:
        response = _ok(admin.auth(keys.access_id, keys.access_key), "auth with API key")
        return AuthOutput.model_validate(response.json()).token

    return sign_in


IDENTITY_TYPES: dict[str, Callable[[AkeylessClient, FlowContext, str], Callable[[], str]]] = {
    "api_key": _api_key_identity,
}


def limited_identity(rules: list[tuple[list[str], str]], identity_type: str = "api_key", key: str = "identity") -> Step:
    """New identity of `identity_type` whose only role has `rules`: [(capabilities, path), ...].

    A path may use `{root}`, e.g. `{root}/team-a/*`. The signed-in client goes to ctx[key].
    """

    def action(ctx: FlowContext) -> None:
        if identity_type not in IDENTITY_TYPES:
            raise StepError(f"identity type '{identity_type}' not implemented; known: {sorted(IDENTITY_TYPES)}")
        admin: AkeylessClient = ctx["admin"]
        suffix = unique_suffix()
        role, auth_method = f"{ctx['root']}/role-{suffix}", f"{ctx['root']}/am-{suffix}"

        _ok(admin.create_role(role), "create role")
        ctx.defer(f"delete role {role}", admin.delete_role, role)
        for capability, path in rules:
            _ok(admin.set_role_rule(role, path.format(root=ctx["root"]), capability), "set role rule")

        sign_in = IDENTITY_TYPES[identity_type](admin, ctx, auth_method)
        _ok(admin.assoc_role_am(role, auth_method), "associate role with auth method")

        ctx[key] = admin.with_token(sign_in())

    return Step(f"Create {identity_type} identity '{key}' with rules {rules}", action)

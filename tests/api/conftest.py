"""Akeyless fixtures: admin identity (once per worker) and a flow per test."""

from __future__ import annotations

import time
from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext

from framework.api.akeyless_client import AkeylessClient
from framework.config import settings
from framework.data.factories import unique_suffix
from framework.flow import Flow
from framework.models.akeyless import AuthOutput


@pytest.fixture(scope="session")
def akeyless(api_request: APIRequestContext) -> AkeylessClient:
    """Client with no identity - for auth tests."""
    return AkeylessClient(api_request)


@pytest.fixture(scope="session")
def admin(akeyless: AkeylessClient) -> AkeylessClient:
    if not settings.akeyless_access_id:
        pytest.skip("AKEYLESS_ACCESS_ID / AKEYLESS_ACCESS_KEY not set - no Akeyless test account configured")
    response = akeyless.auth(settings.akeyless_access_id, settings.akeyless_access_key.get_secret_value())
    assert response.ok, f"admin auth failed: {response.status} {response.text()}"
    return akeyless.with_token(AuthOutput.model_validate(response.json()).token)


@pytest.fixture(scope="session")
def run_root() -> str:
    """Own folder per run (and per xdist worker): parallel-safe, easy to sweep."""
    return f"{settings.test_root}/{time.strftime('%Y%m%d-%H%M%S')}-{unique_suffix()}"


@pytest.fixture
def flow(admin: AkeylessClient, run_root: str) -> Iterator[Flow]:
    with Flow(admin=admin, root=run_root) as f:
        yield f

"""Test data builders. Every test gets unique data, so tests are independent and can run in parallel."""

from __future__ import annotations

import secrets
import uuid


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def secret_value() -> str:
    """Random, never a real credential."""
    return f"qa-{secrets.token_urlsafe(16)}"


def example_user(**overrides) -> dict:
    suffix = unique_suffix()
    user = {"name": f"qa-{suffix}", "email": f"qa-{suffix}@example.test"}
    user.update(overrides)
    return user

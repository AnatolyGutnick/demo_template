"""Test data builders. Every test gets unique data, so tests are independent and can run in parallel."""

from __future__ import annotations

import uuid


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def example_user(**overrides) -> dict:
    suffix = unique_suffix()
    user = {"name": f"qa-{suffix}", "email": f"qa-{suffix}@example.test"}
    user.update(overrides)
    return user

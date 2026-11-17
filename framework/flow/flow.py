"""Generic flow orchestrator: a chain of reusable steps with a cleanup stack.

No system-specific code here. Steps know the system; the flow only
- runs them in order, each as a named Allure step,
- shares data between them (`flow.ctx`),
- undoes what they created, in reverse order, even if a step or the test fails.

Kept thin on purpose (demo project): cleanup is `contextlib.ExitStack`, lifecycle is a pytest
fixture, variations are `pytest.mark.parametrize`. Asserts stay in the test, not in the flow.

    with Flow(admin=client) as flow:
        flow.then(create_secret()).then(limited_identity(...)).run()
        response = flow.ctx["identity"].get_secret_value(...)
    assert ...
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any

import allure


class StepError(Exception):
    """A step could not do its job (setup failed) - not a test assertion."""


@dataclass(frozen=True)
class Step:
    name: str
    action: Callable[[FlowContext], Any]


class FlowContext:
    """Data shared between steps, plus cleanup registration."""

    def __init__(self, stack: ExitStack, data: dict[str, Any]) -> None:
        self._stack = stack
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def defer(self, name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Register a cleanup. Runs last-in-first-out when the flow closes."""

        def _cleanup() -> None:
            with allure.step(f"Cleanup: {name}"):
                fn(*args, **kwargs)

        self._stack.callback(_cleanup)


class Flow:
    def __init__(self, **data: Any) -> None:
        self._stack = ExitStack()
        self._steps: list[Step] = []
        self.ctx = FlowContext(self._stack, dict(data))

    def then(self, step: Step) -> Flow:
        self._steps.append(step)
        return self

    def run(self) -> Flow:
        """Run the queued steps in order. Can be called again: arrange, run, then act, run."""
        steps, self._steps = self._steps, []
        for step in steps:
            with allure.step(step.name):
                step.action(self.ctx)
        return self

    def close(self) -> None:
        """Run all cleanups in reverse order. ExitStack keeps going if one fails, then re-raises."""
        self._stack.close()

    def __enter__(self) -> Flow:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

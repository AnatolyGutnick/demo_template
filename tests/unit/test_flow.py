"""The flow orchestrator itself: order, shared data, cleanup. No system under test needed."""

import allure
import pytest

from framework.flow import Flow, Step

pytestmark = [pytest.mark.unit, allure.feature("Framework"), allure.story("Flow orchestrator")]


def _record(log: list[str], name: str, cleanup: bool = True, fail: bool = False) -> Step:
    def action(ctx):
        log.append(f"do {name}")
        if cleanup:
            ctx.defer(name, log.append, f"undo {name}")
        if fail:
            raise RuntimeError(f"{name} failed")

    return Step(name, action)


@pytest.mark.smoke
@pytest.mark.tc("TC-UNIT-001")
def test_steps_run_in_order_and_cleanup_runs_in_reverse():
    log: list[str] = []

    with Flow() as flow:
        flow.then(_record(log, "a")).then(_record(log, "b")).then(_record(log, "c")).run()

    assert log == ["do a", "do b", "do c", "undo c", "undo b", "undo a"]


@pytest.mark.smoke
@pytest.mark.tc("TC-UNIT-002")
def test_steps_share_data_through_context():
    def produce(ctx):
        ctx["secret"] = "s-1"

    def consume(ctx):
        ctx["seen"] = ctx["secret"]

    with Flow(root="/qa") as flow:
        flow.then(Step("produce", produce)).then(Step("consume", consume)).run()

        assert flow.ctx["seen"] == "s-1"
        assert flow.ctx["root"] == "/qa"


@pytest.mark.smoke
@pytest.mark.tc("TC-UNIT-003")
def test_cleanup_runs_when_a_step_fails():
    log: list[str] = []

    with pytest.raises(RuntimeError, match="b failed"), Flow() as flow:
        flow.then(_record(log, "a")).then(_record(log, "b", fail=True)).then(_record(log, "c")).run()

    assert log == ["do a", "do b", "undo b", "undo a"], "c must not run; a and b must be undone"


@pytest.mark.regression
@pytest.mark.tc("TC-UNIT-004")
def test_failing_cleanup_does_not_stop_other_cleanups():
    log: list[str] = []

    def broken(ctx):
        ctx.defer("broken", lambda: (_ for _ in ()).throw(RuntimeError("cleanup failed")))

    with pytest.raises(RuntimeError, match="cleanup failed"), Flow() as flow:
        flow.then(_record(log, "a")).then(Step("broken", broken)).run()

    assert log == ["do a", "undo a"], "a must be undone even though a later cleanup failed"


@pytest.mark.regression
@pytest.mark.tc("TC-UNIT-005")
def test_run_can_be_called_again_for_the_next_phase():
    log: list[str] = []

    with Flow() as flow:
        flow.then(_record(log, "arrange")).run()
        flow.then(_record(log, "act", cleanup=False)).run()

    assert log == ["do arrange", "do act", "undo arrange"]

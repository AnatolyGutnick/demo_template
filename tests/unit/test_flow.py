"""The flow orchestrator itself: order, shared data, cleanup. No system under test needed."""

import allure
import pytest

from framework.flow import Flow, Step

pytestmark = [allure.feature("Framework"), allure.story("Flow orchestrator")]


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
    # Arrange: a log that every step and every cleanup writes to
    log: list[str] = []

    # Act: run three steps a, b, c; leaving the "with" block closes the flow (runs cleanups)
    with Flow() as flow:
        flow.then(_record(log, "a")).then(_record(log, "b")).then(_record(log, "c")).run()

    # Assert: steps ran in order, cleanups in reverse order
    assert log == ["do a", "do b", "do c", "undo c", "undo b", "undo a"]


@pytest.mark.smoke
@pytest.mark.tc("TC-UNIT-002")
def test_steps_share_data_through_context():
    # Arrange: one step writes to the context, the next step reads what the first wrote
    def produce(ctx):
        ctx["secret"] = "s-1"

    def consume(ctx):
        ctx["seen"] = ctx["secret"]

    with Flow(root="/qa") as flow:
        # Act: run both steps on a flow started with root="/qa"
        flow.then(Step("produce", produce)).then(Step("consume", consume)).run()

        # Assert: the second step saw the first step's data, and the start data is there
        assert flow.ctx["seen"] == "s-1"
        assert flow.ctx["root"] == "/qa"


@pytest.mark.smoke
@pytest.mark.tc("TC-UNIT-003")
def test_cleanup_runs_when_a_step_fails():
    # Arrange: three steps, the middle one (b) fails
    log: list[str] = []

    # Act: run them; the failure must come out of the flow, not be swallowed
    with pytest.raises(RuntimeError, match="b failed"), Flow() as flow:
        flow.then(_record(log, "a")).then(_record(log, "b", fail=True)).then(_record(log, "c")).run()

    # Assert: c never ran, and what a and b created was still cleaned up
    assert log == ["do a", "do b", "undo b", "undo a"], "c must not run; a and b must be undone"


@pytest.mark.regression
@pytest.mark.tc("TC-UNIT-004")
def test_failing_cleanup_does_not_stop_other_cleanups():
    # Arrange: step a (normal cleanup), then a step whose cleanup raises an error
    log: list[str] = []

    def failing_cleanup():
        raise RuntimeError("cleanup failed")

    def broken(ctx):
        ctx.defer("broken", failing_cleanup)

    # Act: run and close the flow; the cleanup error must still be reported
    with pytest.raises(RuntimeError, match="cleanup failed"), Flow() as flow:
        flow.then(_record(log, "a")).then(Step("broken", broken)).run()

    # Assert: a was cleaned up even though the cleanup registered after it failed
    assert log == ["do a", "undo a"], "a must be undone even though a later cleanup failed"


@pytest.mark.regression
@pytest.mark.tc("TC-UNIT-005")
def test_run_can_be_called_again_for_the_next_phase():
    # Arrange: a log, and a flow used in two phases
    log: list[str] = []

    # Act: run an "arrange" step, then queue and run an "act" step on the same flow
    with Flow() as flow:
        flow.then(_record(log, "arrange")).run()
        flow.then(_record(log, "act", cleanup=False)).run()

    # Assert: each step ran once, in order, and the arrange step was cleaned up at the end
    assert log == ["do arrange", "do act", "undo arrange"]

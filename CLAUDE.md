# CLAUDE.md - working rules for AI in this repo

## Project
API + UI test automation: Python, pytest, Playwright (sync), Page Object Model, Allure.

## Commands
- Install: `pip install -e .[dev] && playwright install chromium`
- All tests: `pytest`
- Smoke only: `pytest -m smoke`
- Parallel: `pytest -n auto`
- Headed debug: `pytest tests/ui -k <name> --headed --slowmo 300`
- Report: `allure serve allure-results`
- Lint: `ruff check . && ruff format --check .`

## Layout
- `framework/pages` - page objects, `framework/pages/components` - reusable UI parts
- `framework/api` - API clients (one per resource) on `BaseClient`
- `framework/models` - pydantic response contracts
- `framework/data` - test data factories (unique data per test)
- `tests/api | ui | e2e` - tests per layer; `tests/<layer>/<category>/` - one folder per category.
  Layer and category markers + Allure suites come from the folder (hook in `tests/conftest.py`) - do not add them by hand.
- `framework/flow` - generic flow orchestrator; `framework/steps` - reusable steps per system
- `docs/` - system review, strategy, test cases, bugs, AI log

## Rules
- Page objects: locators + actions only, **no assertions**. Navigating actions return the next page object.
- Locators: `get_by_role`, `get_by_label`, `get_by_test_id`. No XPath, no `wait_for_timeout`/sleep.
- Assertions: `expect(...)` for UI (auto-retry), plain `assert` + pydantic model for API.
- Every test: `@allure.feature`, `@allure.story`, a priority marker (`smoke`/`regression`) and `@pytest.mark.tc("ID")`
  matching `docs/03-test-cases.md`.
- Test body: `# Arrange:`, `# Act:`, `# Assert:` comments, each saying in words what happens.
- Tests are independent: own data via API, cleanup in `finally` / fixture teardown.
- Prefer API for setup and verification; use UI only for what the test is about.
- A known bug -> `@pytest.mark.xfail(reason="BUG-00X ...", strict=True)` + entry in `docs/04-bugs.md`.
- Never invent system behaviour: if unsure, explore the app (Playwright MCP) or ask.
- After AI-assisted work, add a row to `docs/AI_USAGE.md`.

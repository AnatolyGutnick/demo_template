# demo_template

API + UI test automation template - Python, pytest, Playwright, Page Object Model, Allure.

**Allure report:** https://anatolygutnick.github.io/demo_template/ (published by CI on every push to `main`)

## How to read this repo

The test design is in `docs/`, the code follows it:

1. [System review](docs/01-system-review.md) - what the system does, observed behaviour, open questions
2. [Test strategy](docs/02-test-strategy.md) - risks, priorities, what is tested at API vs UI level,
   [framework design diagrams](docs/02-test-strategy.md#framework-design---chain-of-steps)
3. [Test cases](docs/03-test-cases.md) - every case with technique, priority, layer; IDs link to the code and Allure
4. [Bugs](docs/04-bugs.md) - defects found, with evidence
5. [AI usage](docs/AI_USAGE.md) - how AI was used, what was kept, changed or dropped

## Structure

```
framework/
  flow/         generic flow orchestrator: chain of steps + cleanup stack (no system code)
  steps/        reusable steps per system (Akeyless secret access pipeline)
  pages/        Page Object Model (locators + actions, no assertions)
  api/          API clients on Playwright APIRequestContext (credentials masked in reports)
  models/       pydantic response contracts
  data/         test data factories
  config.py     settings from env vars
tests/
  unit/         the flow orchestrator itself - runs without any system
  api/          one folder per pipeline stage (category):
    auth/       identity -> token
    items/      values, versions, delete
    access/     role rules decision table
                folder = marker + Allure suite, set by a hook (`pytest -m access`)
  ui/           user-visible behaviour
  e2e/          arrange via API -> act in UI -> verify via API
```

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -e .[dev]
playwright install chromium
cp .env.example .env            # set BASE_URL, API_URL, users

pytest                          # all
pytest -m smoke                 # P1 only
pytest -n auto                  # parallel
pytest tests/ui --headed        # watch the browser

allure serve allure-results     # open the report (needs Allure CLI)
```

## Results

<!-- Fill at the end: X cases designed, Y automated, Z bugs found, link to the CI run. -->

## What I would do next

<!-- With more time: ... -->

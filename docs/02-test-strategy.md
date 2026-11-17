# 2. Test strategy

## Scope

**In scope:**

**Out of scope (and why):**

## Risk analysis

Priority = impact x likelihood. Drives what gets automated first.

| Area | Impact (H/M/L) | Likelihood (H/M/L) | Priority | Why |
|------|----------------|--------------------|----------|-----|
|      |                |                    |          |     |

- **P1** - smoke: automated, runs on every commit
- **P2** - regression: automated if time allows
- **P3** - documented, manual / future

## Test levels - what goes where

| Level | What it covers                                                    | Why at this level               |
|-------|-------------------------------------------------------------------|---------------------------------|
| API   | Business rules, validation, contracts, negative cases             | Fast, stable, precise failures  |
| UI    | User-visible behaviour, messages, navigation                      | Only what the user sees         |
| E2E   | Few critical journeys: arrange via API, act in UI, verify via API | Proves the layers work together |

## Test design techniques

- Equivalence partitioning / boundary values - input fields, limits
- Decision table - rule combinations
- State transitions - entity lifecycle
- Negative / error handling - auth, invalid data, missing resources

## Test data

- Created per test via API (`framework/data`), unique names -> independent, parallel-safe
- Cleaned up after the test

## Environment & execution

- Config via env vars (`.env.example`); no secrets in the repo
- Local: `pytest`; CI: GitHub Actions on push, Allure report published

## Risks to the testing itself

<!-- e.g. shared environment, no test data reset, rate limits -->

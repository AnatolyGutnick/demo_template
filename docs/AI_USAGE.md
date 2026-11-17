# AI usage

Tools: Claude Code (Opus 5.5), Playwright MCP.

Principle: AI drafts, I decide. Every AI output was reviewed, run, and checked against the real
system before it was kept.

## Log

| # | Step               | What I asked                     | What AI produced                   | Kept      | Changed / dropped - and why                                                                |
|---|--------------------|----------------------------------|------------------------------------|-----------|--------------------------------------------------------------------------------------------|
| 1 | Project skeleton   | Template for API+UI, POM, Allure | Framework layout, base classes, CI | Structure | Removed a trace-attach fixture: trace is written after context close, so it never attached |
| 2 | System exploration | Research Akeyless public API docs, pick a feature | API summary per endpoint, scope = Static Secrets + roles, open questions | Scope, endpoint facts | Kept only what the OpenAPI spec states; unknowns (error codes, limits) listed as questions, not guessed |
| 3 | Test ideas | Strategy + test cases for Static Secrets | Risk table, levels, 26 cases, access decision table, lifecycle states | Draft - review pending | To review against a live account; expected results marked (explore) where docs are silent |
| 4 | Page objects       |                                  |                                    |           |                                                                                            |
| 5 | Review             |                                  |                                    |           |                                                                                            |
| 6 | Framework design | Chain-of-steps pattern (from my earlier design), shown as diagrams | Layer diagram + chain-run flowchart (Mermaid) | Diagrams | Asked to stop and plan before code; kept asserts in the test, not hidden in the flow |
| 7 | Flow code + pipeline tests | Build the generic Flow and the Akeyless secret access pipeline | Flow (ExitStack), unit tests, API client, steps, 3 test groups | All, after review | Endpoint names checked in the API reference first; credentials masked in the public Allure report; each decision-table row gets its own TC ID; cases not fully covered marked "partly" |
| 8 | Category folders | Folder per category, category name sent to each test | Folders + conftest hook: folder -> marker + Allure suite; markers registered from folders | All | Chose dynamic marker registration so a new folder needs no pyproject change; checked labels in a real allure-results file |

## Where AI helped most

## Where AI was wrong / needed correction

## What I would not delegate to AI

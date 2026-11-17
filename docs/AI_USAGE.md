# AI usage

Tools: Claude Code (Opus 5.5), Playwright MCP.

Principle: AI drafts, I decide. Every AI output was reviewed, run, and checked against the real
system before it was kept.

## Log

| # | Step               | What I asked                     | What AI produced                   | Kept      | Changed / dropped - and why                                                                |
|---|--------------------|----------------------------------|------------------------------------|-----------|--------------------------------------------------------------------------------------------|
| 1 | Project skeleton   | Template for API+UI, POM, Allure | Framework layout, base classes, CI | Structure | Removed a trace-attach fixture: trace is written after context close, so it never attached |
| 2 | System exploration |                                  |                                    |           |                                                                                            |
| 3 | Test ideas         |                                  |                                    |           |                                                                                            |
| 4 | Page objects       |                                  |                                    |           |                                                                                            |
| 5 | Review             |                                  |                                    |           |                                                                                            |

## Where AI helped most

## Where AI was wrong / needed correction

## What I would not delegate to AI

Review the tests changed on this branch (or "$ARGUMENTS") against the rules in CLAUDE.md.

Check: assertions inside page objects, brittle locators, sleeps, tests depending on each other or on shared data,
missing cleanup, missing Allure labels / tc marker, test name not matching behaviour, a case in code but not in
`docs/03-test-cases.md` (or the reverse), UI used where API would prove the same thing.

Report findings as a list: file:line - problem - suggested fix. Do not edit files.

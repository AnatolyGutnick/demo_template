# 3. Test cases

IDs match `@pytest.mark.tc("...")` in the code and the Allure ID label. Automated "yes" / "partly" = the test is
written (partly = some of the listed checks); it runs once an Akeyless test account is configured, otherwise it is
skipped with a clear reason. Test files live in one folder per category (`tests/api/auth|items|access/`).
System: Akeyless Static Secrets + access roles. Expected results come from the public docs; points
marked *(explore)* depend on an open question in [01-system-review.md](01-system-review.md).

| ID         | Feature        | Scenario                                                                                     | Layer | Technique           | Priority | Automated | Test                                    |
|------------|----------------|----------------------------------------------------------------------------------------------|-------|---------------------|----------|-----------|-----------------------------------------|
| TC-API-001 | Auth           | Valid access-id + key -> 200, `token` and `expiration` match contract                        | API   | Contract            | P1       | yes       | `tests/api/auth/test_access_key.py`     |
| TC-API-002 | Auth           | Wrong access key -> 401, `{"error"}`, no token                                               | API   | Negative            | P1       | yes       | `tests/api/auth/test_access_key.py`     |
| TC-API-003 | Lifecycle      | Create generic secret -> get-secret-value returns the exact value                            | API   | State transition    | P1       | yes       | `tests/api/items/test_values.py`        |
| TC-API-004 | Auth           | get-secret-value with no token / garbage token / other account's token -> rejected, no value | API   | Negative, EP        | P1       | partly    | `tests/api/auth/test_token_required.py` |
| TC-API-005 | Versions       | Update with `keep-prev-version: "true"` -> latest = new value, previous version = old value  | API   | State transition    | P1       | yes       | `tests/api/items/test_versions.py`      |
| TC-API-006 | Lifecycle      | Delete (`version: -1`) -> get-secret-value fails, list-items no longer shows it              | API   | State transition    | P1       | yes       | `tests/api/items/test_delete.py`        |
| TC-API-007 | Lifecycle      | Create with an existing name -> error, original value unchanged *(explore)*                  | API   | Negative            | P2       | planned   |                                         |
| TC-API-008 | Lifecycle      | Read / update / delete a secret that does not exist -> `{"error"}`, not 200                  | API   | Negative            | P2       | planned   |                                         |
| TC-API-009 | Validation     | Names: empty, missing, nested path `/a/b/c`, unicode, spaces, max length / max+1 *(explore)* | API   | EP, BVA             | P2       | planned   |                                         |
| TC-API-010 | Validation     | Values: empty, multiline, `format: json` valid / invalid JSON, max size / max+1 *(explore)*  | API   | EP, BVA             | P2       | planned   |                                         |
| TC-API-011 | Read           | One get-secret-value call with 2 names returns both; one missing name -> clear error         | API   | EP                  | P2       | planned   |                                         |
| TC-API-012 | Versions       | `version: -N`: -1, -20 (max) return N versions; -21 -> error or capped *(explore)*           | API   | BVA                 | P2       | planned   |                                         |
| TC-API-013 | List           | list-items by `path`, `filter`, `tag`, `type: static-secret` returns only matching items     | API   | EP                  | P2       | planned   |                                         |
| TC-API-014 | Delete protect | `delete_protection: "true"` -> delete rejected, value still readable                         | API   | Decision table      | P2       | planned   |                                         |
| TC-API-015 | Versions       | rollback-secret to v1 -> current value = v1 value, history kept                              | API   | State transition    | P2       | planned   |                                         |
| TC-API-016 | Access         | Role `read` on `/qa/ro/*`: read allowed; update, delete, create denied                       | API   | Decision table      | P1       | partly    | `tests/api/access/test_role_rules.py`   |
| TC-API-017 | Access         | Role with `deny` on a path that another rule allows -> read denied                           | API   | Decision table      | P1       | yes       | `tests/api/access/test_role_rules.py`   |
| TC-API-018 | Access         | Role `list` only: item visible in list-items, get-secret-value denied                        | API   | Decision table      | P2       | partly    | `tests/api/access/test_role_rules.py`   |
| TC-API-019 | Access         | Role on `/qa/teamA/*` cannot read `/qa/teamB/x` or `/qa/teamA-x` (prefix trap)               | API   | Decision table, BVA | P1       | yes       | `tests/api/access/test_role_rules.py`   |
| TC-API-020 | Access         | Rule removed from role -> next read with a new token is denied                               | API   | State transition    | P2       | planned   |                                         |
| TC-API-021 | Security       | list-items / describe-item never contain the secret value                                    | API   | Contract            | P2       | planned   |                                         |
| TC-UI-001  | Console        | Create secret in Console -> shown in Items tree; value verified via API                      | UI    | Happy path          | P1       | planned   |                                         |
| TC-UI-002  | Console        | Secret value is masked by default, shown only after "reveal"                                 | UI    | Security UX         | P1       | planned   |                                         |
| TC-UI-003  | Console        | Create with empty name / empty value -> validation message, nothing created (API check)      | UI    | Negative            | P2       | planned   |                                         |
| TC-E2E-001 | Versions       | Secret created via API -> value edited in Console -> API returns new value, old version kept | E2E   | State transition    | P1       | planned   |                                         |
| TC-E2E-002 | Access         | Read-only user in Console sees the value but cannot edit or delete                           | E2E   | Decision table      | P2       | planned   |                                         |

## Access rules - decision table (TC-API-016..019)

Each row runs once per identity type (parametrized fixture `identity_type`: `api_key` now, `certificate`
planned and skipped).

Identity = limited access key bound to one test role. Secret = `/qa-autotest/<run>/...`.

| # | Rule on the secret's path     | Other rule       | read | list | update | delete | Case |
|---|-------------------------------|------------------|------|------|--------|--------|------|
| 1 | read                          | -                | yes  | no   | no     | no     | 016  |
| 2 | read, update                  | -                | yes  | no   | yes    | no     | 016  |
| 3 | read                          | deny (same path) | no   | no   | no     | no     | 017  |
| 4 | list                          | -                | no   | yes  | no     | no     | 018  |
| 5 | read on a sibling folder only | -                | no   | no   | no     | no     | 019  |
| 6 | none                          | -                | no   | no   | no     | no     | 019  |

## Lifecycle - state transitions (TC-API-003, 005, 006, 015)

```
(none) --create--> v1 --update(keep prev)--> v2 --rollback(v1)--> v3 (= v1 value)
                    \                         \                      \
                     +--------- delete (version -1) ---------------> (deleted: read fails)
```

## Framework self-tests

The flow orchestrator is tested on its own (no system needed), so a framework bug never looks like a product bug.

| ID          | Scenario                                                 | Test                      |
|-------------|----------------------------------------------------------|---------------------------|
| TC-UNIT-001 | Steps run in order, cleanup runs in reverse              | `tests/unit/test_flow.py` |
| TC-UNIT-002 | Steps share data through the context                     | `tests/unit/test_flow.py` |
| TC-UNIT-003 | A failing step stops the chain, earlier steps are undone | `tests/unit/test_flow.py` |
| TC-UNIT-004 | A failing cleanup does not stop the other cleanups       | `tests/unit/test_flow.py` |
| TC-UNIT-005 | `run()` again for the next phase (arrange, then act)     | `tests/unit/test_flow.py` |

## Not automated - and why

| ID         | Scenario                                                         | Reason                                                 |
|------------|------------------------------------------------------------------|--------------------------------------------------------|
| TC-MAN-001 | Token expires after its TTL -> rejected                          | Needs waiting for real TTL; check once manually        |
| TC-MAN-002 | Gateway cache serves a stale value after update (`ignore-cache`) | Needs a deployed Gateway                               |
| TC-MAN-003 | Audit log shows who read / changed the secret                    | Valuable (P2) - automate after exploring the audit API |
| TC-MAN-004 | Console keyboard navigation and screen reader on item view       | Accessibility review, manual                           |

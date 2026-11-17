# 1. System review

> System under test: **Akeyless Secrets Management** (SaaS), feature **Static Secrets + access roles**.
> Source so far: public docs and the OpenAPI reference (docs.akeyless.io, read 2026-11-17).
> Not yet verified on a live account - everything below is "documented", and each point gets
> confirmed or corrected during exploration. Open points are listed as questions, not guessed.

## What the system does

Akeyless is a SaaS platform that stores and hands out secrets (passwords, API keys, certificates,
encryption keys) to people and machines. Teams use it instead of keeping credentials in code,
config files or CI variables. The main value: one place for secrets, access controlled by roles,
every value versioned and audited. Users are developers, DevOps/platform engineers (API, CLI,
SDKs, Kubernetes, CI plugins) and security admins (web Console).

**Feature chosen for this task - Static Secrets.** A static secret is a named value that a person
creates and updates by hand (e.g. a DB password). It is the simplest item type, the most used, and
the base for everything else: if create/read/update/delete or access control is wrong here, the
product fails at its core promise. It is also small enough to test properly in a short task.

## Main flows

| # | Flow                        | Entry point (UI / API)                                           | Notes (from docs)                                                                       |
|---|-----------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 1 | Authenticate (access key)   | `POST /auth`                                                     | `access-id` + `access-key` -> `token`, `expiration`. Error: 401 `{"error": "..."}`      |
| 2 | Create static secret        | `POST /create-secret`; Console > Items > New                     | Required `name`, `value`. `type` generic/password, `format` text/json/key-value, `tags` |
| 3 | Read secret value           | `POST /get-secret-value`; Console item view                      | `names` is an array. `version` N = that version, -N = last N versions (max 20)          |
| 4 | Update value (new version)  | `POST /update-secret-val`; Console edit                          | `keep-prev-version` true/false, account default if unset                                |
| 5 | Roll back to an old version | `rollback-secret` (CLI; REST to confirm)                         | `old-version` becomes the current value                                                 |
| 6 | List / search items         | `POST /list-items`; Console Items tree                           | Filter by `path`, `filter`, `tag`, `type`; paginated (`next_page`)                      |
| 7 | Delete secret               | `POST /delete-item`; Console delete                              | `version` -1 = whole item, 0 = last version; returns `deletion_date`                    |
| 8 | Grant access                | `POST /create-role`, `POST /set-role-rule`, role <-> auth method | Rule = `path` + `capability` [read, create, update, delete, list, deny]                 |

## Architecture as seen from outside

- **UI:** web Console (console.akeyless.io). Items are shown as a folder tree; names are paths
  (`/team/app/db-password`).
- **API:** REST, `https://api.akeyless.io`, every operation is `POST /<command>` with a JSON body.
  The auth token goes **in the body** (`token` field), not in an `Authorization` header.
  Errors use one shape: `{"error": "<message>"}`. The spec documents only 200 and "default" for
  most commands, so exact error status codes must be observed.
- **Also:** CLI and SDKs wrap the same API; an optional customer-hosted Gateway with a cache
  (`ignore-cache` flag on reads).
- **Notable behaviour:**
  - State: an item has versions; `max-versions` is limited by account settings.
  - Access: deny-by-default; a role grants capabilities on a path (wildcards), `deny` blocks.
  - Async: deletion has a `deletion_date` (may be scheduled, not immediate - to confirm for secrets).
  - Cache: reads through a Gateway can be served from cache.

## Open questions / assumptions

| #  | Question                                                               | Assumption made                                                                            | Impact if wrong                             |
|----|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------------|
| 1  | HTTP status for each error (missing item, no permission, duplicate)?   | Non-2xx + `{"error"}`; tests assert the shape and "not 200", status pinned after exploring | Weaker negative asserts until confirmed     |
| 2  | Creating a secret with an existing name - error or overwrite?          | Error, original value unchanged                                                            | TC-API-007 expected result flips            |
| 3  | Name rules: allowed characters, max length, leading `/`?               | Path-like names allowed; limits unknown -> explore                                         | Boundary cases for TC-API-009               |
| 4  | Max value size?                                                        | Unknown -> find by exploring, then boundary test                                           | TC-API-010 limits                           |
| 5  | Account defaults for `keep-prev-version` and `max-versions`?           | Tests set `keep-prev-version` explicitly                                                   | Version tests flaky if left to defaults     |
| 6  | What happens on update beyond `max-versions`?                          | Oldest version is dropped                                                                  | TC-API-012                                  |
| 7  | Is a deleted static secret gone at once or soft-deleted?               | Gone for reads at once (`delete-in-days` is for keys)                                      | Cleanup and TC-API-006                      |
| 8  | Does `list-items` / `describe-item` ever return the value?             | Never (only metadata)                                                                      | Security leak - would be a bug              |
| 9  | Token TTL and refresh                                                  | Long enough for a test run; one token per session                                          | Long runs may need re-auth                  |
| 10 | Test account: free tier limits (items, API rate)?                      | Enough for ~50 items per run                                                               | Need cleanup sweeper / throttling           |
| 11 | `get-secret-value` response shape (schema is "any properties")?        | `{"<secret name>": "<value>"}`                                                             | TC-API-003/005 read the value wrongly       |
| 12 | Is an API-key auth method used with `/auth` `access-type: access_key`? | Yes (same access-id / access-key pair)                                                     | `limited_identity` step and TC-API-016..019 |

## Observations / suspicious behaviour

- The OpenAPI spec defines no specific error codes (only `default`), so clients can't rely on
  status codes from the docs alone - test them, and report gaps as doc issues.
- `update-secret-val` takes `keep-prev-version` as a **string** `"true"/"false"`, while most flags
  are booleans - worth a negative test (`true` as boolean, `"yes"`).
- `get-secret-value` response schema is "any properties" - the contract test pins the real shape
  once observed.

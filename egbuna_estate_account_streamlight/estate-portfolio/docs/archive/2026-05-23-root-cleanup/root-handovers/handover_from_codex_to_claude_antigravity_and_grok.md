# Handover From Codex To Claude Antigravity And Grok

## Session State

- Active git branch: `test`
- Branch was created from `main`
- `test` was created specifically to keep all `epm-tests` investigation and follow-up work off `main`
- Existing uncommitted workspace changes were carried onto `test`; nothing was reverted

## What Codex Has Done

1. Investigated `egbuna_estate_account_streamlight/estate-portfolio/epm-tests` in read-only mode.
2. Confirmed that `epm-tests` is a test harness/spec directory, not a standalone deployable service.
3. Mapped `epm-tests` files to the current `estate-portfolio` backend and frontend codebase.
4. Confirmed the strongest drift is in the backend test suite, not the frontend unit tests.
5. Updated `AGENTS.md` to require agents to work on `test` and never directly on `main`.
6. Carried migrated tests into the live `estate-portfolio` backend and frontend projects on branch `test`.
7. Executed the adapted backend and frontend test suites successfully on branch `test`.

## Work Carried Out On Branch `test`

### Repo governance

- Added a new `Branch Discipline` section to `AGENTS.md`
- Explicit rule now states agents must work on `test`
- Explicit rule now states only Antigravity / The Builder may merge stable code into `main`

### Frontend test integration

Migrated compatible `epm-tests` frontend coverage into the live frontend project:

- `estate-portfolio-manager/tests/unit/stores/authStore.test.ts`
- `estate-portfolio-manager/tests/unit/stores/uiStore.test.ts`
- `estate-portfolio-manager/tests/unit/hooks/useTheme.test.ts`
- `estate-portfolio-manager/tests/unit/hooks/useCountUp.test.ts`
- `estate-portfolio-manager/tests/unit/lib/format.test.ts`
- `estate-portfolio-manager/vitest.config.ts`

Frontend support changes made:

- added `test` and `test:watch` scripts to `estate-portfolio-manager/package.json`
- added frontend test dependencies through `npm install`
- updated `estate-portfolio-manager/src/hooks/useCountUp.ts` to reset to zero when the target changes
- updated `estate-portfolio-manager/src/lib/format.ts` to accept `number | string`, matching the API-driven usage expected by the migrated tests

### Backend test integration

Adapted mapped backend tests to the current FastAPI layout instead of the older modular layout assumed by `epm-tests`:

- `backend/tests/conftest.py`
- `backend/tests/unit/test_deps.py`
- `backend/tests/unit/test_auth_router.py`
- `backend/tests/unit/test_holdings_router.py`

Backend test strategy:

- kept tests aligned with the current `app.deps`, `app.routers.auth`, and `app.routers.holdings` layout
- avoided the hanging ASGI client path in this environment by calling async route functions directly in router unit tests
- mocked password verification at the router unit boundary to avoid local `passlib` / `bcrypt` backend issues unrelated to route behavior

## Verification Results

### Backend

Command run:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 TMPDIR=/tmp pytest -q egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_deps.py egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_holdings_router.py egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_auth_router.py
```

Result:

- `12 passed`
- `1 warning`

Warning observed:

- `python-jose` emits a deprecation warning for `datetime.utcnow()` inside the library, not in the newly added tests

### Frontend

Commands run:

```bash
cd egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager
npm install
npm test
```

Result:

- `5` test files passed
- `21` tests passed
- `0` frontend test failures

## Current Practical State

- The mapped frontend tests that had direct source matches are now live and passing.
- A meaningful subset of the mapped backend tests is now live and passing against the current backend architecture.
- The larger backend drift identified earlier still exists for the unmigrated `epm-tests` files that assume missing modules, missing schema packages, and missing endpoint families.

## High-Level Findings

### 1. `epm-tests` is not standalone

`epm-tests` contains only:

- backend test files
- frontend test files
- empty `.github/workflows/`
- no local app code
- no local `package.json`
- no local backend package/module tree
- no local docker compose file

It relies on the surrounding project:

- `egbuna_estate_account_streamlight/estate-portfolio/backend/`
- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/`
- `egbuna_estate_account_streamlight/estate-portfolio/docker-compose.yml`

### 2. Frontend alignment is partial-to-good

Most frontend unit tests in `epm-tests` target files that exist in:

- `estate-portfolio-manager/src/store/`
- `estate-portfolio-manager/src/hooks/`
- `estate-portfolio-manager/src/lib/`

But the current frontend package does not yet declare the test runner setup needed to run them.

### 3. Backend alignment is poor

The backend tests assume a larger modular FastAPI codebase than currently exists. The checked-in backend is flatter and smaller:

- current backend has `app/config.py`, `app/database.py`, `app/deps.py`, `app/models.py`, `app/main.py`, and a few routers
- tests expect subpackages like `app.auth.logic`, `app.auth.dependencies`, `app.models.users`, `app.schemas.*`, `app.services.portfolio`, and `app.scripts.seed_admin`

This is still true for the unmigrated backend files in `epm-tests`. The newly added backend tests were deliberately adapted to the current backend rather than blindly copied.

### 4. Docs violate the current OpenAgile deployment law

The estate project docs still instruct direct SSH and manual `docker compose` operations on the server. That conflicts with current OpenAgile rules requiring GitHub Actions mediated deployment.

## Infrastructure Notes Relevant To `epm-tests`

- Surrounding estate app is routed through Traefik at `estate.zubbystudio.shop`
- Surrounding estate app uses external Docker network `openagile_openagile_network`
- Surrounding estate app expects shared Postgres rather than a dedicated database container
- `epm-tests` backend integration tests are designed to hit shared Postgres with rollback isolation

## File-By-File Mapping

### Backend tests

| `epm-tests` file | Current codebase mapping | Status | Notes |
|---|---|---|---|
| `epm-tests/backend/tests/integration/conftest.py` | `estate-portfolio/backend/app/main.py`, `estate-portfolio/backend/app/database.py`, `estate-portfolio/backend/app/deps.py`, `estate-portfolio/backend/app/models.py` | Partial | `app.main` and DB layer exist, but `get_db`, `app.auth.logic`, and `app.models.users` do not exist in current tree. |
| `epm-tests/backend/tests/unit/test_api_routes.py` | `estate-portfolio/backend/app/main.py`, `estate-portfolio/backend/app/routers/auth.py`, `estate-portfolio/backend/app/routers/dashboard.py`, `estate-portfolio/backend/app/routers/holdings.py`, `estate-portfolio/backend/app/deps.py` | Partial | Route targets exist in part, but imports like `app.auth.logic` do not. Response envelope assumptions also appear richer than current backend. |
| `epm-tests/backend/tests/unit/test_auth_logic.py` | `estate-portfolio/backend/app/deps.py`, `estate-portfolio/backend/app/config.py` | Partial | JWT/auth logic currently lives in `app/deps.py`, not `app.auth.logic` or `app.auth.dependencies`. Function names and signatures differ. |
| `epm-tests/backend/tests/unit/test_business_logic.py` | No current equivalent | Missing | No `app/services/portfolio.py` exists. Business calculations are not currently factored into a standalone service module. |
| `epm-tests/backend/tests/unit/test_pydantic_schemas.py` | No current equivalent | Missing | No `app/schemas/` package exists in the checked-in backend. |
| `epm-tests/backend/tests/unit/test_seed_admin.py` | `estate-portfolio/backend/scripts/seed_admin.py` | Partial | A seed script exists, but it is in `backend/scripts/seed_admin.py`, not `app.scripts.seed_admin`. Function name and env var contract differ. |
| `epm-tests/backend/tests/contract/test_api_contract.py` | `estate-portfolio/backend/app/main.py`, routers, models | Partial | Contract assumes many endpoints not present in current backend: companies, prices, dividends, transactions, registrars, watchlist, nav-history, rebalancing. |
| `epm-tests/backend/tests/db/test_schema_integrity.py` | `estate-portfolio/backend/alembic/`, `estate-portfolio/backend/app/models.py`, `estate-portfolio/init_db.sql` | Partial-to-missing | Test expects a much larger schema and more migrations than are currently checked in. |
| `epm-tests/backend/tests/integration/test_auth_integration.py` | `estate-portfolio/backend/app/routers/auth.py`, `estate-portfolio/backend/app/deps.py` | Partial | Auth endpoints exist, but referenced helper modules and model layout do not fully match. |
| `epm-tests/backend/tests/integration/test_holdings_integration.py` | `estate-portfolio/backend/app/routers/holdings.py`, `estate-portfolio/backend/app/models.py` | Partial | Holdings endpoint exists, but status/draft/soft-delete semantics in tests may be ahead of current implementation. |
| `epm-tests/backend/tests/integration/test_prices_integration.py` | No current equivalent | Missing | No dedicated prices router/service found in current backend tree. |
| `epm-tests/backend/tests/performance/` | No files yet | Placeholder | Directory exists but contains no test files. |

### Frontend tests

| `epm-tests` file | Current codebase mapping | Status | Notes |
|---|---|---|---|
| `epm-tests/frontend/tests/unit/stores/authStore.test.ts` | `estate-portfolio-manager/src/store/authStore.ts` | Good | Target store exists and uses Zustand. |
| `epm-tests/frontend/tests/unit/stores/uiStore.test.ts` | `estate-portfolio-manager/src/store/uiStore.ts`, `estate-portfolio-manager/src/store/authStore.ts` | Good | Both target stores exist. |
| `epm-tests/frontend/tests/unit/hooks/useTheme.test.ts` | `estate-portfolio-manager/src/hooks/useTheme.ts` | Good | Target hook exists. |
| `epm-tests/frontend/tests/unit/hooks/useCountUp.test.ts` | `estate-portfolio-manager/src/hooks/useCountUp.ts` | Good | Target hook exists. |
| `epm-tests/frontend/tests/unit/lib/format.test.ts` | `estate-portfolio-manager/src/lib/format.ts` | Good | Target formatting helpers exist. |
| `epm-tests/frontend/tests/unit/components/` | Current components exist under `estate-portfolio-manager/src/components/` | Placeholder | No component test files are present yet. |
| `epm-tests/frontend/tests/e2e/` | No checked-in E2E suite | Placeholder | Directory exists but contains no test files. |

## Current Source Trees That Matter

### Backend actually present

- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/config.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/database.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/deps.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/main.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/models.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/auth.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/dashboard.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/holdings.py`
- `egbuna_estate_account_streamlight/estate-portfolio/backend/scripts/seed_admin.py`

### Frontend actually present

- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/store/authStore.ts`
- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/store/uiStore.ts`
- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/hooks/useTheme.ts`
- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/hooks/useCountUp.ts`
- `egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/lib/format.ts`

## Concrete Drift Points

### Backend package layout drift

Tests expect:

- `app.auth.logic`
- `app.auth.dependencies`
- `app.models.users`
- `app.models.companies`
- `app.models.holdings`
- `app.schemas.*`
- `app.services.portfolio`
- `app.scripts.seed_admin`

Current backend provides:

- `app.deps`
- `app.models`
- `backend/scripts/seed_admin.py`

### Function and contract drift

- Tests expect `create_access_token(data={...})`
- Current backend exposes `create_access_token(user_id: int, role: str)` in `app/deps.py`
- Tests expect `verify_password` and `hash_password`
- Current checked-in auth flow does not expose those at the expected import path
- Tests expect `get_db`
- Current backend exposes `get_session`

### Schema drift

Tests expect:

- many tables beyond the currently visible Alembic history
- richer status semantics
- soft-delete behavior across multiple entities
- list endpoints with `meta.total`
- standardized `{ data, error }` or `{ data, meta, error }` envelopes

Current backend likely only partially satisfies that contract.

### Frontend test-runner drift

Frontend tests use:

- `vitest`
- `@testing-library/react`

Current `estate-portfolio-manager/package.json` does not yet declare:

- a `test` script
- `vitest`
- `@testing-library/react`

So the frontend test files are mapped to real source files but are not yet wired for execution.

## Deployment-Law Violations Found

These files should be treated carefully before any merge back to `main`:

- `egbuna_estate_account_streamlight/estate-portfolio/CI_CD_SETUP.md`
- `egbuna_estate_account_streamlight/estate-portfolio/deploy.sh`

Problems:

- direct SSH guidance
- manual server-side `docker compose` instructions
- operational steps that conflict with current OpenAgile GitHub-Actions-only deployment law

## Recommended Next Steps On `test`

1. Continue migrating only the `epm-tests` files that can be cleanly adapted to the current backend architecture.
2. Decide whether to build out the missing backend modules expected by the remaining `epm-tests`, or rewrite those remaining tests against the current architecture.
3. Rewrite estate deployment docs to remove direct SSH/manual Docker operational guidance before any merge back to `main`.
4. Keep all additional testing and refactoring on branch `test` until the unmigrated backend drift is resolved.

## Safe Working Rule

Continue all corrections, rewrites, and validation on branch `test`.

Do not merge back to `main` until:

- backend/frontend mapping decisions are explicit
- deployment-law violations in docs/scripts are resolved
- the intended test architecture is stable

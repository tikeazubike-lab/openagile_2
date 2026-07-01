# EPM — Software Testing Lifecycle (STLC)
**Authored by**: Claude (The Brain)
**Input from**: Grok (Zone 2 Spotter — Testing Lifecycle Spec)
**Date**: 2026-04-20
**Stack**: FastAPI + SQLAlchemy + shared openagile_postgres + React 18 (TanStack Start/Router) + Vite + Tailwind v4
**Execution environment**: GitHub Actions ONLY — Netcup VPS (Ubuntu 24.04, 8 vCPU / 16 GB)
**Protocol**: MASTER_CONTEXT.md v3.0 — No local Docker, no new Postgres instances, shared DB reused

---

## Guiding Principles

1. **Shift-Left** — bugs are cheapest at unit level. Every layer of the pyramid below catches what the layer above it missed.
2. **Shared DB, zero side-effects** — all DB-touching tests run inside a transaction that is rolled back after each test. The production schema is never mutated by tests.
3. **No new infrastructure** — no new Postgres container, no new Redis, no Cypress Cloud account. Everything uses existing openagile_network and GitHub Actions secrets.
4. **Fail fast** — each pipeline stage blocks the next. A unit test failure never wastes CI minutes on E2E tests.
5. **Separation of concerns** — a CI config check (ENDSSH quoting) belongs in a shell/YAML linting stage, not in an acceptance checklist. A cookie behaviour belongs in E2E, not in a unit test. Each test type owns its domain.

---

## The Testing Pyramid (EPM-Specific)

```
                    ┌─────────────┐
                    │  UAT / UAT  │  Manual, stakeholder sign-off (OpenProject)
                    └──────┬──────┘
                  ┌────────┴────────┐
                  │  Non-Functional │  Perf + Security + Accessibility + Regression
                  └────────┬────────┘
               ┌───────────┴───────────┐
               │   System / E2E Tests  │  Playwright — full stack, staging only
               └───────────┬───────────┘
          ┌────────────────┴────────────────┐
          │  Integration + Contract + DB     │  pytest + httpx + shared Postgres
          └────────────────┬────────────────┘
    ┌──────────────────────┴──────────────────────┐
    │              Unit Tests                      │  pytest (FastAPI) + Jest/RTL (React)
    └─────────────────────────────────────────────┘
```

Fastest and most numerous at the bottom. Slowest and fewest at the top.
Each layer runs ONLY after the layer below it passes.

---

## Stage 0: Pre-Commit / Static Analysis
**Trigger**: Every commit, runs in < 30 seconds locally (pre-commit hook) and in CI
**Blocks**: Nothing passes Stage 1 if Stage 0 fails

### 0.1 — Backend Linting & Type Checking
**Tool**: `ruff` (linter) + `mypy` (type checker)
**Scope**: All files in `backend/`
**What it catches**:
- Import errors, undefined names, unused variables
- Type mismatches in FastAPI route signatures and SQLAlchemy models
- Pydantic v2 model violations

### 0.2 — Frontend Linting & Type Checking
**Tool**: `eslint` + `tsc --noEmit`
**Scope**: All files in `frontend/src/`
**What it catches**:
- TypeScript type errors (API response shape mismatches caught here before runtime)
- Unused imports, unreachable code
- React hook rule violations

### 0.3 — CI Configuration Validation
**Tool**: `actionlint` (GitHub Actions YAML linter)
**Scope**: `.github/workflows/*.yml`
**What it catches**:
- **The ENDSSH quoting bug** — `actionlint` flags unquoted heredoc delimiters as a known interpolation risk
- Invalid workflow syntax, missing required secrets references
- Deprecated action versions

### 0.4 — Dependency Security Scan
**Tool**: `pip-audit` (backend) + `npm audit` (frontend)
**Scope**: `backend/requirements.txt` + `frontend/package.json`
**What it catches**:
- Known CVEs in pinned dependencies
- The bcrypt/passlib version conflict class of bug (pip-audit flags known incompatibilities)

### 0.5 — Secret Detection
**Tool**: `truffleHog` or `gitleaks`
**Scope**: Full git diff on every commit
**What it catches**:
- Accidentally committed passwords, API keys, JWT secrets
- Hardcoded `admin/admin123` credentials in source files

---

## Stage 1: Unit Tests
**Trigger**: Every PR and every push to `main` or `develop`
**Execution**: Parallel matrix jobs (backend + frontend run simultaneously)
**Blocks merge if**: Any test fails OR coverage < 85%
**Runtime target**: < 5 minutes total

### 1A — Backend Unit Tests (pytest + FastAPI TestClient)

**Location**: `backend/tests/unit/`
**Infrastructure**: No database. All DB calls mocked with `unittest.mock` or `pytest-mock`.
**Coverage tool**: `pytest-cov` with `--cov=app --cov-fail-under=85`

#### 1A.1 — Authentication Logic
```
test_password_hashing_produces_bcrypt_hash()
test_password_verification_correct_password_returns_true()
test_password_verification_wrong_password_returns_false()
test_jwt_token_creation_contains_correct_claims()
test_jwt_token_creation_sets_correct_expiry()
test_jwt_token_decode_valid_token_returns_payload()
test_jwt_token_decode_expired_token_raises_exception()
test_jwt_token_decode_tampered_token_raises_exception()
test_require_admin_dependency_admin_role_passes()
test_require_admin_dependency_readonly_role_raises_403()
test_require_admin_dependency_no_user_raises_401()
test_get_current_user_valid_cookie_returns_user()
test_get_current_user_missing_cookie_raises_401()
```

#### 1A.2 — Pydantic Schema Validation
```
test_login_schema_rejects_empty_username()
test_login_schema_rejects_empty_password()
test_holding_schema_rejects_negative_shares()
test_holding_schema_rejects_negative_price()
test_price_entry_rejects_future_date()
test_price_entry_rejects_negative_price()
test_price_entry_rejects_price_above_100000_naira()  ← sanity cap from spec
test_dashboard_response_monetary_values_are_strings() ← not floats
test_transaction_schema_accepts_all_valid_types()     ← buy/sell/bonus_receipt/rights_subscription
test_transaction_schema_rejects_unknown_type()
```

#### 1A.3 — Business Logic (portfolio.py service)
```
test_current_value_calculation(shares=100, price=50.00, expected=5000.00)
test_cost_basis_calculation(shares=100, avg_price=40.00, expected=4000.00)
test_return_pct_positive_gain(current=5000, cost=4000, expected=+25.0)
test_return_pct_negative_loss(current=3000, cost=4000, expected=-25.0)
test_return_pct_zero_cost_basis_does_not_divide_by_zero()
test_dividend_yield_calculation(annual_div=5.0, price=100.0, expected=5.0)
test_dividend_yield_zero_price_does_not_divide_by_zero()
test_rebalancing_gap_overweight(current_pct=35.0, target_pct=30.0, expected=+5.0)
test_rebalancing_gap_underweight(current_pct=18.0, target_pct=20.0, expected=-2.0)
test_rebalancing_on_target_within_tolerance(current=30.1, target=30.0)
test_wht_deduction(gross=1000.00, rate=0.10, expected_net=900.00)
test_portfolio_total_value_sums_live_holdings_only()
test_portfolio_total_excludes_draft_holdings()
```

#### 1A.4 — API Route Units (TestClient, mocked DB)
```
test_login_endpoint_valid_credentials_sets_httponly_cookie()
test_login_endpoint_valid_credentials_returns_user_object()
test_login_endpoint_invalid_credentials_returns_401()
test_logout_endpoint_clears_epm_token_cookie()
test_logout_endpoint_returns_200_without_cookie_present()  ← idempotent
test_auth_me_endpoint_with_valid_cookie_returns_user()
test_auth_me_endpoint_without_cookie_returns_401()
test_holdings_endpoint_excludes_deleted_records_by_default()
test_holdings_endpoint_excludes_draft_records_for_readonly_role()
test_holdings_endpoint_includes_draft_records_for_admin_role()
test_price_quick_entry_writes_to_price_audit_log()
test_soft_delete_sets_deleted_at_not_destroys_row()
test_publish_holding_flips_status_draft_to_live()
```

#### 1A.5 — seed_admin.py Unit Tests
```
test_seed_admin_creates_user_when_none_exists()
test_seed_admin_is_idempotent_when_user_already_exists()  ← the critical one
test_seed_admin_reads_password_from_environment_variable()
test_seed_admin_does_not_use_hardcoded_credentials()
test_seed_admin_hashed_password_is_not_plaintext_in_db()
```

---

### 1B — Frontend Unit Tests (Jest + React Testing Library)

**Location**: `frontend/src/__tests__/unit/`
**Infrastructure**: No real API. All fetch calls mocked via `msw` (Mock Service Worker).
**Coverage tool**: `jest --coverage --coverageThreshold='{"global":{"lines":85}}'`

#### 1B.1 — Zustand Store Logic
```
authStore: test_initial_state_is_null_user()
authStore: test_set_user_populates_store()
authStore: test_clear_user_resets_to_null()
authStore: test_is_admin_returns_true_for_admin_role()
authStore: test_is_admin_returns_false_for_readonly_role()
authStore: test_is_admin_returns_false_when_no_user()

uiStore: test_edit_mode_defaults_to_false()
uiStore: test_toggle_edit_mode_requires_admin_role()
uiStore: test_toggle_edit_mode_does_nothing_for_readonly()
uiStore: test_sidebar_open_defaults_to_false()
uiStore: test_toggle_sidebar_flips_boolean()
```

#### 1B.2 — useTheme Hook
```
test_default_theme_reads_system_preference_light()
test_default_theme_reads_system_preference_dark()
test_toggle_from_light_saves_dark_to_localstorage()
test_toggle_from_dark_saves_system_to_localstorage()
test_persisted_dark_preference_applies_dark_class_on_mount()
test_persisted_system_preference_reads_matchmedia_on_mount()
test_resolved_theme_is_light_when_system_is_light()
test_resolved_theme_is_dark_when_forced()
test_theme_change_adds_removes_dark_class_on_html_element()
```

#### 1B.3 — useCountUp Hook
```
test_count_up_starts_at_zero()
test_count_up_reaches_target_value_after_duration()
test_count_up_resets_and_replays_when_target_changes()
test_count_up_handles_zero_target_without_animation()
test_count_up_handles_negative_values()
```

#### 1B.4 — Utility Functions (lib/format.ts)
```
test_fmt_naira_formats_positive_number_with_symbol()
test_fmt_naira_formats_zero_correctly()
test_fmt_naira_formats_negative_as_loss()
test_fmt_naira_handles_string_input_from_api()   ← API returns strings not floats
test_fmt_pct_formats_positive_with_plus_prefix()
test_fmt_pct_formats_negative_with_minus_prefix()
test_fmt_pct_formats_zero()
```

#### 1B.5 — Component Unit Tests

**Login Component**
```
test_login_renders_username_and_password_fields()
test_login_renders_sign_in_button()
test_login_shows_spinner_during_submission()
test_login_shows_error_message_on_401_response()
test_login_does_not_contain_skip_to_demo_link()  ← regression guard
test_login_does_not_store_token_in_localstorage() ← security guard
```

**Navbar Component**
```
test_navbar_renders_page_title()
test_navbar_shows_edit_mode_toggle_for_admin()
test_navbar_hides_edit_mode_toggle_for_readonly()
test_navbar_shows_moon_icon_in_light_mode()
test_navbar_shows_sun_icon_in_dark_mode()
test_navbar_theme_toggle_visible_to_both_roles()
test_navbar_shows_bell_icon_for_admin_only()
test_navbar_avatar_dropdown_contains_sign_out()
```

**Sidebar Component**
```
test_sidebar_renders_all_main_nav_items()
test_sidebar_renders_admin_section_for_admin()
test_sidebar_hides_admin_section_for_readonly()
test_sidebar_highlights_active_route()
test_sidebar_logout_button_calls_api_before_clearing_store()  ← logout bug regression test
test_sidebar_logout_navigates_to_login_after_api_call()
test_sidebar_logout_clears_store_even_if_api_fails()         ← finally block test
```

**Holdings Table**
```
test_holdings_table_renders_correct_column_headers()
test_holdings_return_pct_header_is_exact_text()              ← "return[%]" exactly
test_holdings_positive_return_renders_green()
test_holdings_negative_return_renders_red()
test_holdings_draft_row_has_amber_left_border()
test_holdings_draft_rows_hidden_for_readonly()
test_holdings_actions_column_hidden_in_view_mode()
test_holdings_actions_column_visible_in_edit_mode_for_admin()
test_holdings_publish_button_visible_on_draft_rows_in_edit_mode()
```

**Dashboard KPI Cards**
```
test_kpi_card_renders_label_and_value()
test_kpi_card_count_up_animation_fires_on_mount()
test_kpi_card_positive_change_renders_green()
test_kpi_card_negative_change_renders_red()
test_kpi_card_total_holdings_shows_draft_count_for_admin()
test_kpi_card_total_holdings_hides_draft_count_for_readonly()
```

---

## Stage 2: Integration Tests + API Contract Tests + Database Tests
**Trigger**: After Stage 1 passes
**Execution**: Sequential (contract → DB schema → API integration)
**Infrastructure**: Connects to `openagile_postgres` via `openagile_network`. All DB operations wrapped in `BEGIN` / `ROLLBACK` savepoints — zero permanent side effects.
**GitHub Actions secrets required**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`
**Runtime target**: < 10 minutes

### 2A — API Contract Tests (Pydantic + OpenAPI)
**What**: Validates that every endpoint's response schema matches the contract defined in Part B of the handover.
**Tool**: `pytest` + `fastapi.testclient` + `jsonschema`

```
test_openapi_schema_is_valid_json()
test_all_api_routes_are_documented_in_openapi()
test_dashboard_response_matches_contract_schema()
test_holdings_response_monetary_fields_are_strings_not_floats()
test_holdings_response_contains_return_pct_field()
test_auth_me_response_contains_role_field()
test_auth_login_response_sets_httponly_cookie_not_json_token()
test_error_responses_use_standard_envelope()              ← { data, meta, error }
test_404_responses_return_json_not_html()
test_all_list_endpoints_return_meta_with_total()
test_soft_deleted_records_absent_from_default_responses()
test_draft_records_absent_from_readonly_role_responses()
```

### 2B — Database Tests (Schema Integrity)
**What**: Verifies migrations ran correctly and constraints are enforced.
**Tool**: `pytest` + `sqlalchemy` + direct DB inspection
**Pattern**: Each test opens a transaction, does its work, rolls back.

```
── Schema existence
test_all_required_tables_exist()
  → nav_history, watchlist, price_audit, sector_targets, corporate_actions, users,
    holdings, companies, dividends, transactions, registrars, price_history

── Column existence (new additive migrations)
test_holdings_has_status_column_with_default_live()
test_holdings_has_deleted_at_column()
test_dividends_has_source_column()
test_dividends_has_is_scrip_column()
test_dividends_has_scrip_shares_column()
test_users_table_has_role_column_defaulting_to_readonly()
test_price_audit_has_source_column()

── Constraints
test_holdings_company_id_unique_constraint_enforced()
test_users_username_unique_constraint_enforced()
test_nav_history_snapshot_date_unique_constraint_enforced()
test_soft_delete_does_not_violate_unique_constraint()     ← deleted rows excluded from unique check

── Foreign keys
test_holdings_company_id_fk_references_companies()
test_price_audit_company_id_fk_references_companies()
test_watchlist_company_id_fk_references_companies()
test_corporate_actions_company_id_fk_references_companies()

── Data integrity
test_monetary_columns_are_numeric_not_varchar()
test_status_column_rejects_invalid_values()               ← only 'draft' | 'live'
test_deleted_at_defaults_to_null()

── Alembic
test_alembic_current_head_matches_schema()
test_alembic_downgrade_and_upgrade_is_reversible()
```

### 2C — API Integration Tests (FastAPI + Real DB)
**What**: Tests the full request → handler → DB → response path with real Postgres.
**Tool**: `pytest` + `httpx.AsyncClient` + transaction rollback fixture

```
── Auth flow (real DB)
test_login_creates_session_cookie_against_real_db()
test_login_rejects_wrong_password_against_real_db()
test_logout_clears_cookie_verified_by_subsequent_me_call()
test_auth_me_returns_correct_role_from_db()
test_change_password_updates_hash_in_db()

── Holdings CRUD (real DB)
test_create_holding_defaults_to_draft_status()
test_publish_holding_changes_status_to_live_in_db()
test_soft_delete_holding_sets_deleted_at_in_db()
test_restore_holding_clears_deleted_at_in_db()
test_readonly_role_cannot_see_draft_holdings_from_api()
test_admin_role_can_see_draft_holdings_from_api()
test_duplicate_company_holding_is_rejected_by_db_constraint()

── Price entry (real DB)
test_quick_price_entry_creates_price_audit_record()
test_price_audit_stores_old_and_new_price()
test_price_revert_restores_previous_value_in_db()
test_bulk_csv_import_updates_multiple_prices_atomically()
test_bulk_csv_import_rolls_back_on_partial_failure()      ← atomicity test

── NAV history
test_nav_snapshot_inserts_row_into_nav_history()
test_nav_snapshot_is_idempotent_for_same_day()            ← UNIQUE constraint on date

── Soft delete
test_soft_deleted_records_excluded_from_list_endpoints()
test_soft_deleted_records_returned_with_include_deleted_param()
test_include_deleted_param_rejected_for_readonly_role()
```

---

## Stage 3: Build
**Trigger**: After Stage 2 passes
**What**: Docker multi-stage build — React compiled, static files baked into FastAPI container
**Blocks**: Stages 4+ if build fails

```
── Build validation (checked in CI logs, not separate tests)
✓ npm ci completes without error
✓ npm run build produces non-empty dist/ directory
✓ dist/index.html exists
✓ dist/assets/ contains at least one .js and one .css file
✓ CSS file is > 10KB (Tailwind compiled with utilities)
✓ docker build completes without error
✓ Image size is within acceptable range (< 500MB)
✓ No secrets present in docker image layers (truffleHog scan on image)
```

---

## Stage 4: Deploy to Staging + E2E Tests
**Trigger**: After Stage 3 passes
**Environment**: `demo.estate.zubbystudio.shop` on openagile_network
**Tool**: Playwright (TypeScript)
**Location**: `frontend/tests/e2e/`
**Runtime target**: < 15 minutes

### 4A — E2E: Authentication Flows
```
test_e2e_login_with_valid_credentials_reaches_dashboard()
test_e2e_login_with_invalid_credentials_shows_error_message()
test_e2e_login_form_shows_spinner_during_api_call()
test_e2e_direct_url_dashboard_while_logged_out_redirects_to_login()
test_e2e_direct_url_holdings_while_logged_out_redirects_to_login()
test_e2e_hard_refresh_on_dashboard_preserves_session()
test_e2e_logout_clears_cookie_and_redirects_to_login()
test_e2e_logout_back_button_does_not_restore_dashboard()
test_e2e_cookie_is_httponly_not_accessible_via_js()
test_e2e_settings_price_entry_blocked_for_readonly_role()
```

### 4B — E2E: Static Asset Delivery
```
test_e2e_index_html_cache_control_is_no_cache()
test_e2e_asset_bundles_return_200()
test_e2e_deep_link_refresh_on_holdings_returns_spa_not_404()
test_e2e_deep_link_refresh_on_settings_returns_spa_not_404()
test_e2e_unknown_route_shows_react_404_not_fastapi_json()
```

### 4C — E2E: Theme System
```
test_e2e_moon_icon_visible_in_light_mode()
test_e2e_clicking_moon_switches_to_dark_mode()
test_e2e_sun_icon_visible_after_dark_mode_activated()
test_e2e_dark_mode_persists_after_page_refresh()
test_e2e_clicking_sun_returns_to_system_theme()
test_e2e_no_flash_of_wrong_theme_on_initial_load()
```

### 4D — E2E: Dashboard
```
test_e2e_dashboard_kpi_cards_render_with_values()
test_e2e_dashboard_count_up_animation_completes()
test_e2e_sector_donut_chart_renders()
test_e2e_top_holdings_bar_chart_renders()
test_e2e_recent_transactions_table_renders()
test_e2e_action_items_card_renders()
test_e2e_dashboard_auto_refreshes_within_65_seconds()
```

### 4E — E2E: Holdings CRUD (Admin)
```
test_e2e_holdings_table_renders_all_columns()
test_e2e_return_pct_column_header_is_exact_text()
test_e2e_edit_mode_toggle_shows_actions_column()
test_e2e_create_new_holding_as_draft()
test_e2e_draft_holding_not_counted_in_portfolio_value()
test_e2e_publish_holding_updates_portfolio_value()
test_e2e_soft_delete_holding_removes_from_table()
test_e2e_deleted_holding_appears_in_settings_deleted_records()
test_e2e_restore_deleted_holding_reappears_in_table()
```

### 4F — E2E: Price Entry
```
test_e2e_quick_price_entry_updates_current_price()
test_e2e_price_change_reflected_in_dashboard_kpi()
test_e2e_csv_upload_column_mapping_ui_renders()
test_e2e_csv_upload_preview_shows_valid_and_invalid_rows()
test_e2e_csv_commit_updates_prices_in_bulk()
test_e2e_price_audit_log_shows_recent_changes()
test_e2e_revert_price_change_restores_previous_value()
```

---

## Stage 5: Non-Functional Tests
**Trigger**: After Stage 4 (E2E) passes
**Environment**: `demo.estate.zubbystudio.shop` staging

### 5A — Performance (Locust)
**Location**: `backend/tests/performance/locustfile.py`
```
Scenarios:
  load_test_dashboard_endpoint()     → 50 concurrent users, 60s ramp
  load_test_holdings_endpoint()      → 50 concurrent users, 60s ramp
  load_test_price_quick_entry()      → 20 concurrent users (write path)
  load_test_auth_login_logout()      → 20 concurrent users

Acceptance thresholds:
  P95 response time < 500ms for GET endpoints
  P95 response time < 1000ms for POST endpoints
  Error rate < 1% under load
  No memory leak: container RAM stable after 5-minute soak
```

### 5B — Security (SAST + DAST)
```
Bandit (SAST — Python):
  bandit -r backend/app/ -ll             ← medium+ severity fails build
  Catches: hardcoded passwords, SQL injection patterns, insecure random

Snyk (dependency CVEs):
  snyk test --file=backend/requirements.txt
  snyk test --file=frontend/package.json
  Catches: known CVEs in pinned packages (bcrypt/passlib class of issue)

OWASP ZAP (DAST — against staging):
  Passive scan on demo.estate.zubbystudio.shop
  Active scan on /api/v1/ endpoints
  Catches: XSS, CSRF, missing security headers, cookie flags
  Must verify: epm_token has HttpOnly + Secure + SameSite=Strict flags
```

### 5C — Accessibility (axe-core)
```
Integrated into Playwright E2E suite via @axe-core/playwright:

test_a11y_login_page_has_no_critical_violations()
test_a11y_dashboard_has_no_critical_violations()
test_a11y_holdings_page_has_no_critical_violations()
test_a11y_dark_mode_contrast_meets_wcag_aa()

WCAG 2.1 Level AA minimum. Critical + Serious violations fail the build.
```

### 5D — Regression
```
Full automated suite re-run (Stages 1 + 2 + 4) against the staging build.
Purpose: catches regressions introduced by stage-5 fixes.
Must pass at same coverage thresholds as initial run.
```

---

## Stage 6: UAT (Manual / Stakeholder)
**Trigger**: After all automated stages pass
**Tracked in**: OpenProject (existing instance on openagile_network)
**Participants**: Product Owner (Zubby) + optional readonly viewer (family member)
**Environment**: `demo.estate.zubbystudio.shop`

### UAT Checklist (OpenProject tasks)
```
Session 1: Admin workflow
  [ ] Log in, view dashboard, verify portfolio value looks correct
  [ ] Add a new holding as draft, verify not in portfolio total
  [ ] Publish holding, verify total updates
  [ ] Enter a stock price manually, verify dashboard updates
  [ ] Upload Stooq CSV (if available), verify column mapping UI
  [ ] Log out, verify redirect to login

Session 2: Viewer workflow (switch to readonly account)
  [ ] Log in as viewer, verify dashboard is read-only
  [ ] Confirm no edit mode toggle visible
  [ ] Confirm Price Entry not in sidebar
  [ ] Confirm draft holdings not visible
  [ ] Log out

Session 3: Theme & responsive
  [ ] Toggle to dark mode, reload, confirm persistence
  [ ] View on mobile browser, confirm bottom nav, table scroll
```

**Sign-off gate**: PO sign-off in OpenProject required before production cutover.

---

## GitHub Actions Pipeline Structure

```yaml
# Conceptual pipeline — Antigravity implements the actual YAML

name: EPM CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  # Stage 0 — runs in < 30s
  static-analysis:
    steps: [ruff, mypy, eslint, tsc, actionlint, pip-audit, npm audit, gitleaks]

  # Stage 1 — parallel
  unit-backend:
    needs: static-analysis
    steps: [pytest backend/tests/unit/ --cov --cov-fail-under=85]

  unit-frontend:
    needs: static-analysis
    steps: [jest --coverage --coverageThreshold 85]

  # Stage 2 — sequential, needs both unit jobs
  integration:
    needs: [unit-backend, unit-frontend]
    steps: [pytest backend/tests/integration/ + backend/tests/contract/ + backend/tests/db/]
    env:
      DB_HOST: ${{ secrets.DB_HOST }}
      # ... other secrets

  # Stage 3 — build
  build:
    needs: integration
    steps: [npm ci, npm run build, docker build, truffleHog image scan]

  # Stage 4 — E2E against staging
  e2e:
    needs: build
    steps: [docker compose up -d, playwright test, docker compose down]

  # Stage 5 — non-functional
  non-functional:
    needs: e2e
    steps: [locust headless, bandit, snyk, zap scan, axe-core regression]

  # Stage 6 — deploy to prod (manual trigger after UAT)
  deploy-production:
    needs: non-functional
    if: github.ref == 'refs/heads/main'
    environment: production  # requires manual approval in GitHub
    steps: [SSH to VPS, docker compose up -d estate.zubbystudio.shop]
```

---

## Test File Structure (Codebase Layout)

```
estate-portfolio/
├── backend/
│   └── tests/
│       ├── unit/
│       │   ├── test_auth_logic.py
│       │   ├── test_business_logic.py
│       │   ├── test_api_routes.py
│       │   ├── test_pydantic_schemas.py
│       │   └── test_seed_admin.py
│       ├── integration/
│       │   ├── conftest.py              ← DB transaction rollback fixture
│       │   ├── test_auth_integration.py
│       │   ├── test_holdings_integration.py
│       │   ├── test_prices_integration.py
│       │   └── test_nav_history_integration.py
│       ├── contract/
│       │   └── test_api_contract.py
│       ├── db/
│       │   ├── test_schema_integrity.py
│       │   └── test_constraints.py
│       └── performance/
│           └── locustfile.py
└── frontend/
    └── tests/
        ├── unit/
        │   ├── stores/
        │   │   ├── authStore.test.ts
        │   │   └── uiStore.test.ts
        │   ├── hooks/
        │   │   ├── useTheme.test.ts
        │   │   └── useCountUp.test.ts
        │   ├── lib/
        │   │   └── format.test.ts
        │   └── components/
        │       ├── Login.test.tsx
        │       ├── Navbar.test.tsx
        │       ├── Sidebar.test.tsx
        │       ├── HoldingsTable.test.tsx
        │       └── DashboardKPICard.test.tsx
        └── e2e/
            ├── auth.spec.ts
            ├── static-assets.spec.ts
            ├── theme.spec.ts
            ├── dashboard.spec.ts
            ├── holdings.spec.ts
            ├── price-entry.spec.ts
            └── accessibility.spec.ts
```

---

## Metrics & Quality Gates (Prometheus → Grafana)

| Metric | Gate | Action on fail |
|--------|------|----------------|
| Unit test coverage (backend) | ≥ 85% | Block merge |
| Unit test coverage (frontend) | ≥ 85% | Block merge |
| Integration test pass rate | 100% | Block build |
| E2E test pass rate | 100% | Block non-functional stage |
| P95 API response time | < 500ms | Alert + block deploy |
| Bandit severity | No medium+ | Block deploy |
| Snyk CVEs | No high/critical | Block deploy |
| WCAG violations | No critical/serious | Block deploy |

---

## Next Steps (Immediate)

Following this document, implementation begins in this order:

1. **Unit tests — Backend** (Stage 1A) — Antigravity writes `backend/tests/unit/`
2. **Unit tests — Frontend** (Stage 1B) — Lovable or Antigravity writes `frontend/tests/unit/`
3. **Integration + Contract + DB tests** (Stage 2) — After unit suite is green
4. **GitHub Actions pipeline wiring** — Stages 0 → 2 first, Stages 3 → 5 after build is stable

---

**END OF EPM STLC DOCUMENT**
**Owner**: Claude (The Brain)
**Implements**: Grok's OpenAgile Testing Lifecycle specification
**Version**: 1.0 — expand as new pages are built in Phase 2B

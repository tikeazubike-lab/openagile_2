# F-026: Registrar Requirements Dashboard

| Field | Value |
|---|---|
| Status | **Retroactive spec** — backend built before this spec existed (ratified exception, see §8) |
| Author | Claude Code (architect), 2026-11-23, per ARCHITECT-TAKEOVER-001 |
| Acceptance test | AT-026 |
| Branch | `feature/f-026-dashboard-and-f-026b-reminders` (PR #10) |
| Related | F-026b `F-026-email-reminder-infrastructure.md`; HO-143/144/145 (combined scope) |

## 1. Purpose
Give admins one place to see how complete each company's registrar document requirements are,
what needs attention next, and which companies have no registrar mapped.

## 2. Scope
### In scope (as built, backend)
- `GET /api/v1/registrars/dashboard-summary` (`backend/app/routers/registrars.py`, commit
  `abb9c685230e610e2058b82ca1e728bb7e1c5060`)
- `GET /api/v1/registrar-requirements/global-tracker?page=&page_size=` (same commit)
- Migration `d1e2f3a4b5c6_f026_registrar_dashboard_schema.py` (commit
  `68877326e359079f17eff6dc8af4e49c848d44f6`), additive and guarded by `_table_exists`/`_col_exists`:
  - new table `company_registrars` (company_id, registrar_id, role `primary|co_registrar`,
    created_at, deleted_at; unique (company_id, registrar_id); FKs cascade)
  - `registrars.jurisdiction` (default `nigeria`), `companies.security_type` (default `equity`),
    `registrar_requirements.due_date` (nullable)
### In scope (to build)
- Frontend `RegistrarsDashboard` component on `/registrars` (see §5). Not yet built on any branch.
### Out of scope
- Email delivery (F-026b). Editing requirements from the dashboard (existing modals only).

## 3. API contract (as built)
### `GET /api/v1/registrars/dashboard-summary`
- Auth: any authenticated user (`get_current_user`). Read-only.
- 200: `completion_pct` (number, 1 dp — a percentage, not money), `total_requirements`,
  `completed_requirements`, `pending_requirements`, `top_action_items[]`
  (`requirement_id, task_name, document_title, registrar_name, due_date|null, is_required`),
  `registrar_health {complete, attention, no_data}`, `unmapped_companies {count, companies[≤20]}`.
### `GET /api/v1/registrar-requirements/global-tracker`
- Auth: any authenticated user. Query: `page` (default 1), `page_size` (default 20).
- 200: `rows[]` (`requirement_id, status, task_name, document_title, registrar_name, registrar_id,
  due_date|null, is_required, latest_document|null {id, file_name, status, uploaded_at},
  actions_available[]`), `total, page, page_size, total_pages`.
- `status` derives from the latest document: `completed` → complete, `rejected` → attention, else pending/in_progress.

## 4. Data rules
- No monetary values in this feature. `completion_pct` stays a number.
- Soft-deleted rows (`deleted_at` not null) are excluded.

## 5. Frontend requirements (to build)
- `estate-portfolio-manager/src/components/registrars/RegistrarsDashboard.tsx`, shown at the top of
  `/registrars` (rendered by `RegistrarsLayout.tsx`):
  - summary tiles: completion %, total / completed / pending, registrar health counts
  - "Needs attention" list from `top_action_items`
  - unmapped-companies count with the first 20 names
  - global tracker table (paginated, server-side) using TanStack Table
- Read-only; any action opens the existing modals (no inline editing).
- Before building: check whether a `RegistrarsDashboard` exists in the running container image
  (ARCHITECT-TAKEOVER-001 task 3). Recover it if so; otherwise build from this spec.

## 6. Acceptance criteria (AT-026)
| AC | Given | When | Then |
|---|---|---|---|
| AC-1 | requirements with mixed document states | GET dashboard-summary | counts and `completion_pct` match the data; `registrar_health` buckets sum to the registrar count |
| AC-2 | companies with no `company_registrars` row | GET dashboard-summary | they appear in `unmapped_companies`, capped at 20, `count` is the full number |
| AC-3 | 45 requirements | GET global-tracker `page=2&page_size=20` | 20 rows, `total=45`, `total_pages=3` |
| AC-4 | a requirement whose latest document is `rejected` | GET global-tracker | its row `status` is `attention` (or the as-built equivalent) |
| AC-5 | unauthenticated request | either endpoint | 401 |
| AC-6 | migration run twice on a DB that already has the objects | `alembic upgrade` | no error (guards hold); upgrade path contains no drop/alter |
| AC-7 | `/registrars` page | loads | dashboard tiles and tracker render from the two endpoints; no inline edit controls |

## 7. Tests
- Backend: `backend/tests/integration/test_registrars_dashboard.py` (8 tests, existing) — map them
  to AC-1..AC-5 and add any missing ones. Integration tests run against `epm_test` only.
- Frontend: a vitest for `RegistrarsDashboard` rendering with mocked API responses (AC-7).

## 8. Ratified exception
Backend code and migration were committed (2026-08-28) before any F-026 dashboard spec existed,
breaking the spec-first rule. Ratified by the Product Owner on 2026-11-23 because the schema is
already in production (`alembic_version = e1f2a3b4c5d6`). Logged for the Decision Log in
MASTER_CONTEXT v4.11. The F-026b spec (`ca956a563bc09ffd0db565809b78cc6f51e5ad86`) arrived in
the same commit as its code; ratified on the same basis.

Execute ONLY Part C of the brief below (Parts A and B are done). Working directory is the EPM project dir.

# HO-159 — PR #10 completion brief (Architect → Builder)

| Field | Value |
|---|---|
| From / To | Claude Code (architect/orchestrator) → OpenCode builder (Part A: deepseek-v4.1-flash, run before the model change; Part B: mimo-v2.6-pro) |
| Date | 2026-11-23 |
| Branch | `feature/f-026-dashboard-and-f-026b-reminders` (PR #10), base head `ca5ff5c792fa354bc1501a77e428558a40fa98f7` |
| Specs | `.context/feature-specs/F-026-email-reminder-infrastructure.md` (F-026b), `.context/feature-specs/F-026-registrar-dashboard.md` (F-026) |
| HO block | HO-159..HO-208 approved by Zubbyik 2026-11-23 |
| Trigger | Auditor verdict DEVIATED on PR #10 (findings 4 and 5) |

## Architect rulings (no builder action needed)
- **R-1 Route paths.** Backend stays at `/api/v1/admin/reminders/test-send` and `/api/v1/admin/reminders/log`.
  The locked rule "admin routes at /settings/*, never /admin/*" is about **frontend pages**: HO-024 itself
  defines backend endpoints under `/api/v1/admin/holdings`, and F-016 ships `/api/v1/admin/users`.
  Auditor finding 3 is closed as a false positive. The UI lives under `/settings/` (Part B).
- **R-2 Spec order.** The F-026 and F-026b spec-after-code breaches are ratified exceptions (Product Owner, 2026-11-23),
  recorded in `F-026-registrar-dashboard.md` §8, for the v4.11 Decision Log.

## Part A — backend tests (role: builder)
Scope: test files only under `backend/tests/`. **Do not change application code** unless a test proves a bug;
if so, make the smallest fix and say so explicitly in the report.

Add tests for the F-026b acceptance criteria that are missing or mock-only:
| AC | Test to add | Where |
|---|---|---|
| AC-1 | cron run with SMTP config missing/invalid → logs error, does not raise, sends nothing | next to the existing cron tests (find `test_registrar_reminder_cron.py`) |
| AC-3 | requirement with `due_date` in the past → one send, `reminder_type == "overdue"` | same file |
| AC-5 | `POST /api/v1/admin/reminders/test-send` as admin, SMTP send mocked OK → 200 `{"status":"sent",...}`, and no `reminder_log` write | router-level test, follow `backend/tests/unit/test_admin_users.py` (`dependency_overrides`) |
| AC-6 | same endpoint, SMTP send raises → 502, body has no traceback text | same |
| AC-8 | non-admin user → 403 on both endpoints | same |
Each test carries a trace comment: `# Spec: F-026-email-reminder-infrastructure.md | AC-N | Then ...`.

Order: write the tests and commit (RED or GREEN is fine, since the code already exists; report which).
If any fails because of a real bug, fix it in a separate commit.

Run unit tests with a dead database URL so nothing can reach production:
`cd backend && DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none python -m pytest tests/unit -q`
Paste the raw summary line. Do not run `tests/integration`.

## Part B — frontend (role: frontend)
Scope: `estate-portfolio-manager/src/` only.
1. Port the F-026b settings page that already exists on branch `test`, **byte-for-byte**:
   `git show test:egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/routes/_app.settings.registrars.tsx > estate-portfolio-manager/src/routes/_app.settings.registrars.tsx`
2. Add the sidebar entry the same way `test` has it: in `src/components/layout/Sidebar.tsx`,
   `{ to: "/settings/registrars", label: "Registrars", icon: ClipboardList }` (import `ClipboardList` from lucide-react if missing).
   Compare with `git show test:.../Sidebar.tsx` and copy only that entry and import.
3. Regenerate `src/routeTree.gen.ts` with the project's TanStack Router generator
   (`npx @tanstack/router-cli generate`, or whatever `package.json` / vite config uses). Do not hand-edit it.
4. Verify: `npx tsc --noEmit -p tsconfig.json` shows **no new errors** in the files you touched
   (14 errors already exist elsewhere; list any in your files), and `npm run test` (vitest) raw summary.
   Do not run `npm run build`.
5. Do **not** build `RegistrarsDashboard` (F-026 §5). That waits for the task 3 decision.

## Forbidden (enforced by permissions; do not look for workarounds)
Pushing, history rewrite, containers, database clients, Alembic upgrade/downgrade/stamp, reading `.env*`,
editing `opencode.json` / `.claude/` / `.git/`, network fetches, money as float, inline row editing.

## Report back
What changed, raw test output, full 40-char SHAs, what was NOT done, anything you had to decide.

## Part C — F-026 registrar dashboard UI (role: frontend) — added 2026-11-23
Product Owner decision: **rebuild from spec** (no recovery from the running container).
Spec: `.context/feature-specs/F-026-registrar-dashboard.md` §3 (API contract) and §5 (frontend).
Scope: `estate-portfolio-manager/src/` only.

1. Create `src/components/registrars/RegistrarsDashboard.tsx`:
   - Data: `GET /api/v1/registrars/dashboard-summary` and
     `GET /api/v1/registrar-requirements/global-tracker?page=&page_size=20` via `@tanstack/react-query`,
     using the same fetch/auth pattern as `src/routes/_app.settings.registrars.tsx`
     (responses may be wrapped in the `{data, meta, error}` envelope — unwrap the way that file does).
   - Summary tiles (`components/ui/card`): completion % (`completion_pct`, show 1 dp + `%`),
     total / completed / pending requirements, registrar health (complete / attention / no data).
   - "Needs attention" list from `top_action_items` (task, document, registrar, due date or "—").
   - Unmapped companies: count + up to 20 tickers/names.
   - Global tracker: TanStack Table, server-side pagination (`page`, `total_pages`), columns:
     task, document, registrar, status badge, due date, latest document file + status.
     Follow the table pattern in `src/routes/_app.companies.tsx`.
   - Loading (`components/ui/skeleton`) and error states. Read-only: no inline edit controls.
2. Render it at the top of `/registrars` from `src/components/registrars/RegistrarsLayout.tsx`
   (above the existing list/details layout). Keep the existing behaviour unchanged.
3. Test: `src/components/registrars/__tests__/RegistrarsDashboard.test.tsx` (vitest + Testing Library),
   mocking `fetch` for both endpoints; assert tiles, an attention item, and a tracker row render (AT-026 AC-7).
   Trace comment: `// Spec: F-026-registrar-dashboard.md | AC-7 | Then ...`.
   Note: 4 of 9 existing vitest files fail to import because `@testing-library/jest-dom` is missing
   (AUDIT R10). Do not install packages; if your test needs jest-dom matchers, use plain
   `expect(...).toBeTruthy()` / `getByText` instead, and report it.
4. Verify: `npx tsc --noEmit -p tsconfig.json` — no errors in files you touched; `npx vitest run` raw summary.
5. Commit; report SHAs. Do not touch backend code.
6. Architect ruling on Part B escalation 2 (fix it, in a separate commit): in
   `src/routes/_app.settings.registrars.tsx`, unwrap the `{data, meta, error}` envelope for both
   test-send (`recipient`, `status`, `detail`) and the reminder log, check `res.ok` on the log query and
   show an error state instead of "No reminders sent yet." on 4xx/5xx. Prefer the existing helper in
   `src/api/queries` (`fetchApiEnvelope`) if it fits. Byte-for-byte parity with `test` no longer applies.
   Rename the admin sidebar label to "Reminder Settings" to avoid two "Registrars" entries.

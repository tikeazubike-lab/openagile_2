# HO-159 — PR #10 completion brief (Architect → Builder)

| Field | Value |
|---|---|
| From / To | Claude Code (architect/orchestrator) → OpenCode builder (Part A: deepseek-v4.1-flash; Part B: kimi-k2.7-code) |
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

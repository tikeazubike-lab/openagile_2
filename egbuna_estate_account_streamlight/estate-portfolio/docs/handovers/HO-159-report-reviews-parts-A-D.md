== role=reviewer model=opencode-go/deepseek-v4-pro branch=feature/f-026-dashboard-and-f-026b-reminders log=/tmp/claude-1000/-home-zubbyik-openagile-2-egbuna-estate-account-streamlight-estate-portfolio/4ef0d904-59f3-41e9-94e8-eb9be42dd925/scratchpad/runs/20261123-122404-reviewer.jsonl
== denied tool calls:
  ls -la egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/routes/ | head -50; echo "---claims---"; test -f egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/routes/_app.claims.tsx && echo "EXISTS" || echo "MISSING"; echo "---companies.\$id---"; test -f egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/routes/_app.companies.\$id.tsx && echo "EXISTS" || echo "MISSING"
  git log --oneline -1 2755f92 2>/dev/null || echo "commit 2755f92 not found"; echo "---"; git log --oneline ca5ff5c792fa354bc1501a77e428558a40fa98f7~1 -3 2>/dev/null
== errors:
== new commits:
== uncommitted:
== final report:
Review complete. I read the diff range, all three governing documents, the as-built `registrars.py` and `email.py`, and every changed/test file.

## Review — PR #10 (`ca5ff5c..HEAD`, 15 commits)

| # | Severity | file:line | Finding | Evidence |
|---|---|---|---|---|
| 1 | major (pre-existing) | backend/app/routers/registrars.py:189,226,264 | `completion_pct` divides **completed documents** by **requirements**; can exceed 100% and "Completed" tile shows document count, not requirement count. Not introduced by this diff (backend unchanged) but the new dashboard surfaces it as its headline metric. | `completed_reqs = count(RegistrarDocument where status=="completed")` (189) vs `total_reqs = count(RegistrarRequirement)` (183); `completion_pct = round(completed_reqs/total_reqs*100,1)` (226) |
| 2 | minor | backend/tests/unit/test_reminders_router.py:116,136 | AC-6 test mocks the sanitizer away (`send_email` returns a pre-sanitized `detail`), so it never exercises the real `str(e)[:200]` path; `assert "smtplib" not in response.text` is trivially true and does not prove "no raw traceback". | patch returns `{"status":"failed","detail":sanitized}` (116); asserts absent strings (130-136) |
| 3 | minor | backend/tests/unit/test_reminders_router.py:103 | AC-5 "no reminder_log write" assertion `mock_db.add.call_count == 0` is tautological — the endpoint never calls `session.add` on any path, so it can't fail even if a write existed elsewhere. | endpoint calls only `send_test_email` (registrars.py:530-539) |
| 4 | minor | estate-portfolio-manager/src/routeTree.gen.ts:25,35 + `_app.companies.$id.tsx:22` | Scope creep: regenerating routeTree pulled in unrelated pre-existing routes (`/claims`, `/companies/$id`), and `b20b2e6` fixed a broken `function CompanyProfilePage()` declaration in a non-F-026 file. Defensible (needed to keep the generator output compiling) but outside the brief. | regenerated imports `_app.claims`/`_app.companies.$id`; `+function CompanyProfilePage()` |
| 5 | minor | src/components/registrars/RegistrarsDashboard.tsx:87 | Reimplements a local `fetchEnvelopeData` helper instead of reusing `apiFetch`/`fetchApiEnvelope` from `queries.ts`, which the brief said to prefer if it fits. | `async function fetchEnvelopeData<T>` duplicated logic |
| 6 | minor | src/components/registrars/RegistrarsDashboard.tsx:293-294 | `manualPagination: true` + `pageCount` on `useReactTable` are inert — no `state.pagination` and no `getPaginationRowModel`; pagination is driven purely by the custom `<Pagination>` buttons + pre-paginated `rows`. Works, but dead config. | `getCoreRowModel()` only |

**Verified clean (no finding):**
- **Envelope shapes match** — `{data,meta,error}` unwrapped correctly for `dashboard-summary` and `global-tracker`; the **double-nested log** (`{data:{data:rows,meta}}`) is unwrapped correctly in `_app.settings.registrars.tsx:110-117` and its test fixture.
- **No money-as-float** in scope (`completion_pct` is a percentage, `file_size` bytes).
- **No inline edit controls** — dashboard is read-only; AC-7 test asserts no edit/upload/save buttons, inputs, or links.
- **No insecure change** — test-send/log are server-side `require_admin`; client `isAdmin` guard is defense-in-depth; `error_detail` is `str(e)[:200]` (sanitized) and not rendered by the frontend.
- `isAdmin` store selector (`useAuthStore((s)=>s.isAdmin)()`) is correct (function). `ClipboardList` already imported in Sidebar.

Not run: backend integration tests (forbidden — shared DB) and `tsc`/`vitest` (reviewer is read-only, no build).

**Verdict: SHIP** — no blockers; the frontend correctly consumes the as-built API. Flag finding #1 to the backend owner as a separate correctness fix (out of this diff's scope).

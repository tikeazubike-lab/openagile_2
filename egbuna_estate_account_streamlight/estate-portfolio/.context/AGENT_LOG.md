# Agent Handoff Log

Format: `## YYYY-MM-DD HH:MM UTC — <tool> — <one-line summary>` followed by
2-4 lines of what changed / why / what's next. Newest entries at the top.

---

## 2026-07-03 20:30 UTC — opencode — Added Claude Web back as co-Architect
Claude Web restored as co-Architect with DeepSeek Pro. Both are architects — differentiators: DeepSeek Pro delegates to subagents, Claude Web provides domain expertise. All 14 files updated.

## 2026-07-03 20:15 UTC — opencode — Provider migration: OpenRouter → OpenCode Go + OpenCode Zen
Updated all routing files. OpenCode agents run on OpenCode Go. Hermes runs on OpenCode Zen (deepseek:flash). Nemotron removed. All 12 config files synced.

## 2026-07-03 19:50 UTC — opencode — Endpoint acceptance verification (companies + cost-basis + admin)

Curled all F-NGX-COMPANIES and F-COST-BASIS endpoints against testdrive.epm.zubbystudio.shop:
- GET /api/v1/companies (200) — returns 80+ companies with search/filter
- GET /api/v1/cost-basis (200) — returns 76 cost-basis records
- GET /api/v1/admin/users (200) — returns 5 users with role/is_active
- GET /api/v1/auth/me (200) — returns current user profile
- GET /api/v1/companies/download-template (200) — CSV template
- GET /api/v1/cost-basis/download-template (200) — CSV template
- POST /api/v1/cost-basis/quick (201) — created TEST holding (50 shares @ 100.50)
- POST /api/v1/cost-basis/bulk-csv (201) — dry-run preview + commit (2 holdings created)
- Auth enforcement confirmed: all protected endpoints return 401 without cookie
- docker-compose.v3.yml services healthy (epm_v3, test-builder, streamlit)
Next: Run AT-004 acceptance tests, then proceed with F-016 user management.

## 2026-07-03 16:00 UTC — opencode — F-NGX-COMPANIES + F-COST-BASIS full implementation

Implemented and deployed all 5 tasks:
- Task 1: Architect review — both specs APPROVED (purchase_date col added to holdings)
- Task 2: Backend F-NGX-COMPANIES — pdf_parser.py service, upload-pdf/list/download-template endpoints, 11 unit tests
- Task 3: Frontend F-NGX-COMPANIES — /settings/data-upload route with PDF dropzone, result summary, company list with search/filter
- Task 4: Backend F-COST-BASIS — cost_basis.py router, 3-step ticker matching, claim auto-creation, Alembic migration (purchase_date), 12 unit tests
- Task 5: Frontend F-COST-BASIS — tabs on /settings/data-upload with quick form, bulk CSV preview/commit, records table
All 23 tests pass. Deployed to testdrive.epm.zubbystudio.shop. Migration 7d4e8f2a1c03 ran on DB. Branch: test. Next: acceptance verification by Hermes.

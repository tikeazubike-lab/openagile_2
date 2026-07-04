# Agent Handoff Log

Format: `## YYYY-MM-DD HH:MM UTC — <tool> — <one-line summary>` followed by
2-4 lines of what changed / why / what's next. Newest entries at the top.
Prune entries older than ~30 days or once superseded by a merged HO-*.md.

---

## 2026-07-03 16:00 UTC — opencode — F-NGX-COMPANIES + F-COST-BASIS full implementation
Implemented and deployed all 5 tasks:
- Task 1: Architect review — both specs APPROVED (purchase_date col added to holdings)
- Task 2: Backend F-NGX-COMPANIES — pdf_parser.py service, upload-pdf/list/download-template endpoints, 11 unit tests
- Task 3: Frontend F-NGX-COMPANIES — /settings/data-upload route with PDF dropzone, result summary, company list with search/filter
- Task 4: Backend F-COST-BASIS — cost_basis.py router, 3-step ticker matching, claim auto-creation, Alembic migration (purchase_date), 12 unit tests
- Task 5: Frontend F-COST-BASIS — tabs on /settings/data-upload with quick form, bulk CSV preview/commit, records table
All 23 tests pass. Deployed to testdrive.epm.zubbystudio.shop. Migration 7d4e8f2a1c03 ran on DB. Branch: test. Next: acceptance verification by Hermes.

## 2026-07-03 18:45 UTC — opencode — Agent routing update
Updated `Master_context_Claude_web_2.txt` per user request:
- DeepSeek Flash is now default for BOTH backend AND routine frontend work
- Kimi escalated only when Flash fails same frontend task 3+ times (token budget)
- DeepSeek Pro continues as architecture/orchestration only
- No changes to Nemotron/Qwen/Minimax roles
Reason: Kimi consumed too many tokens on simple frontend tasks. Hermes should
note this routing when dispatching future work.

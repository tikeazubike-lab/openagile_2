# EPM v2 — Baseline Audit (READ-ONLY). Paste into Claude Code at the repo root.

## Role and rules
You are performing a read-only audit of EPM v2. You are NOT the architect and NOT the builder in this task.
- Do NOT edit, create, delete, commit, push, migrate, restart containers, or run any write/DDL/DML.
- Allowed: git (read-only), grep/rg, ls, cat, docker ps/logs/inspect, `psql` with SELECT/\d only, running the existing test suite in read-only mode.
- Evidence standard: paste RAW command output; full 40-char SHAs; never summarise from memory. If a command can't run, say so and why; never guess.
- Write ONLY one new file: `.context/audits/AUDIT-2026-11-21.md` (uncommitted). Do not commit it.

## Baseline documents (in priority order)
1. `original_intent/*` (FOUNDATION_VISION, constraints, decisions, Architecture_spec, agent_roles, model_routing, workflow_design, execution_philosophy) = the INITIAL REQUIREMENT.
2. `.context/MASTER_CONTEXT.md` = current canonical decisions (v4.9 dated 2026-08-13; v4.10 update dated 2026-08-15 may or may not be merged — report which).
3. `.context/feature-specs/*` = per-feature intent.

## Section A — Repo vs server state (do this FIRST; it is the core risk)
```
pwd; git remote -v; git branch -a; git status --short | head -50
git rev-parse HEAD; git rev-parse origin/main; git fetch --dry-run 2>&1
git log --oneline origin/main..HEAD ; git log --oneline HEAD..origin/main
git stash list; git diff --stat origin/main | tail -30
git ls-files --others --exclude-standard | head -50
```
For each running container: image, created time, and the git SHA/label if any (`docker ps --format ...`, `docker inspect`). State plainly: **is what is running on testdrive/production equal to origin/main?** List every divergence.

## Section B — Lost/unmerged work (known recurring failure)
- All local-only commits, all unmerged branches (`git branch -a --no-merged origin/main`), open PRs (`gh pr list --state all --limit 40`, include #10).
- For each HO in the master context marked "complete"/"shipped" (HO-120..HO-153 and every F-xxx marked shipped): is the commit hash cited in the doc reachable from `origin/main`? (`git branch -r --contains <sha>`). Table: HO/F-id | SHA claimed | on origin/main? | notes.
- HO-080..119 were previously lost uncommitted: confirm whether any of that code exists anywhere (reflog, stash, branches, working tree).

## Section C — Feature reality matrix
For EVERY F-xxx in the master context feature table (plus F-013 whose status is disputed): 
| F-id | Doc status | Spec file exists? | Backend route/model exists (grep path) | Frontend route exists | Migration exists | Test exists + passes | Verdict: MATCH / DOC-STALE / CODE-MISSING / UNVERIFIED |
Specifically verify: F-013 `/companies` renders (route + component + test), F-007 `portfolio_nav_history` table & job, F-016 role guards (`ADMIN_ROLES` in `backend/app/deps.py`), F-022, F-026/F-026b, F-TD-001 closure (commit 8dcbdf7abf3290906e0d6d18f23754e143e3df1f).

## Section D — Locked-decision conformance (grep, raw output)
For each, give the command, the output, and PASS/FAIL:
1. Additive-only Alembic: scan `alembic/versions/*` for `drop_`, `alter_column`, `DROP`, `RENAME`.
2. Monetary values returned as strings (grep Decimal/float in schemas/responses).
3. No `editMode|setEditMode|isEditing` in `frontend/src`.
4. JWT in httpOnly cookies (no localStorage token use).
5. Role guard on every `/admin/*` router.
6. bcrypt pinned `4.0.1`.
7. `docker-compose*.yml`: all services on external `openagile_network`, Traefik labels only, no published host ports, no new DB instance.
8. Secrets: `git log -p -S` / `git grep` for committed credentials, .env tracked? (report locations only, DO NOT print secret values — mask them.) Note the known live-secret-in-history item.
9. Branch protection: `gh api repos/{owner}/{repo}/branches/main/protection`.
10. `.github/workflows/` exists? (docs say no — confirm).

## Section E — Process-discipline drift (from git history)
- Commits to main without a PR: `git log origin/main --first-parent --format='%H %an %s' | head -100` vs merged PRs.
- HO numbering: duplicates / self-assigned / gaps vs the Pre-assigned table.
- Specs written AFTER code (compare first commit date of spec vs first commit of feature code) for each shipped F-xxx.
- Tests: count by tier; any xfail/skip markers and their reasons; do any tests mock the DB where SQL correctness is the claim?

## Section F — Doc health
- Is `.context/MASTER_CONTEXT.md` header version/date current? Contradictions between it and code or between sections?
- `original_intent/` vs master context: list every original requirement/constraint that no longer appears, appears changed, or is unimplemented.
- Orphans: `claude_handovers/` duplicates, `swarm-forge/` location, stale archived compose files.

## Output format (write to `.context/audits/AUDIT-2026-11-21.md`)
1. **Verdict table**: area | status (ALIGNED / DEVIATED-RATIFIED / DEVIATED-UNRATIFIED / UNVERIFIED) | one-line evidence pointer.
2. **Top 10 risks** ranked, each with evidence (raw output excerpt) and suggested owner zone.
3. **Deviations**: split into (a) ratified one-off exceptions already in the Decision Log, (b) unratified drift, (c) requirement from original_intent never delivered.
4. **Unknowns**: everything you could not verify and what access you would need.
5. Appendix: all raw command outputs.

Finish by printing: the path of the report, `git status --short` (proving nothing else changed), and the single most dangerous finding.

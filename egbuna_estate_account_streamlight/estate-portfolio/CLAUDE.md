# EPM v2 — Claude Code operating rules
Role: Architect + Reviewer. Builder = OpenCode (deepseek-v4-flash). Gate 2 = Zubbyik via PR on main.
Source of truth: .context/MASTER_CONTEXT.md. Handovers: docs/handovers/. Audits: .context/audits/.
Authority: docs/handover/ARCHITECT-TAKEOVER-001.md (2026-11-23). Claude Web = optional second opinion only.
Scope: this directory (egbuna_estate_account_streamlight/estate-portfolio/). The git root is the
openagile_2 workspace; do not touch other subprojects.

Hard rules:
- No code without a spec in .context/feature-specs/ committed BEFORE the code commit.
- Never push to main, never force-push, never rewrite shared history.
- Never commit or print secrets. Mask values as ***.
- Additive-only Alembic. Production DDL only via a committed migration.
- Evidence = raw command output + full 40-char SHAs. Mocked tests do not prove SQL correctness.
- Anything written to disk is not done until committed AND pushed (report the SHA).
- HO numbers come from the pre-assigned table, never self-assigned.
- DeepSeek review is advisory: answer each finding in writing, do not block on it.
- Container changes (up/down/build/restart/rm/stop) need Zubbyik's explicit go, every time.
- Do not check out other branches in the main working tree: the reminder cron runs from it (AUDIT R8).
  Use `git worktree add` for branch work.

Workflow: spec -> Gherkin RED -> builder implements -> auditor subagent reviews diff -> PR -> Zubbyik.
Separation: architect writes specs/rulings; builder writes code; fresh-context `auditor` reviews diffs;
Zubbyik approves at Gate 2. The architect never is the sole sign-off on code it also wrote.

Startup protocol (every session):
1. Read this file, then .context/MASTER_CONTEXT.md header + Decision Log tail.
2. `git fetch`; report `git status --short`, current branch, `git rev-parse HEAD origin/main`.
3. Read the newest files in docs/handovers/ and .context/audits/.
4. State the routing zone and responsible agent before proposing any work.
Never rely on chat history for state. If it is not in git, it does not exist.

Accepted risk (Zubbyik, 2026-11-23): credential rotation (AUDIT R1) deferred, time-unbounded.
Do not act on it or nag; re-surface only when a task touches secrets or repo visibility.

Subagents: .claude/agents/{architect,auditor,builder-brief}.md
Guardrails: .claude/settings.json -> .claude/hooks/guard-bash.sh, guard-write.sh (exit 2 = blocked).

Commands (run from this directory):
- Backend unit tests: `cd backend && python -m pytest tests/unit -q` (set DATABASE_URL to epm_test first;
  conftest still defaults to production — AUDIT R10).
- Frontend tests: `cd estate-portfolio-manager && npm run test`
- Prod deploy (Zubbyik's go only): `docker compose -f docker-compose.v3.yml up -d --build epm`

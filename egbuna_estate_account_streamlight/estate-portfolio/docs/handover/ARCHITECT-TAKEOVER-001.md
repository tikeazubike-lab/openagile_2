# ARCHITECT-TAKEOVER-001 — Claude Code assumes Architect + Reviewer (Zone 2)

Date: 2026-11-23 | From: Zubbyik (Product Owner, Gate 2) via Claude Web | To: Claude Code (in-repo)
HO number: NOT self-assigned. Pull the next valid number from the pre-assigned table (buffer HO-126..155 is exhausted/overrun: HO-157/158 already used outside it). Propose a new block to Zubbyik in your first report.

## 1. Decision (to be logged in MASTER_CONTEXT Historical Decision Log)

| Item | Ruling |
|---|---|
| Architect + reviewer | Claude Code, working in the repo with direct access. Replaces Claude Web as architect of record. Claude Web becomes an optional second opinion; it is no longer a relay for handovers. |
| DeepSeek Pro | Secondary reviewer. Advisory, NOT a blocker. Its findings must be answered in writing (accepted / rejected + reason) but never halt work. This supersedes the "Zone 2 consensus default" row. |
| Builder | OpenCode CLI + deepseek-v4-flash (escalates to Kimi for complex frontend), unchanged. |
| Gate 2 | Unchanged and still the only independent check: PR + Zubbyik's explicit review on `main`. |
| Handovers | Files committed under `docs/handovers/` in git. No manual relaying between tools. |
| Source of truth | `.context/MASTER_CONTEXT.md` in the repo. Claude Web's project copy is a mirror, never authoritative. |
| Accepted risk (Zubbyik, 2026-11-23) | Credential rotation (AUDIT R1) is deferred by the Product Owner. Log it as an accepted, time-unbounded risk. Do not act on it, and do not nag; re-surface only when a task touches secrets or the repo's visibility. |

Because the architect now also reviews, author/reviewer separation is kept like this: the architect writes specs and rulings; the builder writes code; a fresh-context `auditor` subagent reviews diffs; Zubbyik approves at Gate 2. The architect never approves its own spec as the sole sign-off on code it also wrote.

## 2. Startup protocol (every session)
1. Read `CLAUDE.md`, then `.context/MASTER_CONTEXT.md` header + Decision Log tail.
2. `git fetch`; report `git status --short`, current branch, `git rev-parse HEAD origin/main`.
3. Read the newest files in `docs/handovers/` and `.context/audits/`.
4. State the routing zone and responsible agent before proposing any work.
Never rely on chat history for state. If it is not in git, it does not exist.

## 3. Files to create (on a branch `chore/architect-takeover`, never on main)

### 3a. `CLAUDE.md` (repo root, keep under ~60 lines)
```
# EPM v2 — Claude Code operating rules
Role: Architect + Reviewer. Builder = OpenCode (deepseek-v4-flash). Gate 2 = Zubbyik via PR on main.
Source of truth: .context/MASTER_CONTEXT.md. Handovers: docs/handovers/. Audits: .context/audits/.
Hard rules:
- No code without a spec in .context/feature-specs/ committed BEFORE the code commit.
- Never push to main, never force-push, never rewrite shared history.
- Never commit or print secrets. Mask values as ***.
- Additive-only Alembic. Production DDL only via a committed migration.
- Evidence = raw command output + full 40-char SHAs. Mocked tests do not prove SQL correctness.
- Anything written to disk is not done until committed AND pushed (report the SHA).
- HO numbers come from the pre-assigned table, never self-assigned.
- DeepSeek review is advisory: answer each finding in writing, do not block on it.
Workflow: spec -> Gherkin RED -> builder implements -> auditor subagent reviews diff -> PR -> Zubbyik.
```

### 3b. `.claude/agents/architect.md`, `builder-brief.md`, `auditor.md`
- `architect`: tools Read, Grep, Glob, Bash(read-only git/docker/psql SELECT), Write only under `.context/` and `docs/handovers/`. Produces specs, rulings, HOs.
- `auditor`: read-only (no Write/Edit). Fresh context. Input: a diff range + the spec. Output: findings with raw evidence, verdict ALIGNED / DEVIATED. Must run before every PR.
- `builder-brief`: formats an implementation brief for OpenCode from an approved spec (acceptance criteria, files in scope, RED tests first, forbidden actions). It does not write application code.

### 3c. `.claude/settings.json` — deterministic guardrails (hooks, not prompts)
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": ".claude/hooks/guard-bash.sh" }] },
      { "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": ".claude/hooks/guard-write.sh" }] }
    ]
  }
}
```
`.claude/hooks/guard-bash.sh` (chmod +x). Hook input is JSON on stdin; exit 2 blocks and returns stderr to the model:
```bash
#!/usr/bin/env bash
set -euo pipefail
cmd=$(jq -r '.tool_input.command // ""')
block() { echo "BLOCKED by guard-bash: $1" >&2; exit 2; }
grep -Eq 'git +push.*(--force|-f( |$))' <<<"$cmd"            && block "force push"
grep -Eq 'git +push[^|;&]*( |:)main( |$)' <<<"$cmd"           && block "push to main (Gate 2: PR only)"
grep -Eq 'git +(reset +--hard|filter-branch|rebase +-i)' <<<"$cmd" && block "history rewrite/destructive reset"
grep -Eiq 'psql.*(insert|update|delete|alter|drop|create|truncate)' <<<"$cmd" && block "write SQL via psql (use a committed Alembic migration)"
grep -Eq 'docker +(compose +(up|down|build|restart)|restart|rm|stop)' <<<"$cmd" && block "container change needs Zubbyik's explicit go"
grep -Eq 'cat +.*\.env|printenv|env *$' <<<"$cmd"             && block "would print secrets"
exit 0
```
`.claude/hooks/guard-write.sh`: block writes to `.env*`, `.git/`, `alembic/versions/` deletions, and any new file under `backend/app` or `estate-portfolio-manager/src` unless a spec file referencing it exists (start permissive: warn on stderr, exit 0; tighten after one cycle).
Test every hook with a harmless dry input before relying on it, and paste the raw output.

## 4. First work queue (all non-destructive; deferred item R1 stays deferred)
| # | Task | Notes |
|---|---|---|
| 1 | Create `chore/architect-takeover` with 3a/3b/3c; open PR for Zubbyik | First proof of the new loop |
| 2 | Commit + push the 4 local-only commits and untracked `_app.settings.registrars.tsx` to branches | Fixes R4, R9. Report SHAs |
| 3 | Copy source out of running `estate_portfolio_v3` to a scratch dir (`docker cp`), diff vs `test` and every branch | R2. Ask Zubbyik before any container action |
| 4 | Change `backend/tests/conftest.py` default DB to `epm_test` | R10, tiny PR |
| 5 | Propose (do not execute) the reconciliation strategy test -> main with the Alembic chain fix | Needs a spec + auditor pass + Gate 2 |
| 6 | Draft MASTER_CONTEXT v4.11 as a diff: HO-126..158, F-022 downgraded to "built, not wired", F-013 corrected, spec paths fixed, this takeover decision, accepted risk R1 | Commit to a branch |
| 7 | Stop-the-bleeding rule: no new feature work until 5 and 6 are approved | |

## 5. Report format back to Zubbyik
Per task: what changed, raw command output, full SHAs, what was NOT done, next decision needed. No narrative recap.

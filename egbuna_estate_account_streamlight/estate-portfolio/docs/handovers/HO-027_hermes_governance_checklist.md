# HO-027-GOV — Hermes Governance Review Checklist

**To:** Hermes (OpenCode Zen, `deepseek:flash`)
**Scope:** Review only. Do not modify or implement — flag violations back to `opencode-go/deepseek-v4-flash` and the architects.
**Applies to:** PR implementing HO-027 (Option A PR checks + comment-gated deploy approval)

Approve only if every item below is satisfied. Any single failure blocks merge.

## Infra compliance
- [ ] No `services: postgres` or equivalent new Postgres container anywhere in the workflow YAML or `docker-compose.ci.yml`
- [ ] `docker-compose.ci.yml` references `openagile_network` as `external: true`, does not create a new network
- [ ] `pytest`, `ruff`, `mypy`, `alembic` all run via `docker compose run`, never on the bare runner or system Python
- [ ] All jobs pinned to `runs-on: [self-hosted, epm]` — no `ubuntu-latest` or other GitHub-hosted runner anywhere

## CI/CD contract compliance
- [ ] `test` branch workflow does NOT include an approval gate (per branch flow, only `main` requires approval)
- [ ] `main` branch workflow includes: static analysis → tests → build → approval → deploy → e2e, in that order
- [ ] Approval is implemented as a comment (`/approve`), not GitHub required-reviewers/branch protection
- [ ] Approval workflow independently verifies: commenter is in `AUTHORIZED_APPROVERS`, PR targets `main`, PR is `ci-verified`, HEAD SHA matches the verified commit
- [ ] Deploy step cannot execute via any path that bypasses the approval workflow (check for stray `on: push: branches: [main]` deploy triggers elsewhere in the repo)

## Locked decision compliance
- [ ] Integration tests asserting monetary fields check `str` type, not numeric
- [ ] No destructive migration or `DROP DATABASE` anywhere in the test-reset path — must be truncate-only
- [ ] `admin_audit` logging untouched by this change (out of scope — confirm it wasn't incidentally modified)

## Placeholder / honesty check
- [ ] The `Deploy to production` step is either a confirmed real mechanism or explicitly still a flagged placeholder — reject if it was silently filled in with a guessed deploy script
- [ ] `backend/tests/e2e/` existence was confirmed, not assumed

## Sign-off

If all boxes check: post `HO-028` confirming governance pass, tag both architects for final merge decision (per Handoff Rules — architect consensus still required even after governance passes; Hermes approval is necessary, not sufficient).

If any box fails: post `HO-028` itemizing the failure(s) by checklist line number, return to `opencode-go/deepseek-v4-flash`, do not merge.

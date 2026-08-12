# HO-027 — Option A: GitHub PR Checks + Comment-Gated Deploy Approval

**From:** DeepSeek Pro / Claude Web (Architects)
**To:** `opencode-go/deepseek-v4-flash` (Backend & Infrastructure Builder)
**Reviewed by (governance, pre-merge):** Hermes (OpenCode Zen)
**Routing zone:** Zone 1 — Implementation
**Status:** Ready for build. Gherkin RED phase not required for CI scaffolding itself — this workflow implements the branch flow already approved in `Master_context_Claude_web_2.txt`.

---

## 1. Objective

Implement automated PR checks for the `test` branch and an approval-gated deploy pipeline for `main`, per the CI/CD branch flow already defined in master context:

```text
test → static analysis → tests → build → deploy → e2e
main → static analysis → tests → build → approval → deploy → e2e
```

The `approval` step on `main` is a **manual `/approve` PR comment from an authorized human** — not GitHub branch protection, not automatic.

---

## 2. Non-negotiable constraints (from master context — violating any of these blocks Hermes governance sign-off)

| Constraint | Source |
|---|---|
| No new PostgreSQL instances — reuse the existing instance via a dedicated `epm_test` database | Infrastructure → Database |
| Python never runs in system Python — must run inside a container | Infrastructure → Python |
| All execution happens on GitHub Actions / VPS — this means a **self-hosted runner on the VPS**, not GitHub-hosted runners | Execution Rules → Execution Path |
| No direct merge to main; review required every cycle | Handoff Rules → Reviews |
| Deploy job on `main` MUST be gated on the `/approve` comment check | CI/CD → Approval Mechanism |
| Monetary API values are strings — assert this in integration tests, don't silently accept numeric | Locked architectural decisions (memory) |

---

## 3. Prerequisites (verify before writing workflow YAML — do not assume)

1. Self-hosted runner registered on VPS with labels `[self-hosted, epm]`. If not already registered:
   ```bash
   mkdir -p ~/actions-runner && cd ~/actions-runner
   curl -o actions-runner-linux-x64.tar.gz -L \
     https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-linux-x64-2.319.1.tar.gz
   tar xzf actions-runner-linux-x64.tar.gz
   ./config.sh --url https://github.com/<org>/<repo> --token <REGISTRATION_TOKEN> \
     --labels vps,epm --name epm-vps-runner --unattended
   sudo ./svc.sh install && sudo ./svc.sh start
   sudo usermod -aG docker $(whoami)
   ```
2. Confirm `epm_test` database exists on the existing PostgreSQL 15 instance:
   ```bash
   docker exec -it <existing-postgres-container> psql -U postgres -c "\l" | grep epm_test
   ```
   If missing:
   ```sql
   CREATE DATABASE epm_test OWNER epm_app;
   ```
3. Confirm `app/scripts/reset_test_schema.py` exists in the backend codebase (truncates, never drops). If it doesn't exist, write it as part of this handoff — do not fabricate the assumption that it's there.
4. Add repo secret `EPM_TEST_DB_PASSWORD`.
5. Add repo variable `AUTHORIZED_APPROVERS` (comma-separated GitHub usernames permitted to `/approve` deploys to main — minimum: `zubbyik`).

---

## 4. Deliverable 1 — `docker-compose.ci.yml`

```yaml
# docker-compose.ci.yml
# CI-only compose file. Reuses the existing PostgreSQL 15 instance on
# openagile_network — does NOT define a postgres service. This is
# intentional: master context forbids additional Postgres instances,
# even ephemeral ones scoped to a CI job.
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    networks:
      - openagile_network
    environment:
      - DATABASE_URL=${DATABASE_URL}
    # No ports exposed — CI talks to this container via `docker compose run`,
    # not over the network from outside.

networks:
  openagile_network:
    external: true
```

---

## 5. Deliverable 2 — `.github/workflows/pr-checks-test.yml`

```yaml
name: PR Checks (test branch)

on:
  pull_request:
    branches: [test]

concurrency:
  group: pr-checks-test-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  static-analysis:
    runs-on: [self-hosted, epm]
    steps:
      - uses: actions/checkout@v4
      - name: Ensure openagile_network exists
        run: docker network inspect openagile_network >/dev/null 2>&1 || docker network create openagile_network
      - name: Ruff (lint)
        run: docker compose -f docker-compose.ci.yml run --rm backend ruff check .
      - name: Mypy (type check)
        run: docker compose -f docker-compose.ci.yml run --rm backend mypy app/

  tests:
    needs: static-analysis
    runs-on: [self-hosted, epm]
    env:
      DATABASE_URL: postgresql://epm_app:${{ secrets.EPM_TEST_DB_PASSWORD }}@postgres:5432/epm_test
    steps:
      - uses: actions/checkout@v4

      - name: Reset test schema (truncate, never drop)
        run: docker compose -f docker-compose.ci.yml run --rm backend python -m app.scripts.reset_test_schema

      - name: Run migrations (additive-only)
        run: docker compose -f docker-compose.ci.yml run --rm backend alembic upgrade head

      - name: Run pytest with JSON + JUnit report
        run: |
          docker compose -f docker-compose.ci.yml run --rm backend \
            pytest backend/tests/ \
              --json-report --json-report-file=/tmp/report.json \
              --junitxml=/tmp/junit.xml
        continue-on-error: true  # capture, don't hard-stop before posting the PR comment

      - name: Copy report out of container
        run: |
          CID=$(docker compose -f docker-compose.ci.yml ps -q backend)
          docker cp "$CID":/tmp/report.json ./report.json || echo '{"summary":{"passed":0,"failed":1,"total":1}}' > report.json

      - name: Post results as PR comment
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          PASSED=$(jq '.summary.passed' report.json)
          FAILED=$(jq '.summary.failed' report.json)
          TOTAL=$(jq '.summary.total' report.json)
          STATUS=$([ "$FAILED" -gt 0 ] && echo "❌ **$FAILED failing** / $TOTAL total" || echo "✅ **All $TOTAL passing**")
          FAILING_LIST=$(jq -r '.tests[]? | select(.outcome=="failed") | "- `\(.nodeid)`"' report.json)
          gh pr comment "${{ github.event.pull_request.number }}" --body "$(cat <<EOF
          ## Test Results — $STATUS

          | Passed | Failed | Total |
          |---|---|---|
          | $PASSED | $FAILED | $TOTAL |

          $([ "$FAILED" -gt 0 ] && echo "**Failing tests:**" && echo "$FAILING_LIST")

          <sub>Run: [\`${{ github.run_id }}\`](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})</sub>
          EOF
          )"

      - name: Fail job if tests failed
        run: |
          FAILED=$(jq '.summary.failed' report.json)
          [ "$FAILED" -eq 0 ]

  build:
    needs: tests
    runs-on: [self-hosted, epm]
    steps:
      - uses: actions/checkout@v4
      - name: Build backend image (PR check only, no push)
        run: docker build -t epm-backend:pr-${{ github.event.pull_request.number }} ./backend
      - name: Build frontend image (PR check only, no push)
        run: docker build -t epm-frontend:pr-${{ github.event.pull_request.number }} ./frontend
```

---

## 6. Deliverable 3 — `.github/workflows/main-verify.yml`

Runs static analysis, tests, and build on PRs targeting `main`. On success, posts the approval prompt instead of deploying.

```yaml
name: Main Verify (pre-approval)

on:
  pull_request:
    branches: [main]

concurrency:
  group: main-verify-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  static-analysis:
    runs-on: [self-hosted, epm]
    steps:
      - uses: actions/checkout@v4
      - run: docker network inspect openagile_network >/dev/null 2>&1 || docker network create openagile_network
      - run: docker compose -f docker-compose.ci.yml run --rm backend ruff check .
      - run: docker compose -f docker-compose.ci.yml run --rm backend mypy app/

  tests:
    needs: static-analysis
    runs-on: [self-hosted, epm]
    env:
      DATABASE_URL: postgresql://epm_app:${{ secrets.EPM_TEST_DB_PASSWORD }}@postgres:5432/epm_test
    steps:
      - uses: actions/checkout@v4
      - run: docker compose -f docker-compose.ci.yml run --rm backend python -m app.scripts.reset_test_schema
      - run: docker compose -f docker-compose.ci.yml run --rm backend alembic upgrade head
      - run: docker compose -f docker-compose.ci.yml run --rm backend pytest backend/tests/ --json-report --json-report-file=/tmp/report.json
      - run: |
          CID=$(docker compose -f docker-compose.ci.yml ps -q backend)
          docker cp "$CID":/tmp/report.json ./report.json
          [ "$(jq '.summary.failed' report.json)" -eq 0 ]

  build:
    needs: tests
    runs-on: [self-hosted, epm]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t epm-backend:pr-${{ github.event.pull_request.number }} ./backend
      - run: docker build -t epm-frontend:pr-${{ github.event.pull_request.number }} ./frontend

  request-approval:
    needs: build
    runs-on: [self-hosted, epm]
    steps:
      - name: Post approval prompt
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh pr comment "${{ github.event.pull_request.number }}" --body \
            "✅ Static analysis, tests, and build all passed at \`${{ github.sha }}\`.

          **Awaiting human approval to deploy to production.**
          An authorized reviewer must comment \`/approve\` on this PR to trigger deploy + e2e."
      - name: Label PR as verified
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh pr edit "${{ github.event.pull_request.number }}" --add-label "ci-verified"
```

**Why a label (`ci-verified`) in addition to the comment:** the approval-gate workflow (next deliverable) is triggered by a *comment* event, which has no inherent knowledge of whether the underlying commit actually passed CI. The label is the durable, checkable signal that `main-verify` succeeded for the current HEAD SHA — the approval workflow checks it before trusting the comment.

---

## 7. Deliverable 4 — `.github/workflows/main-approve-deploy.yml`

The actual approval gate. Triggered by the `/approve` comment, independently verifies authorization and CI status before running deploy + e2e.

```yaml
name: Main Approve & Deploy

on:
  issue_comment:
    types: [created]

jobs:
  approve-and-deploy:
    # Only fire for PR comments (issue_comment fires on issues too) containing /approve
    if: >
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/approve')
    runs-on: [self-hosted, epm]
    env:
      GH_TOKEN: ${{ github.token }}
      PR_NUMBER: ${{ github.event.issue.number }}
      COMMENTER: ${{ github.event.comment.user.login }}
    steps:
      - name: Verify commenter is authorized
        run: |
          # AUTHORIZED_APPROVERS is a repo variable, comma-separated usernames.
          # Kept as a repo variable (not hardcoded here) so the allowlist can
          # change without touching workflow YAML.
          IFS=',' read -ra APPROVERS <<< "${{ vars.AUTHORIZED_APPROVERS }}"
          AUTHORIZED=false
          for u in "${APPROVERS[@]}"; do
            [ "$u" = "$COMMENTER" ] && AUTHORIZED=true
          done
          if [ "$AUTHORIZED" != "true" ]; then
            echo "❌ $COMMENTER is not in AUTHORIZED_APPROVERS — refusing to deploy"
            gh pr comment "$PR_NUMBER" --body "⚠️ @$COMMENTER is not authorized to approve deploys to main."
            exit 1
          fi

      - name: Verify PR targets main and is ci-verified
        run: |
          BASE=$(gh pr view "$PR_NUMBER" --json baseRefName -q .baseRefName)
          LABELS=$(gh pr view "$PR_NUMBER" --json labels -q '.labels[].name')
          if [ "$BASE" != "main" ]; then
            echo "❌ PR does not target main"; exit 1
          fi
          if ! echo "$LABELS" | grep -q "ci-verified"; then
            gh pr comment "$PR_NUMBER" --body "⚠️ @$COMMENTER — this PR is not \`ci-verified\`. Static analysis/tests/build must pass before approval is valid. Re-run main-verify or push a new commit."
            exit 1
          fi

      - name: Verify HEAD SHA has not moved since verification
        run: |
          # Prevent a stale /approve on an old comment from deploying a newer,
          # unverified commit if someone pushed after the ci-verified label was set.
          CURRENT_SHA=$(gh pr view "$PR_NUMBER" --json headRefOid -q .headRefOid)
          LATEST_CHECK_SHA=$(gh api "repos/${{ github.repository }}/commits/$CURRENT_SHA/check-runs" \
            --jq '[.check_runs[] | select(.name=="build") | select(.conclusion=="success")] | length')
          if [ "$LATEST_CHECK_SHA" -lt 1 ]; then
            gh pr comment "$PR_NUMBER" --body "⚠️ @$COMMENTER — no successful build check-run found for the current HEAD (\`$CURRENT_SHA\`). Refusing to deploy a commit that wasn't verified."
            exit 1
          fi

      - uses: actions/checkout@v4

      - name: Deploy to production
        run: |
          # Actual deploy mechanism — placeholder pending confirmation of
          # existing deploy script/process (docker compose pull+up on VPS,
          # or a dedicated deploy.sh). DO NOT treat this step as final —
          # flag back to architects if a deploy script doesn't already exist.
          echo "Deploy step — replace with confirmed deploy mechanism"

      - name: Run e2e suite
        run: |
          docker compose -f docker-compose.ci.yml run --rm backend pytest backend/tests/e2e/

      - name: Post deploy confirmation
        run: |
          gh pr comment "$PR_NUMBER" --body "🚀 Approved by @$COMMENTER and deployed at \`$(date -u +%FT%TZ)\`."
```

**Why three separate verification steps before deploy runs:** a comment-based gate is inherently weaker than GitHub's native required-reviewers UI — anyone with comment permissions can *write* `/approve`, so the workflow has to do the authorization, CI-status, and staleness checks that branch protection would otherwise give for free. Skipping any one of these silently reopens the "no direct merge to main without review" rule.

---

## 8. What builder must confirm before this is mergeable (do not guess these)

1. Does `backend/tests/e2e/` exist? If not, this handoff includes scaffolding it as a separate, explicit task — don't fabricate a passing e2e suite.
2. What is the actual production deploy mechanism? The `Deploy to production` step above is a placeholder — flag back to architects rather than inventing one.
3. Confirm `AUTHORIZED_APPROVERS` repo variable is set before this workflow goes live — until then, `/approve` will always fail closed (safe default, not a bug).

## 9. Definition of done

- [ ] Self-hosted runner confirmed live on VPS with `[self-hosted, epm]` labels
- [ ] `epm_test` database confirmed to exist on the existing Postgres instance
- [ ] `docker-compose.ci.yml` added
- [ ] `pr-checks-test.yml`, `main-verify.yml`, `main-approve-deploy.yml` added
- [ ] `EPM_TEST_DB_PASSWORD` secret and `AUTHORIZED_APPROVERS` variable set
- [ ] Dry run on a throwaway PR to `test`, confirm PR comment posts correctly
- [ ] Dry run on a throwaway PR to `main`, confirm `ci-verified` label + approval prompt post correctly
- [ ] Confirm `/approve` from a non-authorized user is correctly rejected before testing the authorized path
- [ ] Submit `HO-028` back to Hermes for governance review

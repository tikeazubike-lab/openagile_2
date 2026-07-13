# HO-[ASSIGN NEXT SEQUENTIAL NUMBER] — GitHub Actions PR Checks (Option A)

**From:** DeepSeek (Architect/Zone 2)
**To:** `[hermes]Deepseek:flash` (Backend & Infrastructure Builder / Zone 1)
**Zone:** Zone 1 — Implementation
**Status:** Ready for execution
**Governing document:** `Master_context_Claude_web.txt` — this file is authoritative. If anything below conflicts with it, the master context wins and you must flag the conflict back to DeepSeek before proceeding, not silently resolve it.

---

## 1. Objective

Add a GitHub Actions workflow that runs static analysis, tests, and a build check on every PR targeting the `test` branch, using a **self-hosted runner on the existing VPS**, reusing the **existing PostgreSQL 15 instance** (new `epm_test` database inside it, not a new instance), and posting results as a PR comment. Human approval before merge to `main` is enforced via **GitHub native branch protection** (required reviewer) — you are configuring that setting, not building a custom approval-gate step in the workflow.

This is a CI/CD and VPS-operations task. It does not require a Gherkin RED phase — the design is pre-approved (branch flow already defined in master context; Option A design approved by Zubbyik in prior session).

---

## 2. Non-negotiable constraints (from `Master_context_Claude_web.txt`)

Do not re-derive these — apply them:

- **Never create an additional Postgres instance.** Reuse the existing instance. `epm_test` is a database *inside* it.
- **Never install into system Python.** `pytest` runs inside the backend container, not on the bare runner.
- **SSH heredocs must be quoted** (`<<'EOF'`) — never unquoted.
- **No direct merge to `main`.** Review required every cycle — this is what branch protection is enforcing.
- **All builds/tests/deploys go through GitHub Actions → VPS.** Nothing runs on Zubbyik's local Fedora workstation, and you should not instruct him to run anything there either.
- **Structured, numbered, status-aware artifacts only.** Your completion report back is an `HO-*.md`, not a chat summary.

---

## 3. Task sequence

Execute in order. Do not skip discovery — several downstream steps depend on what you find.

### 3.1 Discovery (do this first, before writing anything)

Check and report findings for:

1. Does `docker-compose.ci.yml` (or any CI-specific compose override) already exist in the repo? Search the repo, not just the root.
2. What does the existing `docker-compose.yml` backend service look like — image build context, env vars, network name, volume mounts? Your CI compose file must mirror this, pointed at `epm_test` instead of the prod/staging DB.
3. Confirm the exact name and access details of the running Postgres 15 container (container name, network it's attached to — should be `openagile_network` per master context).
4. Confirm whether `pytest-json-report` is already a dependency in `backend/requirements*.txt` or equivalent. If not, add it.
5. Confirm whether a test-schema-reset script (something like `app.scripts.reset_test_schema`) exists. If not, you need to write a minimal one — truncate tables, **never** `DROP DATABASE`, consistent with the soft-delete/no-destructive-ops posture in the master context.
6. Confirm current GitHub Actions state — repo should currently have **zero workflows**. If you find existing ones, stop and report back before proceeding (scope mismatch with what was briefed to Zubbyik).

Report discovery results in your completion HO doc even if everything matches assumptions — this is what "status-aware" means in practice.

### 3.2 Register the self-hosted runner on the VPS

```bash
ssh <user>@<vps-host> <<'EOF'
mkdir -p ~/actions-runner && cd ~/actions-runner

curl -o actions-runner-linux-x64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-linux-x64-2.319.1.tar.gz
tar xzf actions-runner-linux-x64.tar.gz

./config.sh --url https://github.com/<org>/<repo> --token <REGISTRATION_TOKEN> \
  --labels vps,epm --name epm-vps-runner --unattended

sudo ./svc.sh install
sudo ./svc.sh start
EOF
```

Notes for you:

- Get `<REGISTRATION_TOKEN>` from repo → Settings → Actions → Runners → New self-hosted runner. This token is short-lived — generate it fresh at execution time, do not hardcode an old one.
- Use labels `vps,epm`, not bare `self-hosted`. The workflow pins to `[self-hosted, epm]` specifically so any future unrelated self-hosted runner doesn't accidentally pick up EPM jobs it lacks network access for.
- The runner's service account needs Docker group membership:
  ```bash
  sudo usermod -aG docker $(whoami)
  ```
  Verify with `docker ps` as that user post-setup — don't assume the group change took effect without a fresh login/session.
- Confirm the runner shows **Idle** in GitHub's Settings → Actions → Runners UI before moving on.

### 3.3 Create/verify `docker-compose.ci.yml`

If discovery (3.1.1) found no existing file, create one. It must:

- Reuse the same backend image build context as the main compose file (don't diverge the Dockerfile).
- Set `DATABASE_URL` to point at `epm_test` on the existing Postgres container, over `openagile_network`.
- Not define a `postgres` service block — you are connecting to the existing instance, not standing up a new one. This is the constraint from 3.1.3, restated because it's the single easiest thing to get wrong by copying a generic GitHub Actions Postgres tutorial.

### 3.4 Create the `epm_test` database (one-time)

```bash
ssh <user>@<vps-host> <<'EOF'
docker exec -it <existing-postgres-container> psql -U postgres -c \
  "CREATE DATABASE epm_test OWNER epm_app;"
EOF
```

Confirm `epm_app` already exists as a role with appropriate privileges before running this — if it doesn't, report back rather than creating a new role unilaterally (role/privilege decisions are a DeepSeek call).

### 3.5 Add the `EPM_TEST_DB_PASSWORD` secret

Set via `gh secret set` (never echo the value in logs or commit it anywhere):

```bash
gh secret set EPM_TEST_DB_PASSWORD --repo <org>/<repo>
# paste value at prompt
```

### 3.6 Write `.github/workflows/test-pr.yml`

Jobs, in order: `static-analysis` → `tests` → `build`. Key requirements:

- Trigger: `pull_request: branches: [test]`.
- `runs-on: [self-hosted, epm]` for every job.
- `concurrency` group keyed on PR number with `cancel-in-progress: true`, so rapid pushes don't queue stale runs.
- `pytest` executes via `docker compose -f docker-compose.ci.yml run --rm backend pytest ...` — inside the container, never on the runner host directly.
- Use `--json-report` and `continue-on-error: true` on the pytest step specifically, followed by a separate "fail job if tests failed" step. This ordering matters: if pytest's non-zero exit stops the job immediately, the PR comment step never runs and Zubbyik gets a bare red X with no detail. Report → then fail, not fail → then (skipped) report.
- Post results as a `gh pr comment` with a pass/fail table and a list of failing test node IDs.
- Copy the JSON report out of the container via `docker cp`, not a bind mount — don't couple the workflow to the backend Dockerfile's internal working-directory layout.

Full reference structure was already reviewed with Zubbyik in the design discussion — implement to that shape; deviate only where discovery (3.1) surfaces a real conflict, and note any deviation explicitly in your completion HO.

### 3.7 Configure branch protection on `main`

Native branch protection, not a workflow-level gate. Via `gh api` (preferred, scriptable) or documented manual steps if the API path hits permission issues:

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/<org>/<repo>/branches/main/protection \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f enforce_admins=true \
  -f required_status_checks.strict=true \
  -f 'required_status_checks.contexts[]=tests' \
  -f 'required_status_checks.contexts[]=static-analysis' \
  -f 'required_status_checks.contexts[]=build' \
  -f restrictions=null
```

Verify by attempting (in a scratch PR, not a real one) that merge is blocked pre-approval. Report the actual settings screen state (via `gh api /repos/<org>/<repo>/branches/main/protection`) in your completion doc as evidence — don't just assert it's configured.

### 3.8 Verification

Open a throwaway test PR against `test` (e.g. a whitespace change) to confirm:

- Runner picks up the job (check Actions tab, not just assume).
- `static-analysis` → `tests` → `build` run in the correct order and the `tests` job correctly connects to `epm_test`, not any other database.
- PR comment appears with correct pass/fail counts.
- Intentionally break one test locally in the throwaway branch first, confirm the workflow reports the failure correctly and still posts a comment (this validates the `continue-on-error` ordering from 3.6), then fix it and confirm a clean pass.

Close/delete the throwaway PR and branch after verification — don't leave it open.

---

## 4. Deliverables checklist

Report against this list explicitly in your completion HO — don't summarize, enumerate:

- [ ] Discovery findings (3.1), including any deviations from assumptions
- [ ] Self-hosted runner registered, `docker` group confirmed, shown Idle in GitHub UI
- [ ] `docker-compose.ci.yml` created or verified (state which)
- [ ] `epm_test` database created, owned by `epm_app`
- [ ] `EPM_TEST_DB_PASSWORD` secret set
- [ ] `.github/workflows/test-pr.yml` committed
- [ ] Branch protection on `main` configured and verified (paste the actual `gh api` GET response as evidence)
- [ ] Verification PR run — link to the Actions run and the PR comment it produced
- [ ] Verification PR closed/deleted

## 5. Open items to report back to DeepSeek (do not resolve unilaterally)

1. Anything found in discovery (3.1) that contradicts assumptions in this doc.
2. Whether `epm_app` role/privileges needed any change to support `epm_test`.
3. Any required status check name mismatch between what's in the workflow (`tests`, `static-analysis`, `build`) and what actually shows up in GitHub's branch protection UI — job names sometimes don't map 1:1 to what GitHub exposes as a check context, and this needs to be confirmed against the real repo, not assumed from the YAML.

---

**Handoff rule reminder for yourself:** this is infra/CI implementation with pre-approved design — proceed directly. Do not wait for further DeepSeek sign-off before starting 3.1–3.5. Do pause and report back before 3.7 (branch protection) if discovery in 3.1 surfaces anything materially different from what's assumed here, since that changes what "required status checks" should list.

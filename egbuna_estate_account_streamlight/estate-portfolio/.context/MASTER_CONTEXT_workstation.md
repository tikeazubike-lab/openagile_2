# MASTER_CONTEXT_workstation.md — Fedora Laptop / CI/CD Workflow

**Inherits**: All rules from `.context/MASTER_CONTEXT.md` unless explicitly overridden below.
**Applies when**: Agent session runs on or through the Fedora workstation (local laptop).
**Detection**: Host is `fedora`, OS is `Fedora Linux 42`, or the agent is told "workstation mode" or "CI/CD mode."

> **Session start rule**: If an agent is unsure which context to load, it must ask:
> "Are we on the **Server** (VPS direct deploy) or **Workstation** (CI/CD pipeline)?"

---

## Override: Execution Rules

| Rule | MASTER_CONTEXT.md (default) | MASTER_CONTEXT_workstation.md (override) |
|------|----------------------------|------------------------------------------|
| Docker commands | NEVER locally | STRICTLY NEVER — this is the Fedora workstation |
| `docker compose build` | GitHub Actions only | STRICTLY GitHub Actions only |
| `docker compose up -d` | GitHub Actions only | STRICTLY GitHub Actions only |
| `npm install` | NEVER locally | STRICTLY NEVER |
| `npm run build` | NEVER locally | STRICTLY NEVER |
| `python3` / `pytest` | NEVER locally | STRICTLY NEVER |
| SSH to server | For verification only | ✅ YES — for verification only | 
| Git operations | Allowed | ✅ Allowed — this is the ONLY execution on workstation |

**Enforcement**: The Fedora workstation has a known kernel OOM failure on Python/Node loads. This is a hard hardware constraint, not a preference. Agents must NEVER suggest or execute:
- `pip install`, `python3`, `pytest`, `node`, `npm`, `docker`, `docker compose`, `curl` to production endpoints
- Any command that could allocate significant RAM/CPU

---

## Override: Deployment Path

```
git push origin <branch>
       │
       ▼
GitHub Actions fires ci.yml
       │
       ├── FAST PATH (feature/**, develop):
       │     Stage 0: Static analysis
       │     Stage 3: Build Docker image
       │     Stage 4: Deploy to demo.estate.zubbystudio.shop
       │     → Check staging URL in browser. Done.
       │
       └── FULL PATH (main, test, workflow_dispatch):
             All stages → blocks production if any fails
```

**Fast deploy** (feature/**, develop branches):
- Push → Actions builds → deploys to `demo.estate.zubbystudio.shop`
- Verify in browser, no local execution needed

**Production deploy** (main branch only):
- Push to `develop` → fast path to demo → verify
- Create PR to `main` → full CI runs → `/approve` gate → deploy to production
- NEVER direct push to main from workstation

---

## Override: Branch Strategy

```
feature/xyz → develop → test → main
    ↑             ↑        ↑      ↑
  Edit here    Fast CI   Full   Manual
  locally      path      CI +   approval
                         Codex  + prod
                         tests  deploy
```

### PR / Merge Rules
- PR required for every merge to `main`
- `/approve` comment required on main PR before deploy job runs
- Review by DeepSeek Pro or Claude Web (architects)
- Hermes governance check required before merge
- Tests must pass in CI before deploy

---

## GitHub Actions Secrets (Workstation Mode)

```
VPS_HOST          — 185.216.177.250
VPS_USER          — zubbyik
VPS_SSH_KEY       — Private SSH key
JWT_SECRET        — EPM JWT signing secret
DB_HOST           — openagile_postgres
DB_NAME           — estate_portfolio
DB_USER           — openagile
DB_PASSWORD       — shared Postgres password
DB_PORT           — 5432
DB_TEST_SCHEMA    — estate_portfolio_test
ADMIN_USERNAME    — EPM admin username
ADMIN_PASSWORD    — EPM admin password (bcrypt hashed)
E2E_ADMIN_USER    — Playwright test admin username
E2E_ADMIN_PASS    — Playwright test admin password
E2E_VIEWER_USER   — Playwright readonly username
E2E_VIEWER_PASS   — Playwright readonly password
SNYK_TOKEN        — Snyk security scan token
VAULT_REPO_DEPLOY_KEY — SSH key for VPS to pull private vault repo
```

---

## Override: Anti-Patterns (Enforced in Workstation Mode)

```
❌ "Run this on your machine: docker compose up -d"
❌ "Run this on your machine: pip install -r requirements.txt"
❌ "Run this on your machine: npm install"
❌ "Run this on your machine: pytest"
❌ "SSH into the server and run: docker compose restart"
❌ "Copy files to server with scp"
❌ "Use << ENDSSH (unquoted) in GitHub Actions"
❌ "Run python3 locally to test something quickly"

✅ "Commit this change and push to develop — Actions will deploy to staging"
✅ "Push to test branch — Codex will run the full suite on the server"
✅ "Trigger workflow_dispatch from GitHub UI for immediate full pipeline run"
✅ "SSH to VPS to verify if needed: ssh zubbyik@185.216.177.250"
```

---

## Agent Routing (Workstation Mode)

```yaml
Routing for Fedora-based sessions:
  - Antigravity (Gemini Pro CLI): File ops, multi-file edits, code review
  - Claude Web: Architecture, design, documentation, STLC
  - Cursor (Antigravity/GPT): Code editing
  - Grok: Up-to-date info, version verification
  - Codex: Test execution on VPS (SSH via GitHub Actions)
  - Lovable: React UI generation

  Hermes (governance): Runs on OpenCode Zen — review only, no implementation
```

---

**END OF MASTER_CONTEXT_workstation.md**

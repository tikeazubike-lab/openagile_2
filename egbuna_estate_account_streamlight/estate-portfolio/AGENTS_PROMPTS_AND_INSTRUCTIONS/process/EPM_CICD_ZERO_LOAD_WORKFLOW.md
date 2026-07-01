# EPM — Zero-Load Local CI/CD Workflow
## Brainstorm & Design Document

**From**: Claude (The Brain)
**Date**: 2026-04-25
**Protocol**: MASTER_CONTEXT.md v3.0
**Constraint**: Fedora workstation must do as little as possible.
**Goal**: Write code locally → everything else (test, build, deploy) runs on Netcup VPS or GitHub Actions.

---

## The Core Principle

```
Your workstation does exactly THREE things:
  1. Edit code (Neovim / Cursor / Antigravity)
  2. git commit
  3. git push

Everything else — installing packages, running tests, building Docker
images, deploying containers — happens on GitHub Actions (cloud runners)
or directly on the Netcup VPS. Your laptop never runs Python or Node.
```

---

## The Full Workflow Map

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL WORKSTATION (Fedora)                                  │
│  RAM/CPU: protected. Only these operations allowed:          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Edit code    │    │ git commit   │    │ git push      │  │
│  │ (Neovim /   │───▶│ (zero CPU)   │───▶│ (network only)│  │
│  │  Cursor /   │    └──────────────┘    └───────┬───────┘  │
│  │  Antigravity│                                │           │
│  └──────────────┘                               │           │
│                                                 │           │
│  OBSIDIAN VAULT (separate, lightweight):        │           │
│  git commit vault changes → git push            │           │
│  (markdown files only — no Python, no Node)     │           │
└─────────────────────────────────────────────────┼───────────┘
                                                  │
                                          GitHub receives push
                                                  │
                    ┌─────────────────────────────▼──────────────────────────┐
                    │  GITHUB ACTIONS (cloud runners — zero local resources)  │
                    │                                                          │
                    │  Stage 0: Static analysis (ruff, eslint, actionlint)    │
                    │  Stage 1: Unit tests (pytest + vitest)                  │
                    │  Stage 2: Integration tests → shared Postgres via VPS   │
                    │  Stage 3: Build Docker image (React + FastAPI)           │
                    │  Stage 4: Deploy to demo.estate.zubbystudio.shop        │
                    │  Stage 5: E2E + Playwright + Locust (against staging)   │
                    └─────────────────────────────┬──────────────────────────┘
                                                  │
                                    ┌─────────────▼──────────────┐
                                    │  NETCUP VPS (Ubuntu 24.04)  │
                                    │                              │
                                    │  - Runs Docker containers    │
                                    │  - Shared openagile_postgres │
                                    │  - Traefik SSL routing       │
                                    │  - Playwright E2E target     │
                                    │  - Obsidian vault sync target│
                                    └──────────────────────────────┘
```

---

## Part A: Code CI/CD — The Lightweight Push Workflow

### A.1 What you do locally

```bash
# That's it. Three commands. No npm, no pip, no docker.
git add .
git commit -m "feat: add claim records table"
git push origin develop
```

### A.2 What happens automatically (zero local involvement)

```
Push to develop → GitHub Actions fires:
  ├── Stage 0: ruff + eslint + actionlint (< 2 min, cloud runner)
  ├── Stage 1: pytest unit + vitest unit (< 5 min, cloud runner)
  ├── Stage 2: integration tests against shared Postgres (< 10 min)
  ├── Stage 3: npm build + docker build (< 8 min, cloud runner)
  ├── Stage 4: SSH deploy to demo.estate.zubbystudio.shop
  └── Stage 5: Playwright E2E against staging (< 15 min)

You get a GitHub notification (email/mobile) when it passes or fails.
You read the logs in your browser — no local terminal needed.
```

### A.3 Branch strategy (resource-aware)

```
feature/xyz  →  develop  →  test  →  main
    ↑               ↑           ↑       ↑
  You work        Full CI    Codex   Manual
  here only       runs       tests   approval
                  on push           + deploy
                                    to prod
```

**Key rule**: You never run CI locally. If you want to check something before pushing, that's what the `test` branch is for — Codex runs things there on the server.

---

## Part B: Obsidian Vault Sync — Git-Based, Minimal Local Work

### B.1 The Setup (one-time)

```bash
# On your local workstation — one time only:
cd ~/ObsidianVault/NigerianStocks
git init
git remote add origin git@github.com:zubbyik/obsidian-nigerian-stocks-private.git
# Private repo — markdown files only, no code, no packages
```

### B.2 When you update the vault (your only local action)

```bash
# After editing any .md file in Obsidian:
cd ~/ObsidianVault/NigerianStocks
git add .
git commit -m "update: DANGCEM dividend Q1 2026"
git push origin main
# Done. Workstation work is finished.
```

**Resource cost**: `git add` + `git commit` + `git push` on markdown files.
This uses ~10MB RAM. Your kernel will not notice.

### B.3 What happens on the server (automatic)

```
Vault push to GitHub → GitHub Actions webhook fires → VPS pulls vault repo
→ import_obsidian.py runs ON THE VPS (not your workstation)
→ PostgreSQL updated
→ You see result in EPM web app
```

The import script runs entirely on the Netcup VPS where there is 16GB RAM and 8 vCPUs. Your workstation never touches Python.

### B.4 The Vault Sync GitHub Actions Workflow

```yaml
# .github/workflows/vault-sync.yml
# Lives in the PRIVATE VAULT REPO (not the EPM repo)

name: Sync Obsidian Vault to EPM PostgreSQL

on:
  push:
    branches: [main]
    paths:
      - 'Companies/**'
      - 'Dividends/**'
  workflow_dispatch:   # manual trigger from GitHub UI

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: SSH to VPS and run import script
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /root/openagile/egbuna_estate_account_streamlight/estate-portfolio
            
            # Pull the latest vault markdown files onto the VPS
            git -C ~/ObsidianVaultMirror pull origin main || \
              git clone git@github.com:zubbyik/obsidian-nigerian-stocks-private.git \
                ~/ObsidianVaultMirror
            
            # Run the import script ON THE VPS (not local workstation)
            docker compose exec backend python scripts/import_obsidian.py \
              --vault-path /vault \
              --mode new-only

# The VPS mounts the vault mirror as a Docker volume (see Part C)
```

### B.5 Docker volume for vault on VPS

```yaml
# In docker-compose.yml — add to backend service:
services:
  backend:
    volumes:
      - ~/ObsidianVaultMirror:/vault:ro   # read-only mount
      # import_obsidian.py reads from /vault inside the container
```

---

## Part C: What Changes in Your Local Setup

### C.1 Remove from local workstation (if present)

```bash
# You should NOT have these running locally:
# ❌ docker compose up  (never — MASTER_CONTEXT rule)
# ❌ pip install        (never — crashes your kernel)
# ❌ npm install        (never — RAM intensive)
# ❌ pytest             (never — run on server)
# ❌ python anything    (never — kernel overload risk)
```

### C.2 Your local workstation only needs

```
git          — already installed, near-zero RAM
Neovim       — text editor, negligible RAM
Cursor       — AI editor, uses some RAM but no Python execution
Obsidian     — markdown editor, no code execution
SSH client   — to read server logs if needed (optional)
Web browser  — to check GitHub Actions results and EPM web app
```

### C.3 Antigravity's new role on your workstation

Antigravity (Gemini Pro) runs in Cursor or as a CLI tool. It:
- Reads and edits code files
- Writes git commits
- Does NOT execute Python, Node, or Docker

If Antigravity needs to verify something that requires code execution, it does so via SSH to the VPS — not locally.

---

## Part D: Handling the "I Want to Test Before I Push" Urge

You will sometimes want to quickly verify something before committing. Here are the zero-RAM options:

### Option 1: Push to `test` branch (recommended)

```bash
git push origin feature/xyz:test
# GitHub Actions runs the full suite on the test branch
# You get results in 15 minutes in your GitHub notifications
# Zero local resources used
```

### Option 2: SSH to VPS and run manually (for quick checks)

```bash
ssh zubbyik@185.216.177.250
cd /root/openagile/egbuna_estate_account_streamlight/estate-portfolio
docker compose exec backend pytest tests/unit/test_business_logic.py -v
# Runs on VPS — 16GB RAM, no problem
```

### Option 3: GitHub Actions "workflow_dispatch" (manual trigger)

```
Go to: github.com/zubbyik/repo → Actions → CI Pipeline → Run workflow
Select branch → Run
```

No git push needed. Just click a button in your browser.

---

## Part E: Proposed Lightweight CI Pipeline (Resource-Aware)

The existing `ci.yml` runs sequentially and blocks deploy on every test failure. For your workflow, we introduce a **fast path** and a **full path**:

```
FAST PATH (every push to develop/feature branches):
  Stage 0: Static analysis only (< 2 min)
  Stage 3: Build Docker image
  Stage 4: Deploy to staging
  → Notify you: "Deployed to demo.estate.zubbystudio.shop"

FULL PATH (push to main, or manual trigger, or nightly scheduled run):
  Stage 0 → 1 → 2 → 3 → 4 → 5 (full pyramid)
  → Blocks production deploy on any failure
```

This means your code is always running on staging after every push (fast feedback), but the full test gate only runs when it matters (merge to main, or you explicitly ask for it).

```yaml
# .github/workflows/ci.yml — updated trigger logic

on:
  push:
    branches: [main, develop, test, 'feature/**']
  schedule:
    - cron: '0 2 * * *'   # full suite nightly at 2am WAT
  workflow_dispatch:
    inputs:
      full_suite:
        description: 'Run full test suite?'
        type: boolean
        default: false

jobs:
  # Always runs
  static-analysis: ...
  build: ...
  deploy-staging: ...

  # Only runs on main, test branch, nightly, or manual full_suite=true
  unit-backend:
    if: |
      github.ref == 'refs/heads/main' ||
      github.ref == 'refs/heads/test' ||
      github.event_name == 'schedule' ||
      github.event.inputs.full_suite == 'true'

  unit-frontend:
    if: <same condition>

  integration:
    if: <same condition>

  e2e-tests:
    if: <same condition>
```

---

## Part F: Summary — What Each Agent Does in This New World

| Agent | Where it runs | Local resources used |
|-------|--------------|---------------------|
| **You** | Local workstation | Edit + git push only |
| **Antigravity** | Local (Cursor/Neovim) + SSH to VPS for verification | Code editing only |
| **GitHub Actions** | Cloud runners | Zero local |
| **Codex** | SSH to VPS, `test` branch | Zero local |
| **Lovable** | Lovable.dev cloud | Zero local |
| **Obsidian sync** | VPS (via vault private repo) | Zero local |
| **Tests** | GitHub Actions + VPS Postgres | Zero local |
| **Docker build** | GitHub Actions | Zero local |
| **Deployment** | VPS via GitHub Actions SSH | Zero local |

---

## Part G: One-Time Setup Checklist

These are setup tasks, not ongoing work. Do them once:

```
On local workstation:
[ ] git config is set (name, email, SSH key for GitHub)
[ ] Obsidian vault: git init + remote add to private repo

On GitHub:
[ ] Private vault repo created
[ ] Secrets added: VPS_HOST, VPS_USER, VPS_SSH_KEY
[ ] vault-sync.yml workflow added to vault repo

On Netcup VPS (Antigravity does this via SSH):
[ ] SSH key pair generated on VPS for pulling vault private repo
[ ] VPS public key added to vault private repo deploy keys
[ ] ~/ObsidianVaultMirror directory created
[ ] docker-compose.yml updated with /vault volume mount
```

---

## Part H: What This Solves vs What It Doesn't

### Solved ✅
- No Python, Node, or Docker ever runs on your workstation
- Obsidian vault data reaches PostgreSQL without local execution
- You still get fast feedback (staging deploy after every push)
- Full test suite still gates production merges
- Codex still has a place to test (SSH to VPS, `test` branch)
- CI/CD standard practice maintained (pipeline pyramid, blocking gates)

### Not solved / trade-offs ⚠️
- **Feedback latency**: You won't know if unit tests pass until GitHub Actions finishes (~15 min for full suite). The fast path deploys to staging in ~5 min regardless.
- **Vault sync is not real-time**: You still need to `git push` the vault when you want changes in the web app. But that's one command on markdown files — negligible.
- **First-time Obsidian setup**: The one-time `git init` on the vault requires a small amount of setup work. Not ongoing.

---

**Next step**: Confirm this design, then Antigravity implements:
1. The `vault-sync.yml` workflow in the private vault repo
2. The docker-compose volume mount for `/vault`
3. The updated `ci.yml` fast-path / full-path split
4. The one-time VPS setup (SSH key for vault repo pull)

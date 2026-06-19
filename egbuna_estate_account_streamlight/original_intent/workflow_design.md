# WORKFLOW_DESIGN.md

## Development Workflow
```
Local workstation (Fedora):
  Edit code → git commit → git push
       ↓
GitHub repository (test branch)
       ↓
GitHub Actions CI/CD
  Fast path (feature/*, test branch):
    Stage 0: Static analysis (ruff, eslint)
    Stage 3: Docker build
    Stage 4: Deploy to demo.estate.zubbystudio.shop
  Full path (main, scheduled, workflow_dispatch):
    Stage 0–5: Full pyramid (unit → integration → E2E → perf → security)
       ↓
Netcup VPS (Ubuntu 24.04)
  Docker Compose up → Traefik routes → app live
```

## Branch Strategy
```
feature/xyz → test → main
                ↑        ↑
           All work   Manual approval
           here       + prod deploy
```
- All agent work on test branch
- Only owner merges test → main
- Never commit directly to main

## Agent Handover Workflow
```
Claude (design spec + HO document)
    ↓
Antigravity (backend implementation)
    ↓  [parallel]
Deepseek v4 (frontend implementation)
    ↓
Codex (test execution via SSH to VPS)
    ↓
Acceptance Test (AT-*.md filed in docs/)
    ↓
Claude (review AT results → next HO)
```

## Gherkin BDD Pipeline (Uncle Bob Discipline)
```
Claude writes .feature file (Gherkin Given/When/Then)
    ↓
IR validation (parse + check for ambiguity)
    ↓
Stack detection (FastAPI → pytest, React → vitest)
    ↓
Test generation (standard pytest functions, traceability comments)
    ↓
Antigravity/Deepseek v4 run tests → confirm RED
    ↓
Write production code to pass tests → GREEN
    ↓
Refactor (tests stay green)
```
- No pytest-bdd — standard pytest + httpx
- Traceability via comment above each assertion
- .feature files live in docs/testing/ (spec documents, not runtime)

## Price Update Workflow
```
Daily:
  Download NGX Daily Official List PDF from ngxgroup.com
    ↓
  Upload via /settings/price-entry → POST /api/v1/prices/upload-pdf
    ↓
  Parser extracts CLOSE prices (right-to-left, fuzzy name match)
    ↓
  price_history records inserted (date from PDF filename)
    ↓
  companies.current_price updated
    ↓
  NAV snapshot triggered (if none exists today)
```

## Obsidian Import Workflow
```
Edit Obsidian vault markdown files
    ↓
git commit + git push to private vault repo
    ↓
vault-sync.yml triggers on push
    ↓
VPS SSHes (using existing key) → git pull ~/ObsidianVaultMirror
    ↓
docker compose exec backend python scripts/import_obsidian.py
  --vault-path /vault --mode new-only
    ↓
PostgreSQL updated (INSERT new, never UPDATE existing)
    ↓
obsidian_sync_log row inserted
```

## Three-Layer Manual Testing Protocol
```
[DB]  — PostgreSQL direct via psql
[API] — curl from VPS or DevTools Network tab
[UI]  — browser at demo.estate.zubbystudio.shop
```
- Every acceptance test item labelled with its layer
- Test in order: DB → API → UI
- DB confirms persistence, API confirms contract, UI confirms rendering

## Document Governance Workflow
```
Claude writes spec → saves to docs/ in repo
    ↓
Antigravity mirrors to docs/README.md (Wiki alternative)
    ↓
All agents reference docs/ as source of truth
    ↓
Superseded docs moved to docs/*/archived/ with date suffix
    ↓
Never delete — archive only
```


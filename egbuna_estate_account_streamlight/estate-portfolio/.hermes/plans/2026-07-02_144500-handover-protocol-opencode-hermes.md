# OpenCode Onboarding Brief — EPM v2

> **From:** Hermes (Workflow Governance)  
> **To:** [opencode]DeepSeek Pro, [opencode]DeepSeek Flash, [opencode]Kimi  
> **Date:** 2026-07-02  
> **Authority:** `Master_context_Claude_web_2.txt` — this file is the single source of truth.  
> **Purpose:** One-shot onboarding — everything OpenCode needs to start on EPM v2.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Project** | Estate Portfolio Manager (EPM) v2 |
| **Owner** | Zubbyik (Product Owner) |
| **Stack** | FastAPI + React 18 + PostgreSQL 15 |
| **Domain** | testdrive.epm.zubbystudio.shop (staging) |
| **Goal** | Track personal Nigerian stock portfolio: holdings, dividends, registrars, price history, NAV |

### Three North Star Questions (every feature serves one)
1. **Net Worth** — "What do I own and what is it worth today?"
2. **Administration** — "What paperwork is outstanding?"
3. **Performance** — "Is my portfolio growing over time?"

---

## 2. Agent Roles (from Master_context_Claude_web_2.txt)

| Agent | Role | Domain |
|-------|------|--------|
| **[opencode]DeepSeek Pro** | Architecture Lead & Orchestrator | Design, specs, STLC, Gherkin, RCA, reviews, task decomposition |
| **[opencode]DeepSeek Flash** | **Primary Backend & Infra Implementer** | FastAPI, PostgreSQL, Docker, Traefik, VPS, CI/CD, networking |
| **[opencode]Kimi** | **Frontend & Documentation** | React 18, TypeScript, Tailwind v4, TanStack ecosystem |
| **[opencode]Qwen** | Reasoning Fallback | — |
| **[opencode]Minimax** | General Fallback | — |
| **Hermes** (this session) | **Workflow Governance Only** | Handover validation, status tracking, context checks — **MUST NOT implement** |

### Push Sequence (strict)
```
DeepSeek Pro (design) → DeepSeek Flash (backend + deploy) → Kimi (frontend) → Hermes (verify + report)
```
Never build frontend before backend APIs are stable.

---

## 3. VPS — Connection & Paths

| Detail | Value |
|--------|-------|
| **Host** | 185.216.177.250 |
| **User** | zubbyik |
| **Project root** | `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/` |
| **Staging URL** | `https://testdrive.epm.zubbystudio.shop` |
| **Compose file** | `docker-compose.v3.yml` |
| **Container name** | `epm_v3` |

### Directory Layout (key paths only)

```
estate-portfolio/
├── .context/                          ← Agent memory — read every session
│   ├── AGENT.md                       ← Entry point (read first)
│   ├── project-overview.md
│   ├── architecture.md
│   ├── code-standards.md
│   ├── ai-workflow-rules.md
│   ├── ui-context.md
│   ├── progress-tracker.md
│   ├── current-issues.md              ← Active bugs (GITIGNORED)
│   ├── agents.yaml                    ← Agent-to-model routing
│   ├── AGENT_LOG.md                   ← Shared handoff log (MUST CREATE)
│   └── feature-specs/                 ← F-XXX.md files
├── backend/
│   └── app/
│       ├── main.py                    ← App factory + router registration
│       ├── models.py                  ← ALL SQLAlchemy models (flat file)
│       ├── database.py                ← get_session() async factory
│       ├── deps.py                    ← auth: create_access_token, get_current_user, require_admin
│       ├── routers/                   ← auth, dashboard, holdings, prices, companies, etc.
│       └── services/
├── estate-portfolio-manager/
│   └── src/
│       ├── routes/                    ← TanStack file-based routes
│       ├── api/queries.ts             ← All TanStack Query hooks
│       ├── lib/format.ts              ← fmtNaira, fmtPct (null-safe)
│       ├── store/                     ← authStore, uiStore (Zustand)
│       └── hooks/
├── docs/
│   ├── handovers/                     ← HO-XXX.md
│   ├── handover/                      ← OLD LOCATION (consolidate later)
│   ├── decisions/                     ← EMPTY — needs ADRs
│   ├── requirements/
│   └── testing/
├── docker-compose.v3.yml
├── deploy.sh
└── requirements.txt
```

---

## 4. Must-Read Files (First Session — In Order)

| Order | Path | Why |
|-------|------|-----|
| 1 | `.context/AGENT.md` | Entry point — hard rules, agent split, deployment |
| 2 | `.context/architecture.md` | Stack, invariants, contract rules |
| 3 | `.context/code-standards.md` | Python/TS conventions, commit format |
| 4 | `.context/progress-tracker.md` | Live feature status, priority order |
| 5 | `.context/current-issues.md` | Active bugs (BUG-001–005 — all fixed but unverified) |
| 6 | `.context/feature-specs/*.md` | Assigned feature spec (when starting a feature) |

---

## 5. Hard Rules (from `.context/AGENT.md`) — Never Violate

```
NO production code before RED tests
NO implementation without a feature spec
NO guessing at bug fixes — diagnose first, write analysis, wait for approval
NO datetime.utcnow() — always datetime.now(timezone.utc)
NO get_db — always get_session
NO localStorage for JWT — httpOnly cookie only
NO hardcoded hex colours — always var(--token-name)
NO monetary floats from API — always strings ("12345.50" not 12345.50)
NO bcrypt upgrade above 4.0.1
```

---

## 6. Deployment Procedure

### Backend change
```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
docker compose -f docker-compose.v3.yml up -d --build epm_v3
```

### Frontend change
```bash
cd estate-portfolio-manager
npm run build
cp -r dist/* ../backend/app/static/
docker compose -f docker-compose.v3.yml restart epm_v3
```

### View logs
```bash
docker compose -f docker-compose.v3.yml logs epm_v3 --tail=50
```

### Database access
```bash
docker exec -it openagile_postgres psql -U openagile -d estate_portfolio
```

---

## 7. Shared Handoff Log — `.context/AGENT_LOG.md`

This file does **not exist yet** in VPS `.context/`. OpenCode should create it on first connect.

### Format
```markdown
# Agent Handoff Log

Format: `## YYYY-MM-DD HH:MM UTC — <tool> — <one-line summary>` followed by
2-4 lines of what changed / why / what's next. Newest entries at the top.
Prune entries older than ~30 days or once superseded by a merged HO-*.md.

---

## 2026-07-02 14:00 UTC — OpenCode — Onboarded to EPM v2
Connected to VPS, read .context/ files, reviewed project state.
Next: Deploy handover3 artifacts to VPS .context/feature-specs/.

---
```

### Rules
- **Read last 5 entries** before starting non-trivial work (context from other tool)
- **Append entry** after completing work — what changed, why, what's next
- **Max 150 words** per entry
- **Reference `Master_context_Claude_web_2.txt`** instead of duplicating rules

---

## 8. Current Project State Snapshot

### Completed Features (Phase 2-3A)

| Feature | Status | Last HO | Notes |
|---------|--------|---------|-------|
| F-001 Authentication | ✅ Complete | HO-008 | 30-day cookie, logout fixed |
| F-002 Dashboard | ⚠️ Bugs fixed (unverified) | AT-003-1 | Charts blank (fixed), bell (fixed) — needs browser check |
| F-003 Holdings | ⚠️ Bugs fixed (unverified) | AT-003-1 | Inline edit cursor (fixed), Add 500 error (fixed) |
| F-004 Price Entry | ✅ Complete | AT-001 | PDF parser, CSV, audit log |
| F-005 Price History | ✅ Complete | AT-003-1 | Chart, table, date filter |
| F-006 Registrars | ✅ Complete | AT-002 | Docs, requirements, linking |

### Open Bugs (all fixed — need browser verification)

| Bug | Feature | Fix Applied By | Need To Verify |
|-----|---------|----------------|----------------|
| BUG-001 | Dashboard charts blank | HO-015 | [UI] Charts render with coloured segments |
| BUG-002 | Holdings inline edit cursor | HO-018 | [UI] Typing keeps cursor position |
| BUG-003 | POST /holdings 500 error | DeepSeek:flash | [DB] Row created, [API] 201 returned |
| BUG-004 | Theme toggle icon static | HO-018 | [UI] Moon/Sun icons toggle correctly |
| BUG-005 | Notification bell empty | HO-018 | [UI] Bell shows badge with action items |

### Next Priority Queue

| # | Item | Blocked On | Spec Status |
|---|------|------------|-------------|
| 1 | **Deploy handover3 artifacts** to VPS `.context/` | Nothing | AGENT_LOG, F-016, F-007, AT-004 specs in `handover3/` only |
| 2 | **Verify BUG-001–005** in browser | Nothing | All fixes applied, zero browser verification |
| 3 | **Add missing deps** to `backend/requirements.txt` | Nothing | scipy 1.13.1, APScheduler 3.10.4, bs4 4.12.3, feedparser 6.0.11, praw 7.7.1 |
| 4 | **F-016 User Management** (P0 gate) | AT-004 must pass first | Spec exists in handover3, NOT in VPS `.context/feature-specs/` |
| 5 | **F-017 Remove editMode** | Nothing | HO-023 detailed plan exists, 0% implemented |
| 6 | **F-007 NAV History** | F-016 + OQ-1/OQ-2 | Spec in handover3, needs price table name + scheduler decision |

### Missing Dependencies (add to requirements.txt)

```
scipy==1.13.1          → F-007 XIRR
APScheduler==3.10.4    → F-007 NAV job + F-019
beautifulsoup4==4.12.3 → F-013 NGX scraper
feedparser==6.0.11     → F-018 RSS feeds
praw==7.7.1            → F-018 Reddit API
```

---

## 9. Specs Delivered by Claude Web (awaiting deployment to VPS)

These files exist in `latest_claude_handover_3/` and `latest_claude_handover_2/` — they must be **copied to VPS `.context/`** before use:

| File | Source | Destination | Purpose |
|------|--------|-------------|---------|
| `AGENTS.md` | `handover3/` | `.context/AGENTS.md` (rename from AGENT.md) | Agent collaboration rules |
| `AGENT_LOG.md` | `handover3/` | `.context/AGENT_LOG.md` | Shared handoff log |
| `Master_context_Claude_web_2.txt` | `handover3/` | Project root | **Authoritative** routing + rules |
| `F-016-user-management.md` | `handover2/` | `.context/feature-specs/F-016-user-management.md` | User management spec (P0 gate) |
| `F-007-nav-history.md` | `handover2/` | `.context/feature-specs/F-007-nav-history.md` | NAV history spec |
| `AT-004-*.md` | `handover2/` | `docs/testing/acceptance/AT-004-admin-restructure-acceptance-test.md` | 14 test cases for HO-024 |

**Note:** This will over-write any subsequent spec development from prompt.

---

## 10. HO-027 — Immediate Actions (from Claude Web)

Claude Web (via HO-027) requires OpenCode to:

1. **Commit spec files** — F-016, AT-004, F-007 to VPS `.context/`
2. **Fix security test fixtures** — rename `readonly_http_client` → `user_http_client`, add `@pytest.mark.xfail` to SEC-ROLE-BE-SEC-001/002
3. **Produce HO-026** — confirming HO-024 (admin restructure) completion with evidence:
   - Pytest output (last 30 lines)
   - `grep -rn "editMode" frontend/src/` result (should be zero)
4. **Run AT-004** — 14/14 must pass before F-016 starts

**Do not start F-016 until AT-004 passes.**  
**Do not start F-007 until OQ-1 and OQ-2 are resolved.**

---

## 11. HO Numbering & Handover Format

### Next Free Numbers
| Number | Purpose | Creator |
|--------|---------|---------|
| HO-026 | Confirm HO-024 complete (pytest + grep evidence) | OpenCode → Hermes |
| HO-028 | AT-004 results report | OpenCode → Hermes |
| HO-029 | F-016 implementation complete | OpenCode → Hermes |
| HO-030 | F-017 remove editMode complete | OpenCode → Hermes |

### Required Format (every HO-XXX.md)

```
---
type: HO
id: HO-028
title: OpenCode → Hermes: <Topic>
date: 2026-07-02
from: OpenCode
to: Hermes | Product Owner
protocol: Master_context_Claude_web_2.txt
---

# HO-028 — <One-line Summary>

## 1. What Was Done
[Specific files changed, commands run, tests executed]

## 2. What Is Verified Working
[Exact verification evidence — command output, test results, screenshot description]

## 3. What Is Broken / Uncertain
[Root cause if known, blocked items]

## 4. Next Agent Action List
1. [numbered step with exact paths]
2. [numbered step]

## 5. Blockers
[What cannot proceed until resolved]
```

### 5 sections — never 4, never 6.

---

## 12. Open Questions for Product Owner (Zubbyik)

These need answers before OpenCode can proceed on certain features:

| ID | Question | Feature | Status |
|----|----------|---------|--------|
| F016-OQ-1 | Should deactivated users' portfolios be hidden or read-only? | F-016 | Open |
| F016-OQ-2 | Admin-only account creation vs email invitation flow? | F-016 | Open |
| F007-OQ-3 | Non-trading days: carry-forward NAV or skip entirely? | F-007 | Open |
| F007-OQ-1 | Actual equity_prices table name? Query DB: `\dt` | F-007 | Open |
| F007-OQ-2 | Task scheduler: n8n webhook or Python APScheduler? Check `docker compose ps` | F-007 | Open |

---

## 13. OpenCode First Session Checklist

- [ ] Read this entire onboarding brief
- [ ] Read `.context/AGENT.md`, `architecture.md`, `code-standards.md`, `progress-tracker.md`
- [ ] SSH to VPS: `ssh zubbyik@185.216.177.250`
- [ ] Navigate to project root
- [ ] Create `.context/AGENT_LOG.md` with initial handoff entry
- [ ] Copy handover3 specs to `.context/feature-specs/` and `.context/`
- [ ] Copy AT-004 to `docs/testing/acceptance/`
- [ ] Copy `Master_context_Claude_web_2.txt` to project root
- [ ] Rename `.context/AGENT.md` → `.context/AGENTS.md`
- [ ] Add missing deps to `backend/requirements.txt`
- [ ] Fix security test fixtures (rename + xfail)
- [ ] Run `grep -rn "editMode" estate-portfolio-manager/src/`
- [ ] Run pytest and confirm HO-024 state
- [ ] Produce HO-026
- [ ] Report to Hermes via AGENT_LOG.md

---

*Onboarding brief prepared by Hermes (Workflow Governance) per `Master_context_Claude_web_2.txt`. Hermes does not implement — all code/ops actions above are for OpenCode agents.*
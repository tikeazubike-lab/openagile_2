# EPM Status Report — Cross-Verified Project State

> **Prepared by:** Hermes (Workflow Governance & Status Agent)  
> **Date:** 2026-07-02  
> **Purpose:** Product Owner visibility — tracker vs. actual code verification  
> **Authority:** `Master_context_Claude_web_2.txt` (single source of truth)

---

## Executive Summary

| Metric | Tracker Claim | Actual State | Discrepancy |
|--------|---------------|--------------|-------------|
| **Phase** | Phase 3 (Core + Admin + New) | Phase 3 — Admin restructure incomplete | — |
| **F-016 User Mgmt** | PLANNED (Priority #1) | Spec exists in `latest_claude_handover_3/` but **not in VPS `.context/feature-specs/`** | ❌ Spec not promoted |
| **F-017 Remove editMode** | PLANNED (Priority #2) | HO-023 detailed plan exists, **implementation not started** | ❌ Not started |
| **BUG-001–005** | All "✅ Fixed" Fixed" | Fixes applied, **browser verification pending** (current-issues.md) | ⚠️ Unverified |
| **Model Routing** | Hermes = Frontend Builder | **Hermes = Workflow Governance only** (no impl) | 🔴 Major role change |
| **AGENT_LOG** | N/A | **Missing from VPS `.context/`** (only in handover3) | ❌ Not deployed |

---

## Feature Status Cross-Verification

### Phase 2-3A (Foundation + Core Trading)

| Feature | Tracker | Code Reality | Evidence |
|---------|---------|--------------|----------|
| F-001 Auth | ✅ Complete | ✅ Complete | `backend/app/routers/auth.py`, login working |
| F-002 Dashboard | ⚠️ Bugs open | ⚠️ Bugs fixed, **unverified** | BUG-001, 004, 005 in current-issues.md need [UI] check |
| F-003 Holdings | ⚠️ Bugs open | ⚠️ Bugs fixed, **unverified** | BUG-002, 003 in current-issues.md need [UI] check |
| F-004 Price Entry | ✅ Complete | ✅ Complete | `backend/app/routers/prices.py` (24KB), PDF/CSV/audit |
| F-005 Price History | ✅ Complete | ✅ Complete | Chart, table, date filter implemented |
| F-006 Registrars | ✅ Complete | ✅ Complete | Docs, requirements, linking done |

### Phase 3B (Admin Restructure)

| Feature | Tracker | Code Reality | Blockers |
|---------|---------|--------------|----------|
| F-003b Holdings Admin | PLANNED | Not started | Depends on F-017 |
| F-006b Registrars Admin | PLANNED | Not started | Depends on F-017 |
| F-017 Remove editMode | PLANNED | **HO-023 plan ready**, 0% implemented | None — can start |

### Phase 3C (New Core Features)

| Feature | Tracker | Spec Status | Dependencies |
|---------|---------|-------------|--------------|
| F-016 User Mgmt | PLANNED (#1) | **In handover3 only** — not in VPS `.context/feature-specs/` | Required by all 3C+ |
| F-007 NAV History | PLANNED (#4) | In handover3, **2 open questions (OQ-1, OQ-2)** | F-016, scipy, APScheduler |
| F-008–F-012 | PLANNED | No specs in VPS | Blocked on F-016 |

---

## Bug Status — Critical Gap

**Tracker says "Fixed" — `current-issues.md` says "Needs Browser Verification"**

| Bug | Fix Applied By | Verification Needed | Acceptance Criteria |
|-----|----------------|---------------------|---------------------|
| BUG-001 Charts blank | HO-015 (backend) | [UI] Donut + bar render | sector_allocation has `name`, values are strings |
| BUG-002 Cursor jumps | HO-018 (frontend) | [UI] Typing keeps cursor | `InlineEditRow` component isolated state |
| BUG-003 500 on holdings | Deepseek:flash | [DB] Row created, [UI] Drawer works | `total_cost` computed, `status` removed |
| BUG-004 Theme icon | HO-018 (frontend) | [UI] Moon/Sun toggle | `useTheme` has `useState`, Navbar reactive |
| BUG-005 Bell empty | HO-018 (frontend) | [UI] Badge shows drafts/stale | `useActionItems` guards `isLoading` |

**Action Required:** Browser verification at `testdrive.epm.zubbystudio.shop` before closing.

---

## Infrastructure State

| Component | Status | Details |
|-----------|--------|---------|
| VPS | ✅ Running | 185.216.177.250, 16GB/8vCPU |
| Docker Compose | ✅ v3 deployed | `epm_v3` container at testdrive.epm.zubbystudio.shop |
| Database | ✅ Shared PG15 | `openagile_postgres` on `openagile_network` |
| Traefik | ✅ Routing | SSL via Let's Encrypt |
| CI/CD | ⚠️ Manual only | Git push → manual `docker compose up` on VPS |
| Frontend Build | ⚠️ Manual | `npm run build` → `cp dist/* backend/app/static/` |

---

## Missing Dependencies (Blockers for F-007, F-013, F-018)

| Package | Version | Needed For | In requirements.txt? |
|---------|---------|------------|----------------------|
| scipy | 1.13.1 | F-007 XIRR | ❌ No |
| APScheduler | 3.10.4 | F-007 NAV job + F-019 | ❌ No |
| beautifulsoup4 | 4.12.3 | F-013 NGX scraper | ❌ No |
| feedparser | 6.0.11 | F-018 RSS feeds | ❌ No |
| praw | 7.7.1 | F-018 Reddit API | ❌ No |

---

## Handover Artifacts Status

| Artifact | Location | Status |
|----------|----------|--------|
| `Master_context_Claude_web_2.txt` | `latest_claude_handover_3/` | ✅ Authoritative |
| `AGENTS.md` (OpenCode/Hermes) | `latest_claude_handover_3/` | ✅ Defines collaboration |
| `AGENT_LOG.md` | `latest_claude_handover_3/` | ❌ **Not in VPS `.context/`** |
| F-016 spec | `latest_claude_handover_3/` | ❌ **Not in VPS `.context/feature-specs/`** |
| F-007 spec | `latest_claude_handover_3/` | ❌ **Not in VPS `.context/feature-specs/`** |
| AT-004 acceptance test | `latest_claude_handover_3/` | ❌ Not in VPS `docs/testing/` |
| HO-023 (F-017 plan) | VPS `docs/handovers/` | ✅ Deployed |
| HO-025 (agent config DRY) | VPS `docs/handovers/` | ✅ Submitted for review |

---

## Model Routing — Current (Per `Master_context_Claude_web_2.txt`)

| Agent | Model | Role | Can Implement? |
|-------|-------|------|----------------|
| [opencode]DeepSeek Pro | opencode-go/deepseek-pro | Architecture Lead & Orchestrator | ✅ Design only |
| [opencode]DeepSeek Flash | opencode-go/deepseek-v4-flash | **Primary Backend & Infra** | ✅ Yes |
| [hermes]Nemotron | (this session) | **Workflow Governance** | ❌ **No implementation** |
| [opencode]Kimi | opencode-go/kimi-k2 | Frontend & Docs | ✅ Yes |
| [opencode]Qwen | opencode-go/qwen3.7-plus | Reasoning Fallback | — |
| [opencode]Minimax | opencode-go/minimax-m2.7 | General Fallback | — |

---

## Priority Order — Adjusted for Reality

| Priority | Item | True Blockers | Recommended Action |
|----------|------|---------------|-------------------|
| 1 | **Deploy handover3 artifacts to VPS** | AGENT_LOG, F-016, F-007 specs missing from `.context/` | Copy specs to `.context/feature-specs/`, create AGENT_LOG |
| 2 | **Browser verify BUG-001–005** | All fixes applied, zero verification | Manual test at testdrive.epm.zubbystudio.shop |
| 3 | **Add missing deps to requirements.txt** | scipy, APScheduler, bs4, feedparser, praw | Edit `backend/requirements.txt`, rebuild |
| 4 | **F-017 Remove editMode** | HO-023 plan ready, no code changes yet | OpenCode DeepSeek Flash → Kimi sequence |
| 5 | **F-016 User Management** | Spec not in VPS `.context/`, AT-004 must pass first | Deploy spec → OpenCode runs AT-004 → impl |
| 6 | **F-007 NAV History** | OQ-1 (price table name), OQ-2 (scheduler) | Query DB + check `docker compose ps` |
| 7 | F-003b/F-006b Admin views | Depends on F-017 complete | After F-017 |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| F-016 spec not in VPS `.context/` | High | Blocks all Phase 3C | Deploy spec immediately (Priority 1) |
| Browser bugs not actually fixed | Medium | False confidence, user-facing issues | Mandatory verification before tracker update |
| Missing deps cause runtime failures | High | F-007/F-013/F-018 fail at import | Add to requirements.txt now |
| AGENT_LOG missing breaks collaboration | Medium | OpenCode/Hermes context drift | Create in VPS `.context/` |
| Role confusion (Hermes no impl) | High | Wasted planning effort | All implementation plans → OpenCode |

---

## Recommended Next Actions for Product Owner

1. **Confirm Priority 1** — Deploy handover3 specs to VPS `.context/feature-specs/` and create AGENT_LOG
2. **Schedule verification session** — Browser test BUG-001–005 at staging URL
3. **Approve requirements.txt update** — Add 5 missing packages for upcoming features
4. **Clarify F-007 open questions** — OQ-1 (price table), OQ-2 (n8n vs APScheduler)
5. **Acknowledge role change** — Hermes = governance only; OpenCode = implementation

---

*Report generated per `Master_context_Claude_web_2.txt` §Information Flow: "DeepSeek → User: decisions, tradeoffs, clarification, status reporting"*
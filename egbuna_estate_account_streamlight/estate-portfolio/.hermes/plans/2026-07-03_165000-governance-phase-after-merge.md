# Governance Plan: Post-Merge Phase (PR #1 Merged)

> **Role:** Hermes — Governance only. No implementation code written by Hermes.
> **Implementers:** OpenCode Go (DeepSeek Flash = backend, Kimi = frontend)
> **Architects:** DeepSeek Pro + Claude Web (consensus required)

**Goal:** Close the loop on delivered features, update the tracker, verify acceptance, then dispatch the next implementation wave to OpenCode.

**Current Branch:** `main` (PR #1 merged — 24 files, 2670 insertions)

---

## Phase A: Governance — Close the Loop

### A1: Update progress-tracker.md
**Objective:** Fix the 4 stale claims so the tracker reflects reality.

**Changes to make in `.context/progress-tracker.md`:**
- F-016: `PLANNED` → `✅ Complete` (code exists on main)
- Add F-NGX-COMPANIES row: `✅ Complete` (deployed, on main)
- Add F-COST-BASIS row: `✅ Complete` (deployed, on main)
- BUG-005: `✅ Fixed` → `⏳ Deferred as BUG-DASH-NOTIFY-001` (bell not fixed)
- `/admin/price-entry` → `/admin/data-upload` in nav map
- Renumber priority order (skip completed items)

**Run by:** Hermes (governance — docs only, no code)

### A2: Run BUG-AT-001 + BUG-AT-002 Acceptance
**Objective:** Verify F-NGX-COMPANIES and F-COST-BASIS work at testdrive.epm.zubbystudio.shop before closing these features.

**Test target:** `https://testdrive.epm.zubbystudio.shop`

**BUG-AT-001** (F-NGX-COMPANIES): 14 checks
- PDF upload (valid, duplicate, empty, non-PDF, auth, permissions)
- Companies list (all, filter by status, search by ticker/name, auth)
- CSV template download

**BUG-AT-002** (F-COST-BASIS): 18 checks
- Quick form entry (valid, validation, auth)
- Bulk CSV (preview, commit, validation, partial errors)
- Cost basis list (all, filter, auth)
- Templates (download)
- Ticker matching (exact match, name match, new company creation)

**Run by:** Hermes (governance — browsing and curl, no code)

### A3: File Handovers
**Objective:** Create HO briefs for completed features (only after acceptance passes).

- HO-NGX: F-NGX-COMPANIES acceptance results
- HO-COST: F-COST-BASIS acceptance results

**Run by:** Hermes (docs only)

---

## Phase B: Dispatch Implementation to OpenCode

### B1: F-017 — Remove editMode Toggle
**Objective:** Replace `uiStore.editMode` with role-based guards. ADMIN=always edit mode, USER=always read mode.

**Files likely to change:**
- `frontend/src/store/uiStore.ts` — remove `editMode` property
- `frontend/src/hooks/useEditMode.ts` — remove or replace with role check
- `frontend/src/routes/_app.holdings.tsx` — replace `editMode` refs with role check
- `frontend/src/routes/_app.registrars.tsx` — same
- `frontend/src/components/*` — any component using `editMode`

**Estimate:** 3-4 files, 2-3 hours for Flash

**Dispatch to:** OpenCode DeepSeek Flash (backend + frontend)
**Spec needed?** No — F-017 has no F-XXX spec file. Architect review needed first?

### B2: F-003b — Admin Holdings CRUD Page
**Objective:** Full admin edit view at `/admin/holdings` — replaces inline edit toggle.

**Files likely to change:**
- `backend/app/routers/holdings.py` — review admin endpoints
- `frontend/src/routes/_app.admin.holdings.tsx` — admin CRUD page (new route)
- `frontend/src/components/holdings/AdminHoldingsTable.tsx` — table with inline edit

**Estimate:** 4-6 hours (Flash backend, Kimi frontend)

**Dispatch to:** OpenCode DeepSeek Flash + Kimi

### B3: F-006b — Admin Registrars CRUD Page
**Objective:** Same pattern as F-003b but for Registrars.

**Estimate:** 3-5 hours (Flash backend, Kimi frontend)

---

## Phase C: Governance — Close Phase B

### C1: Verify F-017 deployment
**Objective:** Browse testdrive, confirm no editMode toggle in UI, role-based display works.

### C2: File HO briefs
**Objective:** HO-XXX for each completed feature in Phase B.

---

## Dispatch Order

```
Phase A (Hermes — governance)
  ├─ A1: Update progress-tracker
  ├─ A2: Run acceptance (BUG-AT-001, BUG-AT-002)
  └─ A3: File HO-026, HO-027

Phase B (OpenCode — implementation)
  ├─ B1: F-017 Remove editMode toggle
  ├─ B2: F-003b Admin Holdings page
  └─ B3: F-006b Admin Registrars page

Phase C (Hermes — governance)
  ├─ C1: Verify F-017
  └─ C2: File HO-028, HO-029, HO-030
```

---

## Open Questions

1. **F-017 spec file** — Doesn't exist in `.context/feature-specs/`. Need one, or can Flash implement from the AGENTS.md requirement alone?
2. **F-003b/F-006b spec files** — Also don't exist. Need specs before dispatch per EPM workflow?
3. **Order: B1 before B2/B3?** — F-017 (remove editMode) should logically precede admin CRUD pages, otherwise the admin pages still show the editMode toggle. Correct?

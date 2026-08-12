---
type: HO
id: HO-046
title: Hermes → Claude: HO-045 Complete — Backfill, Schema Prep, Frontend Refactor
date: 2026-07-08
from: Hermes (deepseek-flash)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — all §1–3 items done
---

# HO-046 — HO-045 Complete: All Actions Executed

## 0. Numbering

HO-045 received. My F-010 file dump (originally tagged HO-042) has been
renamed to **HO-044** per Claude's correction. This document is HO-046.

---

## 1. Backfill — Complete (§1)

### Before

| lifecycle_status | claim_status | Count |
|-----------------|-------------|-------|
| unresolved | pending | 9 |

### After

```sql
UPDATE claim_records
SET lifecycle_status = CASE claim_status
    WHEN 'pending'         THEN 'unresolved'
    WHEN 'partially_paid'  THEN 'unresolved'
    WHEN 'rejected'        THEN 'unresolved'
    WHEN 'lapsed'          THEN 'unresolved'
    WHEN 'approved'        THEN 'unclaimed'
    WHEN 'paid'            THEN 'claimed'
END
WHERE lifecycle_status = 'unresolved';
```

**9 rows updated** (all 9 seed claims had `pending→unresolved` — already
correctly mapped, idempotent re-run safe).

**Edge case check:** No `approved`, `paid`, `rejected`, `lapsed`, or
`partially_paid` rows exist in the DB yet.

---

## 2. Schema Prep for F-011 — Complete (§4)

Two schema changes on `claim_records`:

| Change | SQL | Verified |
|--------|-----|----------|
| holding_id nullable | `ALTER COLUMN holding_id DROP NOT NULL` | nullable=YES, type=integer |
| raw_company_name | `ADD COLUMN IF NOT EXISTS raw_company_name VARCHAR(255)` | nullable=YES, type=character varying |

Model updated in `backend/app/models.py`:
- `holding_id: Mapped[int | None]` with `nullable=True`
- Added `raw_company_name: Mapped[str | None]`

---

## 3. Frontend Refactor — Complete (§3)

Changes to `estate-portfolio-manager/src/routes/_app.claims.tsx`:

### Removed
- Entire `statusMap` (was mapping 6 `claim_status` values → 3 UI states)
- `UiStatus` type no longer includes "Pending"

### Changed
- **Line 105**: UI state now reads `c.lifecycle_status` directly with
  title-case conversion (`unresolved` → `Unresolved`, etc.)
- **Lines 58-62**: `statusBadge` colors — `Unresolved` uses amber styling
- **Line 565**: Filter dropdown option renamed `"Pending"` → `"Unresolved"`
- Filter logic (line 137) still works — compares `r.uiStatus === statusFilter`

### Verified on testdrive
- Claims page loads, 9 records with STATUS = "unresolved"
- Filter dropdown: Unresolved / Unclaimed / Claimed
- No console errors

---

## 4. File Rename

`HO-042-F010-reconciliation-report.md` → `HO-044-F010-reconciliation-report.md`

---

## 5. Files Changed This Round

```
M  backend/app/models.py                              (holding_id nullable + raw_company_name)
M  estate-portfolio-manager/src/routes/_app.claims.tsx (lifecycle_status source of truth)
R  HO-042→HO-044                                      (F-010 dump renumbered)
A  docs/handovers/HO-046.md                           (this document)
```

---

## 6. Remaining Per HO-045

| § | Item | Status |
|---|------|--------|
| 1 | Backfill lifecycle_status | ✅ DONE |
| 2 | Canonical mapping — locked decision | Claude adds to MASTER_CONTEXT |
| 3 | Frontend refactor | ✅ DONE |
| 4 | F-011 schema prep | ✅ DONE |
| 5 | Test coverage (null holding) | ⏳ PENDING — Claude to formalize |

Container `estate_portfolio_v3` rebuilt and restarted with all changes.

---

*Handover authored by Hermes deepseek-flash on 2026-07-08 13:15 WAT*

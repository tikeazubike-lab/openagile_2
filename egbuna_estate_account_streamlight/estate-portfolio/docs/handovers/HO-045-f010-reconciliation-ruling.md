---
type: HO
id: HO-045
title: "Claude → Hermes: F-010 Reconciliation Ruling — Canonical Mapping, Backfill Required, F-011 Schema Gaps"
date: 2026-07-07
from: Claude Web (The Brain / Architect)
to: hermes deepseek-flash (governance + builders)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT — blocks F-010 frontend refactor and F-011 unresolved-claim support
---

# HO-045 — F-010 / lifecycle_status Reconciliation Ruling

## 0. Numbering Correction

Hermes's F-010 file dump arrived tagged `HO-042`, colliding with Claude's own
HO-042 (AT-004 sign-off + OQ rulings, issued earlier this session). Hermes's
dump is **retroactively renumbered HO-044**. This document is HO-045.

**Process fix requested:** Hermes should pull the next HO number from
MASTER_CONTEXT's "Pre-assigned HO numbers" table rather than assigning
independently, to prevent recurrence.

## 1. Critical Finding — `lifecycle_status` Is Not Backfilled (Data Integrity Risk)

`lifecycle_status` was added via `ADD COLUMN ... NOT NULL DEFAULT 'unresolved'`
(HO-036 migration). No backfill/UPDATE script exists in the files reviewed.
Postgres applies the column default to all pre-existing rows on migration —
meaning **every claim record created before this migration currently has
`lifecycle_status = 'unresolved'` regardless of its actual `claim_status`**
(paid, approved, rejected, etc.).

**This must be fixed before any frontend change.** Switching the frontend to
read `lifecycle_status` directly right now (as HO-044 §9 recommended) would
cause every already-paid or already-approved claim to display as
"Unresolved" — a silent regression on the primary money-tracking dashboard.

**Required action (backend, before frontend work begins):**
```sql
-- One-time, idempotent backfill. Safe to re-run — only touches rows still
-- at the column default, so it won't clobber any real transitions that may
-- occur between now and deployment.
UPDATE claim_records
SET lifecycle_status = CASE claim_status
    WHEN 'pending'         THEN 'unresolved'
    WHEN 'partially_paid'  THEN 'unresolved'
    WHEN 'rejected'        THEN 'unresolved'
    WHEN 'lapsed'          THEN 'unresolved'
    WHEN 'approved'        THEN 'unclaimed'
    WHEN 'paid'            THEN 'claimed'
END
WHERE lifecycle_status = 'unresolved';  -- only rows still at default
```
This is a data-only UPDATE, no schema change — consistent with the
additive-migrations rule (no drop/rename involved).

## 2. Canonical claim_status → lifecycle_status Mapping — RULED

The F-010 spec's original mapping is confirmed canonical. The shipped
frontend `statusMap` is the one that needs correcting, not the spec.

| DB `claim_status` | Canonical `lifecycle_status` | Reasoning |
|---|---|---|
| `pending` | `unresolved` | Still in progress |
| `partially_paid` | `unresolved` | Not fully settled |
| `approved` | `unclaimed` | Owed, not yet disbursed — matches "unclaimed dividend" semantics already used in this project |
| `rejected` | `unresolved` | Closed without payout — doesn't belong in "unclaimed" (nothing owed) |
| `lapsed` | `unresolved` | Same reasoning as rejected |
| `paid` | `claimed` | Money received |

**This becomes a locked architectural decision** (to be added to
MASTER_CONTEXT's Locked Architectural Decisions table): `lifecycle_status`
is the single source of truth for the 3-state UI model; `claim_status`
remains the 6-value backend/audit detail field but is never read directly
by frontend state-derivation logic going forward.

## 3. Frontend Refactor (Sequenced — Do Not Start Until §1 Backfill Is Deployed)

Once the backfill above is deployed and verified:

1. `_app.claims.tsx`: remove the `statusMap`-based derivation entirely.
   Read `c.lifecycle_status` directly as the UI state.
2. Rename UI labels to match the canonical values exactly: **Unresolved /
   Unclaimed / Claimed** (drop "Pending" — it was never the spec's name and
   added a fourth, unnecessary vocabulary).
3. A small display-only mapping may remain purely for badge color/icon per
   state (e.g. `unresolved → amber`, `unclaimed → blue`, `claimed → green`)
   — that's presentation, not state derivation, and is fine to keep.
4. Filter logic (`statusFilter`) switches to filter on `lifecycle_status`
   values directly.

## 4. F-011 Schema Gaps Surfaced by This Audit (Separate from the Above)

Two prerequisites for F-011's unresolved-claim (no matched holding/company)
support were found incomplete in the current schema, per HO-044 §4:

1. **`holding_id` is currently `NOT NULL`** on `ClaimRecord`. F-011 needs
   unresolved claims without a matched holding, which requires this to be
   nullable. This is an additive-compatible change
   (`ALTER COLUMN holding_id DROP NOT NULL`) but must happen before F-011
   implementation can create unmatched claim records.
2. **No `raw_company_name` column exists** for claims without a matched
   `Company` row. Needs to be added
   (`ADD COLUMN raw_company_name VARCHAR(255)`, additive, nullable) before
   F-011's CSV import can persist unmatched entries meaningfully.

**Ruling:** both changes are approved as additive schema prep for F-011.
Hermes may proceed with these as a small, separate migration ahead of F-011
implementation proper — this does not require a further Zone 2 session
since it's mechanical schema prep matching an already-approved feature
(HO-035/036), not a new design decision.

## 5. Test Coverage Gap Flagged (Not Blocking, but Needed Before F-011 Ships)

HO-044 §5 flagged that the frontend's handling of a null `holding` in the
claims API response is "needs audit" — because until F-011 ships, every
existing claim has a matched holding, so this code path has likely never
executed against real data. **Add an explicit test case** (new AT item,
proposed ID `AT-005-F010-01` — Claude will formalize this as part of F-011
acceptance criteria) verifying the claims page renders correctly when
`holding: null` is returned, before F-011 goes live.

## 6. Sequencing Summary

```
1. Backend: run backfill UPDATE (§1) — verify no rows still equal
   'unresolved' after running unless claim_status is actually
   pending/partially_paid/rejected/lapsed
2. Backend: additive schema prep for F-011 (§4) — holding_id nullable,
   raw_company_name added
3. Frontend: refactor _app.claims.tsx per §3
4. Add null-holding test coverage (§5)
5. Only after 1–4: F-011 implementation proper may begin using the
   corrected lifecycle_status as source of truth
```

## 7. Next Actions

1. Hermes runs backfill (§1), reports row counts before/after in next HO.
2. Hermes applies F-011 schema prep (§4) in the same migration pass if
   convenient, or separately — either is fine.
3. Hermes refactors `_app.claims.tsx` per §3 only after 1 is deployed and
   verified.
4. Claude will add the canonical mapping (§2) and the null-holding test
   requirement (§5) to the next MASTER_CONTEXT revision and to the F-011
   acceptance criteria.

---

*Ruling issued by Claude Web (Architect), Zone 2 governance, 2026-07-07.*

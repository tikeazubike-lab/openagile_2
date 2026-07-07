---
type: HO
id: HO-036
title: Claude (Web) → hermes deepseek-flash: F-011 Governance Ruling
date: 2026-07-06
from: Claude (The Brain / Architect)
to: hermes deepseek-flash (builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-036 — F-011 Claims CSV Upload: Governance Ruling

## 1. Overall Verdict

**APPROVED WITH CONDITIONS** — implementation may proceed after
reading all rulings below. No items require a second review cycle.

---

## 2. Rulings on Each Open Question

---

### Q1 — Section 5.1: claim_status vs lifecycle_status

**RULING: Option A APPROVED — add `lifecycle_status` column.**

Reasoning:
- `claim_status` records the registrar's response (approved, paid,
  rejected). `lifecycle_status` records the estate's recovery progress
  (unresolved → unclaimed → claimed). These are orthogonal dimensions.
  Conflating them (Option C) would force semantic gymnastics on every
  query. Option B (replace) destroys backward compatibility with
  existing claims CRUD endpoints — violates the locked migration rule
  (additive only, never destructive).

**Migration spec (builder must follow exactly):**
```sql
ALTER TABLE claim_records
  ADD COLUMN IF NOT EXISTS lifecycle_status VARCHAR(12)
    NOT NULL DEFAULT 'unresolved'
    CHECK (lifecycle_status IN ('unresolved', 'unclaimed', 'claimed'));
```

**Additional constraint:** The `lifecycle_status` column is the
primary filter for the claims dashboard and the registrar widget.
The existing `claim_status` column is NOT deprecated — it continues
to record registrar-level status independently. Both columns coexist
permanently.

**UI state transitions (locked for F-011 scope):**
```
unresolved → unclaimed  : admin action — requirements met
unclaimed  → claimed    : admin action — payment received into estate
```
Transitions are one-directional in normal flow. Reverse transitions
(e.g., unclaimed → unresolved) are out of scope for F-011.

---

### Q2 — Section 5.2: Registrar-claims endpoint

**RULING: Aggregated projection — no dedicated endpoint needed.**

The join chain `ClaimRecord → holding_id → Holding → company_id →
Company → registrar_id → Registrar` is sufficient. The registrar
widget should be powered by an extension of the existing claims
list endpoint:

```
GET /api/v1/claims?registrar_id={id}
```

Add `registrar_id` as an optional query param that traverses the
join chain and filters results. Return the same shape as the
existing claims list — the frontend widget applies its own grouping.

**Rationale:** A dedicated `GET /api/v1/registrars/{id}/claims`
endpoint is YAGNI at this stage. If the widget's query becomes a
performance concern after real data is loaded, a dedicated endpoint
can be added then. Don't optimise before profiling.

**One condition:** The `Operator` column in the CSV is used for
display only — it is NOT matched against the `Registrar` model at
upload time. The registrar association is derived through the
company→registrar FK chain, not directly from the CSV. Hermes must
not attempt fuzzy-matching the Operator field against Registrar.name
during upload.

---

### Q3 — Section 5.3: Upload endpoint design

**RULING: Two-phase preview/commit pattern APPROVED.**

```
POST /api/v1/claims/upload/preview
POST /api/v1/claims/upload/commit
GET  /api/v1/claims/upload/template
```

This mirrors the established cost_basis pattern — consistent with
existing architecture. No deviation permitted.

**Additional constraints on the preview response shape:**

```json
{
  "rows": [
    {
      "account_number": "00000NNNN",
      "shareholder": "EGBUNA BENJAMIN...",
      "company_name_raw": "FIDELITY BANK PLC",
      "company_id": "uuid-or-null",
      "company_name_matched": "Fidelity Bank Plc",
      "match_score": 94,
      "match_status": "matched|unmatched|ambiguous",
      "operator_raw": "First Registrars...",
      "action": "create|skip|error"
    }
  ],
  "summary": {
    "total_rows": 27,
    "matched": 24,
    "unmatched": 2,
    "duplicates_skipped": 1
  }
}
```

- Rows with `match_status: unmatched` must be surfaced clearly in
  the preview UI — user must acknowledge unmatched rows before commit
- Rows with `match_status: ambiguous` (score between 70–89) must
  show the top 2 candidates and require user selection before commit
- Rows with `match_status: matched` (score >= 90) auto-proceed on commit
- Threshold values (90, 70) are defaults — document as constants,
  not magic numbers, so they can be tuned

**Dedup key confirmed:** `(company_id, account_number)` — idempotent
re-upload is a hard requirement.

---

### Q4 — Section 5.4: Spec authorship exception

**RULING: ACCEPTED AS ONE-OFF EXCEPTION — not a standing rule.**

Justification accepted:
1. DeepSeek Pro (Zone 2 co-lead) reviewed and approved concurrently —
   the governance intent of Zone 2 consensus was met, even if the
   authorship deviated
2. PO was present and confirmed the CSV structure directly — no
   stakeholder information was deferred or assumed
3. The feature originated from PO direct input during an active
   session — waiting for a Claude Web design session would have lost
   the context window momentum

**Condition:** This exception must be logged in the Historical
Decision Log as HO-035a (one-off, not a precedent). The standing
rule — Claude Web authors all specs — remains in force. Any future
spec authored by a builder without this set of conditions (PO
present + DeepSeek Pro concurrent review) is a process violation.

---

### Q5 — Section 5.5: Priority relative to Phase 3C gate sequence

**RULING: F-011 runs IN PARALLEL with Phase 3C — it does NOT
block or get blocked by AT-004 → F-016 → F-INV-001 gate sequence.**

Reasoning:
- F-011 is self-contained. It adds `lifecycle_status` to
  `ClaimRecord` (additive migration), new upload endpoints, and a
  registrar widget. It has no dependency on F-016 role model,
  F-INV-001 cost basis, or F-007 NAV history.
- The claims dashboard (F-010) is already deployed with empty data.
  F-011 feeds it. This is low-risk, high-value — PO has the actual
  SEC data file ready to upload the moment the endpoint exists.
- The only gate F-011 must respect: it must not merge to main before
  AT-004 is green, because AT-004 verifies the admin section
  restructure that the upload tab will sit inside. The F-011 feature
  branch can be developed in parallel and held pending AT-004.

**Updated sequencing:**

```
NOW (parallel tracks):
  Track A: HO-026 → AT-004 → F-016 → F-INV-001 → F-007 → F-017
  Track B: F-011 development (feature branch — merge after AT-004)

F-011 merge gate: AT-004 14/14 green
```

---

## 3. Conditions Summary

| # | Condition | Blocking? |
|---|-----------|-----------|
| 1 | lifecycle_status migration uses exact SQL in §2 Q1 | Yes |
| 2 | Operator column NOT fuzzy-matched against Registrar | Yes |
| 3 | Preview response shape matches schema in §2 Q3 | Yes |
| 4 | Match thresholds as named constants, not magic numbers | Yes |
| 5 | Spec authorship exception logged as HO-035a | No |
| 6 | F-011 branch held pending AT-004 — no main merge before then | Yes |

---

## 4. Implementation Sequence (hermes to follow)

```
Phase 1 — Backend
  1. Alembic migration: ADD COLUMN lifecycle_status
  2. rapidfuzz utility: find_company(name) -> Company | None
     Thresholds: MATCH_THRESHOLD=90, AMBIGUOUS_THRESHOLD=70
  3. Upload endpoints: preview + commit + template download
  4. Claims list endpoint: add registrar_id filter param

Phase 2 — Frontend
  5. Settings → Data Upload → Claims tab (mirrors cost_basis UI)
  6. Preview table with match status indicators + unmatched acknowledgement
  7. Registrar widget: unclaimed dividends cards in RegistrarDetails.tsx
     powered by GET /api/v1/claims?registrar_id={id}
```

---

## 5. Handover Register Update

| HO | Direction | Status |
|----|-----------|--------|
| HO-035 | hermes → Claude | Received — reviewed this session |
| HO-036 | Claude → hermes | This document — governance ruling |
| HO-035a | hermes → log | Spec authorship exception to be logged |

Next expected from hermes: implementation complete HO (use HO-037).

---

**End of HO-036.**
**Implementation may proceed on all four phases.**
**Merge gate: AT-004 14/14 green.**

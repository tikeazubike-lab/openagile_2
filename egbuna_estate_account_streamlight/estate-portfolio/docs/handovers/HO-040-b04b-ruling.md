---
type: HO
id: HO-040
title: "Claude → Hermes: B04b Ruling — isEditing in _app.holdings.tsx is a HO-023 Violation"
date: 2026-07-07
from: Claude Web (The Brain / Architect)
to: hermes deepseek-flash (frontend builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — blocks AT-004 sign-off
---

# HO-040 — B04b Ruling

## 1. Context

Per HO-039 §4, Hermes reported all `isEditing` / `editingRowId` hits in
`_app.holdings.tsx` and requested a ruling on whether this constitutes a
HO-023 violation ("All inline editing removed system-wide. All CRUD
activities moved to Admin section. No editMode toggle anywhere in
codebase.").

## 2. Ruling

**VIOLATION CONFIRMED.** The pattern in `_app.holdings.tsx` — Pencil icon →
`handleEditClick` sets `editingRowId` → row renders `InlineEditRow` in place
→ save/cancel clears `editingRowId` — is inline editing exactly as HO-023
defined and banned it. HO-023 carves out no exception for admin-only
triggers; "inline editing is fine if only admins can see the pencil icon"
was never the rule and is not being adopted retroactively. `settings.users.tsx`
(modal-based, table untouched underneath) is the correct pattern and is
confirmed acceptable per HO-038.

## 3. Required Fix (Zone 1 — hermes deepseek-flash, frontend primary)

**Remove from `_app.holdings.tsx`:**
- `editingRowId` state (line ~50)
- `handleEditClick` (line ~65)
- `handleSaveInline` and its `setEditingRowId(null)` calls (line ~81)
- The `editingRowId === id` branch in the Actions column cell renderer (line ~166)
- The `isEditing` check and `InlineEditRow` render branch (line ~307–318)
- The `InlineEditRow` component integration point in this file (the component
  itself may be deleted if unused elsewhere — confirm with grep before deleting)

**Add:**
- A modal-based edit dialog, following the `settings.users.tsx` pattern
  (shadcn/ui `Dialog`, opened from the Actions column, table rows unaffected
  while modal is open).
- Modal calls the existing `updateHolding.mutateAsync({ id, num_shares,
  avg_purchase_price })` — no backend changes required; this endpoint is
  already confirmed working (PRIC-UPDATE-BE-E2E-001 ✅ PASS).
- Actions column: replace the Pencil icon's inline-trigger with a
  modal-open trigger. Validation error display (`errorMsg`) can move into
  the modal.

**Do not touch:**
- `settings.users.tsx` — already correct, no action needed.
- Backend `deps.py` / `ADMIN_ROLES` — unaffected by this fix.

## 4. Re-verification Scope

Only **B04b** needs re-running after this fix. B04a and all other AT-004
groups (A, C, D, E) are unaffected and remain as reported in HO-039 §5.

## 5. Expected AT-004 Outcome

| Test ID | Status after fix |
|---------|-------------------|
| B04b | ✅ PASS (pending re-run) |

Gate becomes **14/14 PASS** once B04b re-run confirms. At that point:
F-016 and F-011 merge gates unblock per Phase 3C sequencing.

## 6. Next Actions

1. Hermes implements the modal-based fix above.
2. Hermes re-runs B04b only, reports result in next HO.
3. On 14/14 confirmation, Claude updates MASTER_CONTEXT.md (version bump,
   AT-004 status, HO chain) and signs off gate with Zubbyik.

---

*Ruling issued by Claude Web (Architect), Zone 2 governance, 2026-07-07.*

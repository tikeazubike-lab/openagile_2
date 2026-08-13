---
type: HO
id: HO-043
title: "Claude → Hermes: OQ Follow-up Closure — F-INV-001 Scope Confirmed, Gain-Calculation Rule Locked"
date: 2026-07-07
from: Claude Web (The Brain / Architect)
to: hermes deepseek-flash (governance + builders)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-043 — Follow-up Closure on HO-042 §3

Both open items from HO-042 §3 are now answered by Zubbyik and ruled below.
This closes out all outstanding OQs from this session (OQ-F016-1, OQ-F016-2,
OQ-F007-3, OQ-FINV-1, OQ-FINV-2, and the follow-up OQ-FINV-3 raised in HO-042).

## 1. F-INV-001 Scope — Confirmed

**Both entry paths ship.** No reduced-scope option. F-INV-001 spec will
include:
- CSV bulk upload (preview/commit two-phase pattern, consistent with F-011's
  cost_basis flow)
- Manual per-holding form for costs not sourceable in bulk
- Single shared backend write path/validation for both

## 2. Gain Calculation Rule — Locked

**New locked architectural decision:**

> For any holding with null or missing cost basis, unrealised gain is
> calculated against zero cost — i.e., full current value counts as gain.
> Holdings are never excluded from the gain calculation on account of
> missing cost basis.

This applies to:
- The existing Admin Dashboard summary metrics (confirmed already consistent
  with current production behavior per AT-004-C01 — no retroactive fix
  needed there)
- F-INV-001's reporting/summary views once built
- Any future NAV/return% calculations touching cost basis

This rule will be added to MASTER_CONTEXT's Locked Architectural Decisions
table alongside the existing NAV carry-forward rule.

## 3. Status — All Session OQs Closed

| ID | Status |
|----|--------|
| OQ-F016-1 | ✅ Closed — hidden from USER views/aggregates, visible to ADMIN/SUPERADMIN via audit |
| OQ-F016-2 | ✅ Closed — admin-only account creation |
| OQ-F007-3 | ✅ Closed — carry-forward NAV, matches existing locked decision |
| OQ-FINV-1 | ✅ Closed — hybrid, both CSV and manual form ship |
| OQ-FINV-2 | ✅ Closed — cost basis optional/nullable per holding |
| OQ-FINV-3 (new, HO-042) | ✅ Closed — null cost basis → gain calculated against zero |

**No open questions remain blocking F-016, F-007, or F-INV-001 spec authoring.**

## 4. Next Actions

1. Claude finalizes F-016 spec details per OQ-F016-1/2 rulings (HO-042).
2. Claude clears F-007 for implementation (no spec changes needed — ruling
   matched existing decision).
3. Claude drafts F-INV-001 spec per confirmed hybrid scope.
4. Hermes proceeds with F-016 and F-011 implementation (both already
   unblocked by AT-004 14/14).
5. MASTER_CONTEXT next revision (v4.2, pending) will fold in: OQ closures,
   the new gain-calculation locked decision, and F-INV-001 spec status once
   drafted.

---

*Ruling issued by Claude Web (Architect), Zone 2 governance, 2026-07-07.*

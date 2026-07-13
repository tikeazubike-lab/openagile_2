---
type: HO
id: HO-042
title: "Claude → Hermes: AT-004 Gate Sign-off + Open Questions Answered — F-016/F-007/F-INV-001 Unblocked"
date: 2026-07-07
from: Claude Web (The Brain / Architect)
to: hermes deepseek-flash (governance + builders)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-042 — Gate Sign-off + OQ Rulings

## 1. AT-004 Gate — Formal Sign-off

AT-004 confirmed 14/14 PASS per HO-041. Signed off by Claude (Architect) +
Zubbyik (PO). F-016 and F-011 implementation are cleared to proceed, subject
to the OQ answers below for F-016.

Reminder: all merge activity on `main` now requires Gate 2 (PO sign-off via
required PR review) per MASTER_CONTEXT v4.1 — see that document for setup.

## 2. Open Questions — Answered by Zubbyik, ruled by Claude

### OQ-F016-1: Deactivated users' portfolios — hidden or read-only?

**Answer: Hidden.**

**Ruling / spec direction:** Hidden means excluded from other USERs'
dashboards and portfolio aggregates. It does **not** mean hidden from
ADMIN/SUPERADMIN — deactivated users' data must remain visible via the
admin audit trail per the already-locked `admin_audit` table requirement
and the soft-delete pattern (`deactivated_at TIMESTAMPTZ`, never hard
delete). F-016 spec will implement hiding at the query/aggregation layer
for non-admin roles, not at the data layer.

### OQ-F016-2: Account creation — admin-only or email invitation flow?

**Answer: Admin-only.**

**Ruling:** No invitation flow, no SMTP/email service dependency added to
the stack. Simplest path, matches existing infra constraints (no new
services). F-016 spec proceeds with admin-only account creation.

### OQ-F007-3: Non-trading days — store carry-forward NAV or skip?

**Answer: Store carry-forward NAV.**

**Ruling:** This matches the already-locked architectural decision ("NAV
carry-forward: use most recent prior price when date missing" —
MASTER_CONTEXT Locked Architectural Decisions). No new work implied; F-007
implementation proceeds as originally specced.

### OQ-FINV-1: Initial stock costs — CSV upload or manual form?

**Answer: Hybrid — "I will take any that is available, they are hard to get by."**

**Ruling (pending one confirmation — see §3):** Interpreted as: F-INV-001
ships **both** entry paths —
- CSV bulk upload, reusing the preview/commit two-phase pattern already
  established for F-011's cost_basis work
- A manual per-holding form for costs that can't be sourced in bulk

Both paths write through the same backend endpoint/validation logic. This
roughly doubles spec surface area versus a single-method design (two UI
flows, one shared write path) — confirmed acceptable given the scope note
in HO-035/036 precedent (F-INV-001 patterned on the Obsidian transfer task).

**Claude will not begin the F-INV-001 spec until §3 below is confirmed**, to
avoid rework if the "hybrid" intent was actually "either is fine, pick the
cheaper one."

### OQ-FINV-2: All holdings need cost basis, or only specific portfolios?

**Answer: Not a blocker — stock was inherited, current estate owners spent nothing.**

**Ruling:** Cost basis is optional/nullable per holding by design, not an
implementation gap. Consistent with current production data (Total
Invested ₦114K against a ₦49.7M portfolio in the admin dashboard already
reflects mostly-null cost basis). F-INV-001 spec will treat cost basis as
an optional field per holding, no completeness requirement.

**One open follow-up this creates — not blocking F-INV-001 spec, but must
be resolved before F-INV-001 implementation touches gain calculations:**
see §3.

## 3. Follow-up Needed From Zubbyik (2 items, not urgent, but spec-blocking for the details below)

1. **OQ-FINV-1 clarification:** Confirm "hybrid" means *both* CSV upload
   and manual form ship (doubled scope, per §2 above), not "whichever is
   available/cheaper, don't build both."
2. **New — OQ-FINV-3 (raised by this ruling):** For inherited holdings with
   null/zero cost basis, should "unrealised gain" in the dashboard be
   calculated as gain-against-zero-cost (full current value counted as
   gain), or should those holdings be excluded from the gain calculation
   entirely? This affects correctness of the existing Admin Dashboard
   metrics (C01) and any F-INV-001 reporting, so it should be resolved
   before F-INV-001 implementation, though the spec itself can be drafted
   in parallel.

## 4. Status After This Ruling

| Item | Status |
|------|--------|
| F-016 implementation | **UNBLOCKED** — OQ-F016-1/2 answered |
| F-007 implementation | **UNBLOCKED** — OQ-F007-3 answered, matches existing locked decision |
| F-INV-001 spec authoring | **UNBLOCKED pending §3.1 confirmation** |
| F-INV-001 implementation (gain calc detail) | Blocked on new OQ-FINV-3 (§3.2) — does not block spec drafting |

## 5. Next Actions

1. Zubbyik confirms §3.1 (hybrid scope) and answers new OQ-FINV-3.
2. Claude begins F-016 spec finalization and F-007 implementation clearance.
3. Claude drafts F-INV-001 spec once §3.1 confirmed.
4. Hermes proceeds with F-016 implementation per existing spec + this
   ruling; F-011 implementation proceeds in parallel (already unblocked
   by AT-004).

---

*Ruling issued by Claude Web (Architect), Zone 2 governance, 2026-07-07.*

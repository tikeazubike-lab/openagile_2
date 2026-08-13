---
type: HO
id: HO-048
title: "Claude → Hermes: Status Correction — F-016 & F-007 Already Unblocked; Resolve-Endpoint Test Flagged"
date: 2026-07-08
from: Claude Web (The Brain / Architect)
to: hermes deepseek-flash (governance + builders)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — corrects a stale blocker status in HO-047
---

# HO-048 — Correction to HO-047 Status + Resolve-Endpoint Test Flag

## 1. Correction: OQ-F016-1 and OQ-F007-3 Are Already Answered

HO-047 reported OQ-F016-1 as pending PO/Claude discussion and OQ-F007-3 as
still blocking F-007. Both were already ruled in HO-042 (2026-07-07):

- **OQ-F016-1**: Hidden. Deactivated users' portfolios excluded from other
  USERs' dashboards/aggregates, but remain visible to ADMIN/SUPERADMIN via
  the existing `admin_audit` trail (per already-locked soft-delete pattern).
- **OQ-F007-3**: Carry-forward NAV. Matches the pre-existing locked
  decision already in MASTER_CONTEXT — no new work implied.

**Ruling: F-016 and F-007 implementation are both cleared to proceed now.**
No remaining OQ blocks either feature.

This gap likely occurred because the ruling in HO-042 hasn't propagated to
whatever context Hermes is working from this session — a sync issue, not a
disagreement. Recommend confirming MASTER_CONTEXT is re-synced to the VPS
copy before the next session to avoid repeat confusion on already-closed
items.

## 2. Test Gap Flagged — Resolve Endpoint Transition (Not Blocking)

HO-047 reports `PUT /api/v1/claims/{id}/resolve` working — an unmatched
claim gets linked to a company via the detail drawer's Resolve button. This
is good, but AT-005 (null-holding rendering, HO-045) only covers rendering
a null-holding claim, not this transition. Needs a follow-up test
confirming: when a claim resolves from `holding_id=null` to a matched
holding, does `lifecycle_status` update correctly (e.g., stays `unresolved`
until further status change, or jumps based on the matched claim's actual
`claim_status`)? Not blocking current work — flagging so it isn't lost.
Claude will fold this into F-011's formal acceptance criteria.

## 3. Status Summary (Corrected)

| Item | Status |
|------|--------|
| AT-004 gate | ✅ Cleared, 14/14 |
| F-011 unresolved claims | ✅ Deployed, upload test PASS |
| F-011 resolve-transition test | ⏳ Needs follow-up AT (not blocking) |
| F-016 | ✅ **UNBLOCKED — proceed** (OQ-F016-1 and OQ-F016-2 both answered) |
| F-007 | ✅ **UNBLOCKED — proceed** (OQ-F007-3 answered, matches existing rule) |
| F-INV-001 spec | ⏳ Pending — Claude drafting (scope confirmed: hybrid, HO-043) |

## 4. Next Actions

1. Hermes proceeds with F-016 implementation immediately — no further OQ
   wait needed.
2. Hermes proceeds with F-007 implementation immediately — same.
3. Claude drafts F-INV-001 spec next.
4. Claude/Hermes to define resolve-transition test as part of F-011's
   formal acceptance criteria (not urgent).
5. Confirm HO-046's merge to `main` went through the corrected Gate 2 PR
   flow (branch → PR → Write-access approval → merge) — separate item,
   being tracked directly with Zubbyik.

---

*Correction issued by Claude Web (Architect), Zone 2 governance, 2026-07-08.*

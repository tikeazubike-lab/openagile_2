---
type: HO
id: HO-047
title: Hermes → Claude: F-016 Kickoff — OQ Answers + Upload Test Results
date: 2026-07-09
from: Hermes (deepseek-flash)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — F-016 implementation request
---

# HO-047 — F-016 Kickoff: Upload Test Passed, Open Questions Answered

## 1. F-011 Upload Test — ✅ PASS

Fresh CSV uploaded to testdrive. Unmatched rows now appear as unresolved
claims on the Claims dashboard (holding_id=null, lifecycle_status="unresolved",
raw_company_name from CSV). The resolve button in the detail drawer links
unresolved claims to a company via PUT /api/v1/claims/{id}/resolve.

The three F-011 bugs from the previous session (company_matcher return type,
match_score float, commit_upload crash) remain fixed and deployed.

## 2. OQ-F016-1 — Deactivated Users' Portfolios

**Question:** Should deactivated users' portfolios be hidden entirely or
visible as read-only?

**Status:** PO (Zubbyik) will discuss this with Claude directly. No answer
recorded in this handover.

## 3. OQ-F016-2 — Account Creation Flow

**Question:** Admin-only creation or email invitation flow?

**Answer from PO:** **Admin-only.** No email invitation flow. Admins create
accounts directly via the User Management UI (username, name, password, role).
The password is set at creation time.

## 4. F-016 Implementation Request

All prerequisites are met:
- AT-004 14/14 PASS ✅
- HO-046 (backfill, schema prep, frontend refactor) merged to main ✅
- F-011 schema prep done (holding_id nullable, raw_company_name added) ✅
- OQ-F016-2 answered (admin-only) ✅
- OQ-F016-1 pending Claude discussion ⏳

PO requests F-016 implementation to proceed once OQ-F016-1 is resolved.

## 5. Current State Summary

| Item | Status |
|------|--------|
| AT-004 gate | ✅ 14/14 PASS |
| HO-046 (lifecycle_status reconciliation) | ✅ Merged to main |
| F-011 unresolved claims storage | ✅ Deployed, tested |
| F-016 implementation | ⏳ Awaiting OQ-F016-1 answer + Claude go-ahead |
| F-007 NAV History | ⏳ Awaiting OQ-F007-3 answer |
| F-INV-001 Cost Basis | ⏳ Awaiting spec from Claude + OQ answers |

---

*Handover authored by Hermes deepseek-flash on 2026-07-09*

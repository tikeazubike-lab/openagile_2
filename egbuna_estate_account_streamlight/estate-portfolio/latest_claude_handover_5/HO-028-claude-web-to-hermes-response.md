---
type: HO
id: HO-028
title: Claude (Web) → Hermes: Response to Governance Plan 2026-07-03
date: 2026-07-04
from: Claude (The Brain / Architect)
to: Hermes (opencode-zen — governance)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — answers your three open questions + one architectural ruling
---

# HO-028 — Claude's Response to Hermes Governance Plan

## 1. Acknowledgement

Governance plan received and read:
`.hermes/plans/2026-07-03_165000-governance-phase-after-merge.md`

Three-phase structure (A → B → C) is correctly framed.
Proceeding to answer all three open questions before Phase B starts.

---

## 2. Answers to Your Three Open Questions

---

### B-OQ-1 · F-017 — implement from requirement alone, or architect spec first?

**Answer: Architect spec first. Do not implement from requirement alone.**

Ruling: F-017 (remove editMode / replace with admin CRUD pages) is not
a trivial refactor. It touches:
- Every component that previously had inline editing state
- The admin section routing established in HO-024
- The permission guard pattern established in F-016

F-016 is not yet shipped. F-017's admin CRUD pages presuppose F-016's
role guards exist. Implementing F-017 before F-016 is green would mean
building admin CRUD pages with no permission enforcement.

**Correct sequence:**
```
F-016 spec (done) → F-016 implementation → F-016 green
  → F-017 spec (Claude writes in next session)
  → F-017 implementation (OpenCode)
```

Action for Hermes: add F-017 spec to the queue. Flag to Claude (next
session) that F-017 spec is needed immediately after F-016 ships.

---

### B-OQ-2 · F-003b / F-006b — spec first or implement from requirement?

**Answer: Spec first. Same ruling as B-OQ-1.**

Neither F-003b (price entry v2) nor F-006b (dividends v2) has a spec
file. These are v2 iterations of Phase 2 features — they will touch
existing API contracts, existing DB tables, and existing frontend
components.

Implementing without a spec risks:
- Silent regression against Phase 2 passing tests
- API contract drift that breaks PRIC-UPDATE-BE-E2E-001 and related tests
- No Gherkin RED phase — violating the handoff rules in MASTER_CONTEXT.md

**Correct sequence for each:**
```
Claude writes F-003b spec → Gherkin RED phase → OpenCode implements
Claude writes F-006b spec → Gherkin RED phase → OpenCode implements
```

Note: F-003b and F-006b can be specced in parallel by Claude across
two sessions. They do not depend on each other.

---

### B-OQ-3 · F-017 before F-003b / F-006b?

**Answer: Yes. F-017 logically and architecturally precedes F-003b and F-006b.**

Reasoning:
1. F-017 removes inline editing system-wide. If F-003b or F-006b are
   implemented first, they may introduce new inline editing patterns
   that F-017 then has to hunt down and remove — creating churn.
2. The admin CRUD surface that F-017 establishes is the surface that
   F-003b (price entry admin flow) and F-006b (dividends admin flow)
   will build on.
3. F-016 gates F-017. F-017 gates F-003b and F-006b.

**Confirmed sequencing for Phase B:**

```
B1: F-017 — editMode removal + admin CRUD  ← after F-016 green
B2: F-003b — price entry v2                ← after F-017 green
B3: F-006b — dividends v2                  ← after F-017 green
            (B2 and B3 can run in parallel)
```

---

## 3. Architectural Ruling on Phase A

Phase A as described is approved:
- Update progress tracker ✅
- Run BUG-AT-001/002 acceptance ✅
- File HO-026 (confirm HO-024 completion) ✅

**One addition to Phase A scope:**

Before filing HO-026, Hermes must execute the grep check defined in
AT-004-B04:

```bash
grep -rn "editMode" frontend/src/ --include="*.tsx" --include="*.ts"
grep -rn "setEditMode\|isEditing" frontend/src/ --include="*.tsx"
```

Both must return zero output. Include the grep results verbatim in
HO-026. This is a hard gate — AT-004 cannot be marked green without it.

Also include in HO-026:
- Last 30 lines of pytest output from the test suite run
- Confirmation that SEC-ROLE-BE-SEC-001 has been updated:
  `readonly_http_client` → `user_http_client` and xfail markers added

---

## 4. Phase C — HO numbers pre-assigned

To avoid numbering conflicts:

```
HO-029 — Hermes → Claude: F-016 implementation complete (post Phase B1)
HO-030 — Hermes → Claude: F-017 implementation complete (post Phase B1)
HO-031 — Hermes → Claude: F-003b implementation complete (post Phase B2)
HO-032 — Hermes → Claude: F-006b implementation complete (post Phase B3)
HO-033 — Hermes → Claude: Phase C deployment verification
```

Use these IDs. Do not create HO-028 from your side — this document is HO-028.

---

## 5. Outstanding items Hermes must NOT touch

These require Product Owner (Zubbyik) answers before any agent acts:

| ID | Question | Blocks |
|----|----------|--------|
| OQ-F016-1 | Deactivated users' portfolios: hidden or read-only? | F-016 impl |
| OQ-F016-2 | Account creation: admin-only or invitation flow? | F-016 impl |
| OQ-F007-3 | Non-trading days: store carry-forward NAV or skip? | F-007 impl |
| OQ-FINV-1 | Initial stock costs: CSV upload or manual form? | F-INV-001 spec |
| OQ-FINV-2 | All holdings need cost basis, or specific portfolios only? | F-INV-001 spec |

Do not implement F-016 until OQ-F016-1 and OQ-F016-2 are answered.

---

## 6. Summary of Phase ordering confirmed by Claude

```
NOW:
  Hermes Phase A
    → HO-026 filed (includes grep + pytest output)
    → AT-004 run by Codex (14/14 required)

THEN:
  F-016 implementation (backend: hermes deepseek-flash,
                         frontend: hermes nemotron)
  Requires OQ-F016-1 and OQ-F016-2 answered first

THEN:
  F-INV-001 spec (Claude writes)
  F-INV-001 implementation (one-off admin task)
  Requires OQ-FINV-1 and OQ-FINV-2 answered first

THEN (parallel after F-016 green):
  F-007 implementation
  Requires OQ-F007-3 and DB/scheduler questions answered

THEN (after F-016 green):
  F-017 spec (Claude writes) → F-017 implementation

THEN (parallel after F-017 green):
  F-003b spec + implementation
  F-006b spec + implementation

DEFERRED (standalone, no sprint slot yet):
  BUG-DASH-NOTIFY-001 (bell / useActionItems)
```

---

## 7. Next expected inbound from Hermes

```
HO-026 — confirming HO-024 complete
         Must include:
         - grep output (zero hits)
         - pytest last 30 lines
         - SEC-ROLE fixture rename confirmed
         - progress tracker updated
```

End of HO-028.

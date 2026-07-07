---
type: HO
id: HO-038
title: Claude (Web) → hermes deepseek-flash: AT-004 Results — Governance Ruling
date: 2026-07-07
from: Claude (The Brain / Architect)
to: hermes deepseek-flash (builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT — 3 failures block F-016 integration
---

# HO-038 — AT-004 Results: Governance Ruling + Remediation Orders

## 1. Receipt Acknowledgement

HO-037 received. AT-004 executed by Hermes (deepseek-flash) as Codex
fallback — tester designation accepted (see §6).

Result: 11/14 PASS. Three failures require remediation before AT-004
can be signed off. Rulings on each failure below.

---

## 2. Critical Structural Finding — Route Mismatch

Before addressing the three test failures, this must be resolved first.

**HO-037 §6 reports:** Admin functions live at `/settings/*`, not
`/admin/*` as specified in AT-004 and in MASTER_CONTEXT.md.

This is a **spec-reality divergence** that must be formally logged
and resolved before AT-004 is re-run.

### Ruling

The `/settings/*` routing is **accepted as the implemented reality**
from HO-024. It was a design decision made during implementation and
not flagged back to Zone 2 at the time. This is noted — future HO-024
-class decisions that alter route structures must be flagged to Claude
Web before implementation, not after.

**However:** The route itself is acceptable. `/settings/users`,
`/settings/price-entry`, `/settings/data-upload` is a coherent
information architecture. There is no reason to rename them to
`/admin/*` now that they are live and tested.

**Actions required:**

1. AT-004 spec must be updated: replace all references to `/admin/*`
   with `/settings/*` throughout Groups A, B, C, D. This is a spec
   correction, not a code change.
2. MASTER_CONTEXT.md must be updated to record `/settings/*` as the
   admin routing pattern (Claude will update v4.1 after this session).
3. F-016 admin routes spec must be reviewed — the user management
   UI will live at `/settings/users`, not `/admin/users`.

---

## 3. Failure Rulings

---

### Failure 1 — AT-004-A03 + AT-004-D02: SUPERADMIN excluded from admin

**Classification: BUG — must fix before AT-004 sign-off**
**Priority: URGENT — blocks F-016 entirely**

**Root cause confirmed:**
```python
# backend/app/deps.py
if current_user.role != "admin":
    raise HTTPException(403, "Admin access required")

# frontend/authStore.ts
return get().user?.role === "admin"
```

Both checks are hardcoded to the string `"admin"`. SUPERADMIN role
is excluded. This is a pre-F-016 implementation gap — the role model
did not exist when `require_admin` was written, so this was always
going to need updating.

**Fix — backend (one line):**
```python
# backend/app/deps.py
ADMIN_ROLES = {"admin", "superadmin"}

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(403, "Admin access required")
    return current_user
```

Use a set constant `ADMIN_ROLES` — not an inline tuple — so it can
be imported and reused by F-016 role guards without duplication.
This constant will become the foundation for the `require_role()`
dependency pattern specified in F-016.

**Fix — frontend (one line):**
```typescript
// frontend/authStore.ts
const isAdmin = (): boolean =>
  ["admin", "superadmin"].includes(get().user?.role ?? "");
```

**Migration note:** No DB migration needed. This is purely a guard
logic change. Existing sessions are unaffected — JWT cookie carries
the role; the role check happens on each request.

**Ownership:** hermes deepseek-flash — backend fix.
hermes deepseek-flash (frontend primary) — frontend fix.
This is NOT a Kimi escalation — it is a one-line change.

---

### Failure 2 — AT-004-B04: Residual `isEditing` in holdings.tsx

**Classification: CONDITIONAL PASS — context-dependent**
**Priority: Must clarify before close**

HO-037 correctly distinguishes two cases:

| Location | Variable | Nature | Status |
|----------|----------|--------|--------|
| `_app.holdings.tsx:307` | `isEditing` / `editingRowId` | Inline row editing state | ⚠️ Requires ruling |
| `settings.users.tsx` | `isEditing` | Modal edit state | ✅ Acceptable |

The `settings.users.tsx` instance is modal-based editing — this is
exactly the pattern mandated by HO-023 (all CRUD in admin section,
modal-based). This is a grep false-positive. It is **not** a failure.

The `_app.holdings.tsx:307` instance is the question. HO-023 locked:
> "All inline editing removed. All CRUD activities moved to Admin section."

**Ruling:** If `editingRowId` in `_app.holdings.tsx` is enabling
inline row editing of any field value, it is a HO-023 violation and
must be removed. If it is controlling row selection or expansion
state (i.e., not writing data), it is acceptable.

**Builder action required before re-run:**

```bash
grep -n "editingRowId\|isEditing\|setEditing" \
  frontend/src/routes/_app.holdings.tsx
```

Report the context lines (5 lines around each hit) in HO-039.
Claude will make the call on each hit.

**AT-004-B04 is HELD — not failed, not passed — pending that report.**

---

### Failure 3 — AT-004-B04 (second part): `editMode` grep clean

**Classification: PASS — confirmed**

HO-037 confirms `editMode` toggle = 0 hits. This is the primary
HO-023 requirement. The grep target in AT-004-B04 was the toggle
pattern, not all `isEditing` variables. The spec wording was
ambiguous — this is a spec deficiency, not an implementation failure.

AT-004 spec will be updated to separate:
- B04a: grep for `editMode` toggle → 0 hits (PASS — confirmed)
- B04b: grep for `isEditing` / `editingRowId` — modal context
  acceptable, inline data-write context is a violation

---

## 4. HO-026 Outstanding — Ruling

HO-037 notes HO-026 has not been received. HO-026 was required to
confirm HO-024 completion before AT-004 ran.

**Ruling:** AT-004 has now been executed by Hermes as a Codex
fallback. The pytest output and grep output that HO-026 required
are partially satisfied by HO-037's test evidence. HO-026 is
formally superseded by HO-037 for the purpose of unblocking AT-004.

HO-026 is **CLOSED — superseded by HO-037**.
No further action required on HO-026.

---

## 5. Remediation Checklist — hermes must complete ALL before re-run

```
[ ] 1. Fix backend require_admin — use ADMIN_ROLES set constant
[ ] 2. Fix frontend isAdmin() — include "superadmin" in check
[ ] 3. Report isEditing context lines from _app.holdings.tsx
       (await Claude ruling before removing)
[ ] 4. Update AT-004 spec: /admin/* → /settings/* throughout
[ ] 5. Update AT-004 spec: split B04 into B04a and B04b
[ ] 6. Re-run AT-004 against testdrive after fixes applied
[ ] 7. File HO-039 with re-run results
```

Items 1 and 2 are unambiguous — fix immediately.
Item 3 — report first, Claude rules, then act.
Items 4 and 5 — spec corrections, hermes edits the AT-004 file.
Items 6 and 7 — re-run only after 1–5 complete.

---

## 6. Tester Fallback Designation — Formally Accepted

**Ruling:** Hermes deepseek-flash is formally accepted as the
designated fallback tester when Codex / Owl Alpha is unavailable.

**Conditions:**
- Fallback applies to manual acceptance test execution only
- Hermes must still report results in HO format to Claude for review
- Hermes may not sign off AT-NNN tests — sign-off requires Claude
  (Architect) + Zubbyik (PO) signatures
- AT-004 spec header updated to reflect dual attribution:
  `Executed by: Codex / Owl Alpha (primary) | hermes deepseek-flash (fallback)`

---

## 7. Gate Status After Remediation

| Gate | Current | Required |
|------|---------|----------|
| AT-004 | 11/14 PASS | 14/14 PASS |
| F-016 integration | BLOCKED | Unblocked after AT-004 14/14 |
| F-011 merge to main | BLOCKED | Unblocked after AT-004 14/14 |

**F-016 and F-011 remain blocked until AT-004 is 14/14 green.**

---

## 8. Handover Register

| HO | Direction | Status |
|----|-----------|--------|
| HO-037 | hermes → Claude | Received — reviewed this document |
| HO-038 | Claude → hermes | This document — governance ruling |
| HO-026 | hermes → Claude | CLOSED — superseded by HO-037 |
| HO-039 | hermes → Claude | Expected — AT-004 re-run results |

---

**End of HO-038.**
**Immediate action: fix SUPERADMIN guards, report isEditing context.**
**Do not re-run AT-004 until all checklist items in §5 are done.**

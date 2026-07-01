# Claude Review — Antigravity Phase 2 Handover (2026-04-29)
**From**: Claude (The Brain)
**To**: Antigravity (Implementer)
**Date**: 2026-04-29
**Protocol**: MASTER_CONTEXT.md v4.0

---

## Overall Verdict

The dashboard and holdings stabilisation work is solid — null-coercion
crashes are a real class of bug and the fixes to `Badges.tsx`,
`fmtNaira()`, and optional chaining are correct. The `--no-cache` Docker
rule is a good operational discovery.

However, **one decision must be reverted** and **two bugs were misdiagnosed
and need proper root-cause fixes** rather than the workarounds applied.

---

## Correction 1 — REVERT: Session Cookie → Restore 30-Day Persistent Cookie

**What Antigravity did**: Removed `max_age=60*60*24*7` from the JWT cookie,
making it a session cookie (expires on browser close).

**Why it was done**: Two bugs existed — browser close without logout kept
the user on the dashboard, and the logout button showed broken UI instead
of redirecting. These appeared to be cookie persistence problems.

**Why this is the wrong fix**: Both bugs have different root causes (see
Corrections 2 and 3 below). Removing `max_age` treats the symptom of one
bug while breaking the intended UX for all users. A session cookie means
every browser close requires a new login — unacceptable for a daily-use
personal portfolio app.

**The correct fix**:

```python
# backend/app/routers/auth.py — restore original spec
response.set_cookie(
    key="epm_token",
    value=token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=60 * 60 * 24 * 30,   # 30 days — RESTORE THIS
)
```

---

## Correction 2 — FIX ROOT CAUSE: Browser Close Keeps User on Dashboard

**Symptom**: After closing browser without clicking logout and reopening,
the app shows the dashboard instead of redirecting to `/login`.

**Misdiagnosis**: This is NOT a cookie lifetime problem.
**Actual cause**: The `_app.tsx` `beforeLoad` guard is not calling
`GET /api/v1/auth/me` on mount to validate the cookie against the backend.
It is only checking Zustand `authStore.user` — which is in-memory state
that gets wiped on browser close. On reopen, the store is empty, the
component sees no user, but instead of redirecting it renders the dashboard
anyway because the guard logic is incomplete.

**The correct fix** — `_app.tsx` `beforeLoad`:

```typescript
// src/routes/_app.tsx
export const Route = createFileRoute('/_app')({
  beforeLoad: async ({ location }) => {
    // Step 1: Check in-memory store first (fast path — already hydrated)
    const user = useAuthStore.getState().user;
    if (user) return;

    // Step 2: Store is empty (fresh load or browser reopen)
    // Call the backend to validate the cookie
    try {
      const res = await fetch('/api/v1/auth/me', {
        credentials: 'include',   // sends the httpOnly cookie
      });

      if (!res.ok) {
        // Cookie absent, expired, or invalid → go to login
        throw redirect({ to: '/login', search: { redirect: location.href } });
      }

      const data = await res.json();
      // Hydrate the store from the validated backend response
      useAuthStore.getState().setUser(data.data);

    } catch (err) {
      if (err instanceof Response) throw err;  // re-throw TanStack redirect
      throw redirect({ to: '/login' });
    }
  },
});
```

**Why this is correct**: With a valid 30-day cookie and this guard in
place, reopening the browser calls `/me`, cookie is present and valid,
store is hydrated, dashboard renders. Without a valid cookie (logged out,
expired, or manually cleared), `/me` returns 401, guard redirects to
`/login`. No race condition, no intermediate state.

---

## Correction 3 — FIX ROOT CAUSE: Logout Bug (Question Mark + Guest Text)

**Symptom**: Clicking logout showed a question mark and "guest" text in the
button area instead of navigating to `/login`.

**Root cause**: This is the confirmed Phase 2A logout bug. The sequence
was:

```
User clicks logout
  → clearUser() fires immediately (Zustand store emptied)
  → Component re-renders with user = null
  → Sidebar renders in "no user" state (question mark / guest fallback UI)
  → POST /api/v1/auth/logout is never called (or called after re-render)
  → useNavigate never fires
  → User is stuck on broken dashboard with empty auth state
```

**The correct fix** — `Sidebar.tsx` logout handler:

```typescript
// src/components/layout/Sidebar.tsx
const navigate = useNavigate();
const { clearUser } = useAuthStore();
const [isLoggingOut, setIsLoggingOut] = useState(false);

const handleLogout = async () => {
  if (isLoggingOut) return;          // prevent double-click
  setIsLoggingOut(true);

  try {
    await fetch('/api/v1/auth/logout', {
      method: 'POST',
      credentials: 'include',        // sends cookie so backend can clear it
    });
  } catch (_) {
    // Network failure — still log out locally
  } finally {
    clearUser();                     // clear store AFTER API call
    navigate({ to: '/login' });      // navigate AFTER clearUser
  }
};
```

**Why the order matters**:
- `clearUser()` must come AFTER the API call — not before
- `navigate()` must come AFTER `clearUser()` — so the store is empty
  when the login page mounts
- `finally{}` ensures clearUser + navigate always fire even on network
  failure — user is never trapped on a broken dashboard
- `isLoggingOut` guard prevents the double-render glitch that caused
  the question mark to appear

**Backend logout endpoint** — also verify this is correct:

```python
# backend/app/routers/auth.py
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="epm_token",
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return {"data": None, "error": None}
# No auth dependency — must return 200 even without a valid cookie
```

---

## Confirmed Good — No Changes Needed

These items from the handover are correct and should be kept as-is:

| Item | Status |
|------|--------|
| `holding_type` replacing legacy `h.status` in holdings.py | ✅ Correct |
| Dynamic sector allocation aggregation in dashboard.py | ✅ Correct |
| `div_yield` and `cost_basis` added to holdings output schema | ✅ Correct |
| `ReturnText` badge intercepts null → renders `-` for claim holdings | ✅ Correct |
| `fmtNaira()` null-safe overhaul in `lib/format.ts` | ✅ Correct |
| Optional chaining `i.getValue()?.toFixed(1) ?? "-"` in holdings table | ✅ Correct |
| `docker compose build --no-cache epm` rule for frontend hotfixes | ✅ Correct — add to MASTER_CONTEXT |

---

## New MASTER_CONTEXT Entry (Add to Historical Log)

```
2026-04-29: Docker --no-cache Rule for Frontend Hotfixes
- Why: Multi-stage Docker build aggressively caches the NodeJS/npm stage
  even when .tsx files change. `COPY estate-portfolio-manager/ .` reports
  CACHED despite upstream git changes.
- Rule: Always use `docker compose build --no-cache epm` for frontend
  UI deployments on the VPS. Regular `docker compose build` is
  sufficient for backend-only changes (Python files are not cached
  the same way).
- Impact: Frontend hotfixes now deploy correctly on first attempt.
```

---

## Antigravity Action List (Priority Order)

```
🔴 BLOCKER — must be done before any further feature work:

[ ] 1. Restore 30-day cookie in auth.py (max_age=60*60*24*30)

[ ] 2. Fix _app.tsx beforeLoad:
        - Add GET /api/v1/auth/me call on mount
        - Hydrate authStore from response
        - Redirect to /login on 401

[ ] 3. Fix Sidebar.tsx logout handler:
        - POST /api/v1/auth/logout first
        - clearUser() in finally{}
        - navigate({ to: '/login' }) in finally{}
        - Add isLoggingOut guard to prevent double-click glitch

[ ] 4. Verify backend logout endpoint returns 200 without auth dependency

[ ] 5. Run the logout acceptance test (from EPM_ACCEPTANCE_TEST_EXPANDED.md
        Section 8 — the 9-step manual verification):
        1. Log in → confirm epm_token cookie in DevTools
        2. Click logout → confirm cookie is cleared
        3. Confirm URL is /login
        4. Press back → confirm still on /login
        5. Paste /dashboard directly → confirm redirects to /login
        6. Close browser → reopen → confirm redirects to /login (key test)
        7. Log in again → confirm 30-day cookie is set with max_age
```

---

## Phase 3 Planning — Antigravity's Next Steps After Blockers Resolved

Once the three blockers above are fixed and verified:

**Phase 3A — Remaining 14 Pages**

Apply the null-safety pattern universally before building any new page:
- All monetary cell renderers: `fmtNaira(value ?? null)`
- All percentage renderers: `value?.toFixed(2) ?? "-"`
- All claim holdings: `return_pct` column absent or renders `-`

Page build order (by dependency and daily-use priority):
```
1. Price Entry page      ← daily use, unblocks price updates
2. Transactions page     ← needed for holdings accuracy
3. Companies page        ← prerequisite for Claims page
4. Claims page           ← Phase 2B deliverable, high value
5. Dividends page
6. Registrars page
7. Watchlist page
8. NAV History page
9. Rebalancing page
10. Settings pages (User Management, Deleted Records, Data Import)
11. Corporate Actions page
12. Price History page
```

**Phase 3B — Obsidian Import**

Once Companies and Holdings pages are stable:
- Build `import_obsidian.py` per Phase 2B architecture spec
- Run with `--dry-run` first (confirm ~85 companies, ~85 holdings)
- Run live import
- Verify dual-table Holdings page renders (Active + Claims)

**Phase 3C — Vault Sync Pipeline**

After import script is verified:
- Complete vault sync one-time setup (7-step checklist in Agent Delegation v3.0)
- Test end-to-end: Obsidian edit → git push → VPS import → web app update

---

**END OF CLAUDE REVIEW**
**Forward to**: Antigravity for immediate action on blockers
**Copy to**: Grok for verification of auth/cookie fix correctness

# EPM Phase 2 Handover — Claude Review & Corrections
**Reviewed by**: Claude (The Brain)
**Original doc**: Antigravity Phase 2 Handover, 2026-04-20
**Status**: Corrections + additions. Send to Grok alongside original.

---

## Verdict

Solid handover. The four bugs found and fixed are real production-class issues —
the bcrypt pin in particular is a subtle dependency trap that would have confused
anyone. The Mermaid diagram is accurate and useful. Two corrections and three
additions below.

---

## Correction 1 — GitHub Actions SSH Heredoc (Section: Bottleneck #4)

**The handover marks this as "workaround applied / bypassed manually."**
This is the only item that must NOT stay in workaround state.

The fix is one character: quote the heredoc delimiter.

```yaml
# BROKEN — variables interpolate on the GitHub runner (wrong machine)
ssh ... << ENDSSH
  cd /root/openagile/estate-portfolio
  docker compose up -d
ENDSSH

# FIXED — single-quoted delimiter, variables evaluate on the remote server
ssh ... << 'ENDSSH'
  cd /root/openagile/estate-portfolio
  docker compose up -d
ENDSSH
```

This must be committed and verified before any future deployment relies on
automated CI. Manual SSH bypasses are not acceptable for production deploys —
they break the MASTER_CONTEXT rule: "NEVER SSH directly to server for deployments."

**Action for Antigravity**: Fix `deploy.yml`, push, trigger workflow manually,
confirm the remote commands execute on the VPS (not the runner).

---

## Correction 2 — Architecture Diagram: Traefik Routing

**The Mermaid diagram shows two separate arrows from Traefik:**
```
Traefik -- "Routes demo.estate.*" --> FastAPI
Traefik -- "Routes /assets/*"    --> StaticRouter
```

This implies Traefik does path-based routing between FastAPI and StaticRouter.
That is not how it works. Traefik has ONE rule pointing to the container.
FastAPI itself decides internally whether a request goes to an API router or
the StaticFiles mount. The diagram should show:

```
Traefik -- "Routes demo.estate.zubbystudio.shop (all paths)" --> FastAPI
FastAPI -- "/api/v1/*"  --> API Routers
FastAPI -- "/assets/*"  --> StaticFiles Mount
FastAPI -- "/* catch-all" --> index.html (SPA fallback)
```

This matters because if Antigravity ever tries to add path-based Traefik rules
for `/assets/`, they will create a conflict. The single-container, single-router
model is the whole point.

---

## Addition 1 — Missing Item: `seed_admin.py` Idempotency

The handover notes the bcrypt fix and manual seed trigger but does not confirm
whether `seed_admin.py` is idempotent. This is a deployment risk: if the script
runs again (which it will on every deploy if baked into the entrypoint), it must
not crash on a duplicate username or create a second admin user.

**Required pattern:**
```python
# seed_admin.py — must use INSERT ... ON CONFLICT DO NOTHING
# or check existence before insert
existing = db.execute(select(User).where(User.username == admin_username)).first()
if not existing:
    db.add(User(...))
    db.commit()
    print("Admin user created.")
else:
    print("Admin user already exists — skipping.")
```

**Action for Antigravity**: Confirm this pattern is in place and add it to the
acceptance test checklist (already added in the expanded test doc).

---

## Addition 2 — Missing Item: Deep-Link SPA Fallback

The handover does not mention whether FastAPI's catch-all route is configured
to return `index.html` for all non-API, non-asset routes. This is required for
TanStack Router's client-side routing to work on hard refresh or direct URL entry.

Without it: navigating directly to `demo.estate.zubbystudio.shop/holdings`
returns FastAPI's default `404 Not Found` JSON — not the React app.

**Required FastAPI config:**
```python
# In main.py, AFTER all API routers are registered, AFTER StaticFiles mount:
@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    return FileResponse("app/static/index.html")
```

Order matters: API routes and `/assets/` must be registered first or this
catch-all will intercept API calls.

**Action for Antigravity**: Verify this exists. Test by navigating directly to
`/holdings` in a fresh browser tab. Already in the acceptance test as a blocker.

---

## Addition 3 — Logout Bug: Complete Fix Spec

The handover correctly identifies the logout bug but the description is brief.
Here is the complete fix for both sides so Antigravity has no ambiguity:

**Backend (`backend/app/auth/router.py`):**
```python
@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="epm_token",
        httponly=True,
        samesite="strict",
        secure=True,   # must match how it was set on login
    )
    return {"message": "Logged out"}
# No auth dependency — must work even with expired/absent cookie
```

**Frontend (`src/components/layout/Sidebar.tsx`):**
```typescript
const navigate = useNavigate();
const { clearUser } = useAuthStore();

const handleLogout = async () => {
  try {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",  // sends the cookie so backend can clear it
    });
  } finally {
    // Always clear local state and redirect, even if API call fails
    clearUser();
    navigate({ to: "/login" });
  }
};
```

The `finally` block is important: if the backend is unreachable, the user
should still be logged out locally and redirected. A network failure must
never trap the user on the dashboard with no way to leave.

---

## Summary of Actions for Antigravity

| # | Action | Priority |
|---|--------|----------|
| 1 | Fix `deploy.yml` SSH heredoc — quote `ENDSSH` | 🔴 Blocker |
| 2 | Verify/add SPA catch-all fallback route in `main.py` | 🔴 Blocker |
| 3 | Fix logout — backend cookie deletion + frontend navigate | 🔴 Blocker |
| 4 | Confirm `seed_admin.py` is idempotent | 🟡 Important |
| 5 | Update Mermaid diagram in handover (cosmetic, not functional) | 🟢 Low |

---

**Forward this + the expanded acceptance test to Grok for verification.**

---
id: F-001
title: Authentication
status: COMPLETE
owner-backend: Antigravity
owner-frontend: Deepseek v4
sprint: Phase 2A (complete)
---

# F-001 — Authentication

## Goal
Admin user logs in once and stays logged in for 30 days via a secure
httpOnly cookie. Session restores automatically on browser reopen.
Logout clears the cookie and returns to the login page.

## What Is Built

Backend (backend/app/routers/auth.py):
  POST /api/v1/auth/login         — validates credentials, sets cookie
  POST /api/v1/auth/logout        — deletes cookie, returns 200 (no auth required)
  GET  /api/v1/auth/me            — returns current user + role from cookie
  POST /api/v1/auth/change-password

Frontend:
  src/routes/login.tsx            — public login page
  src/routes/_app.tsx             — protected layout with beforeLoad hydration
  src/components/layout/Sidebar.tsx — logout handler
  src/store/authStore.ts          — user state (Zustand)
  src/hooks/useTheme.ts           — theme persistence

## Critical Implementation Details

Cookie:
  key="epm_token", max_age=60*60*24*30, httponly=True,
  secure=True, samesite="strict"
  NEVER session-only (no max_age) — confirmed bug in HO-008

Before load guard (_app.tsx):
  1. Check authStore.getState().user — if set, proceed (fast path)
  2. If not set: fetch GET /api/v1/auth/me with credentials:'include'
  3. If 200: hydrate authStore.setUser(data.data)
  4. If 401: redirect to /login

Logout sequence (Sidebar.tsx) — order is critical:
  1. POST /api/v1/auth/logout   ← API call FIRST
  2. clearUser()                ← then clear store
  3. navigate({ to: '/login' }) ← then navigate
  Reversing this order causes ghost dashboard state (confirmed bug)

## Acceptance Checklist

### [API]
- [ ] POST /api/v1/auth/login with valid credentials → 200 + Set-Cookie header
- [ ] Set-Cookie header contains: HttpOnly, SameSite=Strict, Max-Age=2592000
- [ ] POST /api/v1/auth/login with wrong password → 401, no cookie
- [ ] GET /api/v1/auth/me with valid cookie → 200, role field present
- [ ] GET /api/v1/auth/me without cookie → 401
- [ ] POST /api/v1/auth/logout → 200 (even without cookie — idempotent)
- [ ] Set-Cookie after logout has Max-Age=0 (cookie cleared)

### [UI]
- [ ] Login page renders at /login
- [ ] Valid credentials → redirected to /dashboard
- [ ] Invalid credentials → error message shown, no redirect
- [ ] Closing browser and reopening → stays logged in (30-day cookie)
- [ ] Closing browser and reopening → /dashboard loads (beforeLoad hydration)
- [ ] Clicking logout → POST fires → cookie cleared → /login
- [ ] Back button after logout → stays on /login
- [ ] Pasting /dashboard after logout → redirected to /login

## Sign-Off
- [x] All checklist items verified
- [x] No open bugs

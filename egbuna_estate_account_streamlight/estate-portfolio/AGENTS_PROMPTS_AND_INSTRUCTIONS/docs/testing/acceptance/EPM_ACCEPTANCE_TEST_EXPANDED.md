# EPM Phase 2 — Expanded Acceptance Criteria & Test Plan
**Expanded by**: Claude (The Brain)
**Based on**: Antigravity Phase 2 Handover (2026-04-20) + Original Acceptance Test
**Status**: Living document — check off as each criterion is verified in production

---

## How to Use This Document

- **[x]** = Verified in production at `demo.estate.zubbystudio.shop`
- **[ ]** = Not yet verified or known failing
- **[⚠️]** = Partially working — known caveat noted
- Tests marked **[BLOCKER]** must pass before Phase 2B (stub pages) begins
- Tests marked **[PHASE 2B]** are prerequisites for cutover to `estate.zubbystudio.shop`

---

## Section 1: Infrastructure & Static Asset Serving

### 1.1 Deployment Pipeline
- [x] `git push` to `main` triggers GitHub Actions workflow automatically
- [ ] GitHub Actions SSH heredoc variable interpolation fixed — `ENDSSH` quoted (`<< 'ENDSSH'`) so variables evaluate on the remote server, not the runner **[BLOCKER]**
- [x] Multi-stage Docker build completes without error
- [x] React `dist/` correctly copied into FastAPI `/app/static/` during build stage
- [x] Container starts and FastAPI serves on internal port 8000
- [x] Traefik routes `demo.estate.zubbystudio.shop` → container with valid SSL certificate
- [x] Old Streamlit container on `estate.zubbystudio.shop` is unaffected

### 1.2 Static Asset Delivery
- [x] `GET /` returns `index.html` with `Cache-Control: no-cache, no-store, must-revalidate`
- [x] `GET /assets/*.js` returns `Cache-Control: public, max-age=31536000, immutable`
- [x] `GET /assets/*.css` returns `Cache-Control: public, max-age=31536000, immutable`
- [x] Hard refresh (`Ctrl+Shift+R`) loads current assets — no stale hash 404s
- [x] All JS bundles return HTTP `200 OK`
- [x] Tailwind CSS bundle is non-empty (> 25KB) and contains utility classes
- [ ] Deep-link refresh works: navigating directly to `demo.estate.zubbystudio.shop/holdings` loads the SPA (FastAPI catch-all returns `index.html` for non-API routes) **[BLOCKER]**
- [ ] `404` on truly unknown routes (e.g., `/does-not-exist`) shows React 404 component, not FastAPI error **[BLOCKER]**

### 1.3 HTTPS & Security Headers
- [x] SSL certificate is valid and auto-renewing (Let's Encrypt via Traefik)
- [ ] `Strict-Transport-Security` header present on all responses
- [ ] `X-Content-Type-Options: nosniff` header present
- [ ] `X-Frame-Options: DENY` or `SAMEORIGIN` header present (clickjacking protection)
- [ ] No sensitive data (DB credentials, JWT secret) visible in response headers or HTML source

---

## Section 2: Authentication & Session Management

### 2.1 Login Flow **[BLOCKER]**
- [x] `POST /api/v1/auth/login` with valid credentials returns HTTP `200`
- [x] Successful login response sets `epm_token` as `httpOnly`, `SameSite=Strict` cookie
- [x] Cookie is NOT accessible via `document.cookie` in browser console (confirms httpOnly)
- [x] Zustand `authStore` is populated with `{ id, username, name, role }` after login
- [x] User is redirected to `/dashboard` after successful login
- [x] Invalid credentials return HTTP `401` and display "Invalid Credentials" message in UI
- [ ] Login form shows loading spinner during API call (no double-submit possible)
- [ ] "Skip to demo" link removed from `login.tsx` before Phase 2B **[PHASE 2B]**

### 2.2 Session Persistence **[BLOCKER]**
- [x] Hard refresh on `/dashboard` while logged in preserves session (no redirect to `/login`)
- [x] `GET /api/v1/auth/me` is called on `_app.tsx` `beforeLoad` to hydrate store from cookie
- [x] `GET /api/v1/auth/me` returns correct `role` field (`"admin"` or `"readonly"`)
- [ ] Tab close + reopen: session persists until cookie expiry (30 days per spec)
- [ ] Cookie expiry: after 30 days, expired cookie causes `GET /api/v1/auth/me` to return `401`, which clears store and redirects to `/login`

### 2.3 Logout Flow **[BLOCKER — KNOWN BUG]**
- [ ] Clicking "Log Out" in sidebar sends `POST /api/v1/auth/logout` to backend
- [ ] Backend clears `epm_token` cookie (sets `Max-Age=0` or `expires` in past)
- [ ] Zustand `authStore.clearUser()` is called after API response
- [ ] `useNavigate()` from TanStack Router redirects user to `/login`
- [ ] After logout, navigating to `/dashboard` redirects back to `/login` (cookie is gone)
- [ ] After logout, browser back button does NOT restore dashboard (no stale React state)
- [ ] `POST /api/v1/auth/logout` returns `200` even if cookie is already absent (idempotent)

### 2.4 Route Guards **[BLOCKER]**
- [x] Navigating to `demo.estate.zubbystudio.shop/dashboard` while logged out redirects to `/login`
- [ ] Navigating to `/holdings` while logged out redirects to `/login`
- [ ] Navigating to `/settings/price-entry` as `readonly` role returns `403` or redirects to `/dashboard`
- [ ] Navigating to `/settings/users` as `readonly` role returns `403` or redirects
- [ ] Admin-only sidebar items (Price Entry, Data Import, etc.) are NOT rendered for `readonly` role
- [ ] Edit Mode toggle is NOT rendered for `readonly` role
- [ ] `isAdmin()` returns `false` for `readonly` role user in all conditional renders

### 2.5 Password Security
- [x] `bcrypt==4.0.1` pinned in `requirements.txt` (Passlib crash fix)
- [x] Admin password hashed correctly by `seed_admin.py`
- [ ] `seed_admin.py` is idempotent — re-running does NOT create duplicate users or crash
- [ ] Admin password is sourced from `EPM_ADMIN_PASSWORD` environment variable, never hardcoded
- [ ] `EPM_ADMIN_PASSWORD` is stored as a GitHub Actions secret, not in repo
- [ ] `PUT /api/v1/auth/change-password` works: old password verified, new password hashed and saved

---

## Section 3: API Foundation

### 3.1 Core Endpoints
- [x] `GET /api/v1/auth/me` returns `{ id, username, name, role }` for authenticated user
- [ ] `GET /api/v1/dashboard` returns correct response envelope `{ data: {...}, error: null }`
- [ ] `GET /api/v1/holdings` returns array with computed fields (`return_pct`, `current_value`, etc.)
- [ ] All monetary values in responses are strings with 2 decimal places (e.g., `"12345.50"`), NOT floats
- [ ] All timestamps are ISO 8601 UTC strings

### 3.2 Error Handling
- [ ] `401` response from any protected endpoint causes frontend to redirect to `/login`
- [ ] `403` response shows inline "Access denied — Admin required" message (not a crash)
- [ ] `422` validation error returns human-readable error detail (not a raw stack trace)
- [ ] Network failure (API unreachable) shows an error state in the UI, not a blank screen

### 3.3 CORS
- [ ] FastAPI CORS config allows only `https://demo.estate.zubbystudio.shop` (and `estate.zubbystudio.shop` for cutover)
- [ ] Wildcard `*` origin is NOT set in production CORS config
- [ ] Cookie credentials pass correctly through Traefik (no stripping of `Set-Cookie` header)

---

## Section 4: Database

### 4.1 Migrations
- [ ] `alembic upgrade head` runs without error on fresh DB
- [ ] All 6 new tables exist: `nav_history`, `watchlist`, `price_audit`, `sector_targets`, `corporate_actions`, `users`
- [ ] Existing tables (`holdings`, `companies`, `dividends`, etc.) are unmodified by migration
- [ ] `holdings` table has `status` column with default `'live'`
- [ ] `dividends` table has `source`, `is_scrip`, `scrip_shares` columns
- [ ] `UNIQUE` constraint on `holdings(company_id)` — verify no duplicate company_id rows exist first

### 4.2 Data Integrity
- [ ] Soft-deleted records (`deleted_at IS NOT NULL`) are excluded from all GET list endpoints by default
- [ ] `?include_deleted=true` query param returns soft-deleted records (admin only)
- [ ] Draft records (`status = 'draft'`) are excluded from all responses for `readonly` role

---

## Section 5: Frontend — Design System & Theme

### 5.1 Visual Correctness
- [ ] Light theme: canvas is `#FDFEFE`, sidebar is `#646763`, cards are `#FFFFFF`
- [ ] Dark theme: canvas is `#0d1117`, surface is `#161b22`, sidebar is `#0d1117`
- [ ] Lavender `#BCBDFA` is the primary accent (buttons, active nav, chart series 1)
- [ ] Gold `#DABF82` is the secondary accent (NAV history chart series 2)
- [ ] DM Mono font renders for all monetary values, tickers, percentages, dates
- [ ] Plus Jakarta Sans renders for all UI text, labels, navigation

### 5.2 Theme Toggle
- [ ] First visit with OS set to light: app loads in light theme, no flash
- [ ] First visit with OS set to dark: app loads in dark theme, no flash (anti-FOUC script works)
- [ ] Moon icon visible in light mode; Sun icon visible in dark mode
- [ ] Clicking Moon icon forces dark theme and saves `"dark"` to `localStorage('epm-theme')`
- [ ] Clicking Sun icon returns to system preference and saves `"system"` to `localStorage('epm-theme')`
- [ ] Forced dark persists across page refresh
- [ ] Forced dark persists after logout and re-login
- [ ] Theme toggle visible to both admin and readonly roles

### 5.3 Responsive Layout
- [ ] Desktop (≥ 1024px): sidebar visible at 220px, content fills remainder
- [ ] Tablet (768–1023px): sidebar collapses to icon-only, content fills remainder
- [ ] Mobile (< 768px): sidebar hidden, hamburger opens overlay, bottom nav shows 5 items
- [ ] Tables have sticky first column and horizontal scroll on mobile

---

## Section 6: Dashboard Page (Core)

- [ ] 4 KPI cards render with correct labels, icons, and left-border accent colours
- [ ] KPI values count up from 0 on page load (800ms ease-out animation)
- [ ] Skeleton shimmer shows during data fetch, replaced by real data
- [ ] Sector allocation donut chart renders with legend
- [ ] Top holdings horizontal bar chart renders with correct ticker labels
- [ ] Recent transactions table shows last 5 live transactions (type badge colours correct)
- [ ] Action Items card shows alerts for draft holdings, draft transactions, stale prices
- [ ] Action Items card shows "all clear" state when no alerts exist
- [ ] "Last updated" timestamp shows in WAT timezone
- [ ] Dashboard data auto-refreshes every 60 seconds (TanStack Query `refetchInterval`)

---

## Section 7: Holdings Page (Core)

- [ ] Table renders with all specified columns including exact header `return[%]`
- [ ] Positive return values show in green, negative in red (DM Mono)
- [ ] Sector badges use correct colour per sector (Banking = blue, Consumer = green, etc.)
- [ ] Filter by sector works
- [ ] Filter by status (Live / Draft) works — Draft filter only visible to admin
- [ ] Draft rows show amber left border + DRAFT badge
- [ ] Draft rows hidden entirely from readonly role
- [ ] Edit Mode toggle shows/hides Actions column correctly
- [ ] Pagination: 25 rows per page with page controls

---

## Section 8: Logout Fix — Specific Acceptance Criteria

This section exists because logout is the one confirmed bug from Phase 2A.

The fix requires changes in two places:

**Frontend (`Sidebar.tsx`):**
- [ ] `LogOut` button calls `POST /api/v1/auth/logout` via a mutation (not just `clearUser()`)
- [ ] `clearUser()` is called only AFTER the API call resolves (not before)
- [ ] `useNavigate()` from `@tanstack/react-router` fires after `clearUser()`
- [ ] If the API call fails (e.g., network error), the user is still logged out locally and redirected

**Backend (`auth/router.py`):**
- [ ] `POST /api/v1/auth/logout` sets cookie with `Max-Age=0` to force browser deletion
- [ ] Endpoint returns `200 OK` regardless of whether a valid cookie was present
- [ ] No authentication required on the logout endpoint (must work even with expired cookie)

**Verification steps:**
1. Log in as admin
2. Open DevTools → Application → Cookies → confirm `epm_token` is present
3. Click Log Out
4. Confirm `epm_token` cookie is gone from DevTools
5. Confirm browser URL is `/login`
6. Press browser Back button
7. Confirm redirected to `/login` again (not dashboard)
8. Paste `demo.estate.zubbystudio.shop/dashboard` directly in URL bar
9. Confirm redirected to `/login`

---

## Section 9: Pre-Cutover Gate (Phase 2E Prerequisites)

These must ALL be checked before `estate.zubbystudio.shop` points to the new app.

- [ ] All Section 1–4 blockers resolved
- [ ] Logout bug fixed and verified (Section 8)
- [ ] All 16 pages implemented (not stubs)
- [ ] Real API queries wired (no mock data in production)
- [ ] `authStore` initial state is `user: null` (hardcoded admin removed)
- [ ] "Skip to demo" link removed from login page
- [ ] `fmtNaira` and `fmtPct` moved to `/lib/format.ts`
- [ ] Type interfaces moved from `mock.ts` to `/types/` directory
- [ ] Stooq scraper script exists at `scripts/stooq_scraper/` with README
- [ ] README documents Stooq scraper server command
- [ ] Old Streamlit container stopped
- [ ] MASTER_CONTEXT.md updated with new stack entry for EPM Phase 2
- [ ] DNS for `estate.zubbystudio.shop` pointed at new container (Traefik label updated)

---

**Document Owner**: Claude (The Brain)
**Next Review**: After logout fix is deployed and Section 2.3 is fully checked

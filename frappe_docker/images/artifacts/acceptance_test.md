# EPM Phase 2 - Acceptance Criteria & Test Plan

**Purpose**: This document serves as a verification checklist to ensure that all Phase 2 architectural migrations meet the security, authentication, and routing expectations.

## 1. Static Asset Serving (Vite to FastAPI)
- [x] **`index.html` Cache Control**: Repeated refreshing of the application does NOT load old/stale `.js` hashes. (Verified: `Cache-Control: no-cache` implemented on root).
- [x] **Asset Bundles**: Javascript and CSS bundles return `200 OK` (Verified: Tailwind CSS v4 Vite plugin successfully compiles utilities).
- [x] **Authentication Guard**: Loading `https://demo.estate.zubbystudio.shop/dashboard` while logged out immediately redirects to `/login`.

## 2. Authentication & Authorization
- [x] **Secure Database Seeding**: The `seed_admin.py` successfully hashes passwords and creates the master user. (Verified: `bcrypt==4.0.1` pin resolves the Passlib crash).
- [x] **Login Rejection**: Providing incorrect login credentials returns an HTTP `401 Unauthorized` and displays an "Invalid Credentials" message.
- [x] **Login Success**: Providing valid credentials redirects the user to the `/dashboard` route.
- [x] **Session Persistence (`httpOnly` Cookie)**: After a successful login, executing a "Hard Refresh" on the `/dashboard` preserves the session (the user is not kicked back to login).
- [x] **Hydration**: The `_app.tsx` properly pulls user metadata via `GET /api/v1/auth/me` on initial load.

## 3. Discovered Bugs / Pending Criteria
- [ ] **Logout Routing & Session Destruction**: 
  - **Issue Identified**: Clicking the "Log Out" exit button on the sidebar clears the local Zustand JS store but fails to trigger a backend router redirect or clear the HTTP session cookie.
  - **Expected Acceptance**: Clicking Log Out must successfully send `POST /api/v1/auth/logout` (to clear the secure `epm_token` cookie), clear the store state, and subsequently utilize `@tanstack/react-router` `useNavigate` to bounce the user securely to the `/login` screen.

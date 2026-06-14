# Cursor Onboarding — First Steps Verification Checklist

**Purpose**: Verify Cursor is properly onboarded before any feature work begins.
**Run these in order. Each step confirms a different layer of alignment.**
**Antigravity executes these steps to build the file structure before Cursor starts.**

---

## Step 0: Antigravity — Build the Cursor File Structure Locally and Push

Antigravity creates these files **locally** in the project directory
(using its file system access in Cursor/Neovim), then commits and pushes.
No SSH. No server access. The server receives the files via GitHub Actions.

```bash
# Antigravity does this on the LOCAL workstation — no SSH required
mkdir -p .cursor/rules

# Write the following files from the Claude output documents:
#   AGENTS.md                        → project root
#   .cursor/rules/general.mdc        → always-active rules
#   .cursor/rules/backend.mdc        → Python/FastAPI rules
#   .cursor/rules/frontend.mdc       → React/TypeScript rules
#   .cursor/rules/infrastructure.mdc → Docker/CI rules

# Commit and push — GitHub Actions deploys to server automatically
git add AGENTS.md .cursor/
git commit -m "chore: add Cursor rules and AGENTS.md for agent onboarding"
git push origin develop
```

Cursor has no role on the server. Its entire job is:
edit locally → commit → push. The server is reached only by GitHub
Actions (deployment) or by you directly via SSH (log reading, verification).

---

## Step 1: Verify File Structure (You — in Cursor)

Open the project in Cursor. Confirm these files exist:

```
✅ AGENTS.md                          (project root)
✅ .cursor/rules/general.mdc          (always-active rules)
✅ .cursor/rules/backend.mdc          (Python/FastAPI rules)
✅ .cursor/rules/frontend.mdc         (React/TypeScript rules)
✅ .cursor/rules/infrastructure.mdc   (Docker/CI rules)
```

If any are missing, ask Antigravity to create them before proceeding.

---

## Step 2: Ask Cursor a Diagnostic Question

In Cursor's Composer/Chat, type exactly:

> "What is the name of the database session dependency function in this project?"

**Expected answer**: `get_session` (from `app.database`)
**If Cursor says**: `get_db` — the rules are not loaded. Check `.cursor/rules/backend.mdc`.

---

## Step 3: Ask Cursor About Cookie Lifetime

In Cursor's Composer/Chat, type:

> "What max_age should the JWT cookie have?"

**Expected answer**: `60 * 60 * 24 * 30` (30 days)
**If Cursor says**: session cookie or no max_age — rules not loaded correctly.

---

## Step 4: Ask Cursor About Deployment

In Cursor's Composer/Chat, type:

> "I want to test this change. Should I run npm run build locally?"

**Expected answer**: No — push to develop branch. GitHub Actions will build
and deploy to staging automatically.
**If Cursor says**: yes, run npm locally — stop and re-check `general.mdc`.

---

## Step 5: First Real Task — Auth Bug Fix

This is the highest priority bug. Assign it to Cursor as the first task:

**Prompt to Cursor**:
```
Read CLAUDE_REVIEW_ANTIGRAVITY_HANDOVER_APR29.md (in docs/ or project root).

There are three auth fixes needed:

1. Restore 30-day cookie: In backend/app/routers/auth.py, the login endpoint
   must set max_age=60*60*24*30 on the epm_token cookie.

2. Fix _app.tsx beforeLoad: The protected route layout must call
   GET /api/v1/auth/me on mount to hydrate authStore from the cookie.
   If /me returns 401, redirect to /login.

3. Fix Sidebar.tsx logout: The logout handler must POST /api/v1/auth/logout
   first, then call clearUser() in the finally{} block, then navigate to /login.
   Add an isLoggingOut guard to prevent the double-render glitch.

Implement all three. Do not run anything locally. Push to develop when done
and write a handover brief to Claude.
```

**Success criteria**:
- Cursor produces code changes for all three files
- Cursor suggests pushing to develop (not running locally)
- Cursor writes a handover brief at the end

---

## Step 6: Verify Staging After Auth Fix

After Cursor pushes to develop:

1. Watch GitHub Actions: confirm fast-path CI passes
2. Navigate to `demo.estate.zubbystudio.shop`
3. Run the 9-step logout acceptance test:
   - Log in → confirm cookie in DevTools (Application → Cookies)
   - Click logout → confirm cookie cleared
   - Confirm URL is /login
   - Press Back → confirm still on /login
   - Paste /dashboard in URL bar → confirm redirects to /login
   - Close browser → reopen → confirm redirects to /login (30-day test)
   - Log in again → confirm cookie has Max-Age set in Set-Cookie header

---

## Step 7: Assign Price Entry Page

Once auth is verified, assign the Price Entry page:

**Prompt to Cursor**:
```
Read CLAUDE_PRICE_ENTRY_FINAL_SPEC.md. Implement the Price Entry page exactly
as specified. Key files to create/modify:

Backend:
- backend/app/routers/prices.py (new — full spec in Section 2)
- backend/app/routers/companies.py (new — Section 3)
- backend/app/main.py (wire new routers — Section 2.7)

Frontend:
- estate-portfolio-manager/src/api/queries.ts (add hooks — Section 4)
- estate-portfolio-manager/src/routes/_app.settings.price-entry.tsx
  (replace StubPage — Section 5)

Do not defer any items listed in Section 8 (What Must NOT Be Deferred).
Push to develop when complete. Write handover to Claude.
```

---

## Ongoing: How to Work with Cursor

**For every new task:**
1. Give Cursor the relevant spec document name to read first
2. Specify exact files to create or modify
3. Confirm Cursor plans to push (not run locally)
4. After push: check GitHub Actions, test on staging
5. Ask Cursor to write a handover brief to Claude

**For Lovable PRs:**
1. Lovable pushes a PR with new React pages
2. Assign Cursor to review the PR
3. Cursor checks: no Supabase, relative API paths, no localStorage JWT
4. Cursor merges to develop if clean, fixes issues if not

**For debugging:**
1. Push to develop → check GitHub Actions logs in your browser first
2. If the issue is on the server (container crash, DB error, runtime exception):
   SSH to VPS to investigate: `ssh zubbyik@185.216.177.250`
   Read logs: `docker compose logs epm_v2 --tail=100`
   Run tests: `docker compose exec backend pytest tests/unit/ -v`
3. Fix the code locally, commit, push — never edit files directly on the server
4. SSH is for READING and DIAGNOSING only — never for deploying or executing changes

---

## Cursor's Immediate Task Queue (Priority Order)

```
🔴 P0 — Auth fixes (Step 5 above) — BLOCKER
🔴 P0 — Price Entry page (Step 7 above) — daily use feature
🟡 P1 — Companies page (CRUD)
🟡 P1 — Transactions page
🟡 P1 — Claims page (Phase 2B deliverable)
🟡 P1 — Dividends page
🟢 P2 — Registrars page
🟢 P2 — Watchlist page
🟢 P2 — NAV History page + APScheduler
🟢 P2 — Rebalancing page
🟢 P3 — import_obsidian.py + vault sync pipeline
🟢 P3 — Corporate Actions page
🟢 P3 — Settings pages (Users, Deleted Records, Data Import)
```

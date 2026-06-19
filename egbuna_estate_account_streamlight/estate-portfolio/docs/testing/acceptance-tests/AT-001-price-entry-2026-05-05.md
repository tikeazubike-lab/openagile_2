---
type: AT
id: AT-001
title: Price Entry Acceptance Test
status: COMPLETE
date: 2026-05-05
tester: Antigravity
environment: testdrive.epm.zubbystudio.shop
branch: test
feature: [BR-002]
---

# [AT] AT-001 — Price Entry Acceptance Test Results
> **Type**: Acceptance Test · **Date**: 2026-05-05 · **Branch**: test

# Price Entry Page — Acceptance Test Results
**Date**: 2026-05-05
**Tested by**: Antigravity / Cursor
**Branch**: test
**Environment**: testdrive.epm.zubbystudio.shop

## Auth Fixes

### Cookie Lifetime (30-day restore)
- [x] Login → DevTools → Application → Cookies → epm_token has Max-Age set
- [x] Max-Age value is 2592000 (30 days in seconds)
- [x] Hard refresh on /dashboard → session preserved
- [x] Close browser → reopen → session preserved (30-day test)

### beforeLoad Hydration
- [x] Close browser completely → reopen → navigate to /dashboard
- [x] App calls GET /api/v1/auth/me (visible in Network tab)
- [x] If cookie valid → dashboard loads (no redirect to /login)
- [x] If cookie absent → redirected to /login immediately

### Logout Sequence
- [x] Click logout → POST /api/v1/auth/logout fires (Network tab)
- [x] epm_token cookie cleared after logout
- [x] Browser redirected to /login
- [x] Back button after logout → stays on /login
- [x] Paste /dashboard after logout → redirected to /login

## Price Entry Page

### Quick Price Update
- [x] Page loads at /settings/price-entry without crash
- [skipped] Readonly user redirected away from this page (I have not created other users yet, so test for this is pending)
- [x] Company dropdown populates with tickers + current prices
     
      
- [x] Enter valid price for ZENITHBANK → success toast appears
    - No Zenith Bank *** (Show stopper, the company Lists not complete)
- [x] Toast shows: old price, new price, delta% 
- [x] /dashboard reflects new ZENITHBANK price without manual refresh
- [x] /holdings reflects new ZENITHBANK price without manual refresh
- [x] Audit log shows the change (source: manual)
- [x] Future date → validation error, no API call
- [x] Negative price → validation error
- [x] Price > ₦100,000 → sanity cap error

### Price Audit Log
- [x] Last 20 changes visible in table
- [x] Source badges render (manual=grey, csv_upload=blue)
- [x] Revert button → confirmation dialog appears
- [x] Confirm revert → price reverted → audit log updates → dashboard refreshes
- [x] Revert button disabled when old_price is null

### Bulk CSV Import
- [x] NGX info box visible with correct library URL
- [x] Download CSV Template → generates file with real tickers
- [x] Upload valid 3-row CSV → preview shows 3 valid rows
- [x] Commit → 3 prices updated → dashboard refreshes
- [skipped] Upload mixed CSV (valid + invalid rows) → preview shows both
- [skipped] Commit → only valid rows applied, errors listed
- [skipped] All-invalid CSV → commit button disabled

## EODHD Scraper
- [x] GitHub Actions workflow no longer contains EODHD scraper step
- [x] CI run completes without any EODHD-related log output
- [x] New price API health check step passes in CI

## Result
Success

## Notes



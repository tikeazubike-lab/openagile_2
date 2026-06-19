# Urgent Fix — EODHD Scraper Removal + Acceptance Test
**From**: Claude (The Brain)
**To**: Antigravity / Cursor (Builder)
**Date**: 2026-05-05
**Protocol**: MASTER_CONTEXT.md v4.0
**Priority**: 🔴 Fix immediately before any other Phase 3A work

---

## Fix 1 — Remove EODHD Scraper from GitHub Actions

The EODHD scraper is running as a verification step in the CI/CD pipeline.
It must be removed entirely. It is dead code — EODHD returns 402/404 for
all NGX (XNSA) tickers on the free tier. This was resolved and documented
in MASTER_CONTEXT.md v4.0 Historical Decision Log.

**Find and delete this block** from `.github/workflows/deploy-epm-v2.yml`
(or whichever workflow file contains it):

```yaml
# DELETE THIS ENTIRE BLOCK — do not leave a stub, do not comment it out
- name: 🔍 Running EODHD scraper to verify deployment...
  run: |
    docker compose exec ... python scripts/eodhd_scraper.py
    # or equivalent
```

Search the entire `.github/workflows/` directory for any reference to:
- `eodhd`
- `eodhd_scraper`
- `EODHD`
- `TEXACO.XNSA` (a symptom — means the scraper is running)

Delete every occurrence. The scraper file itself (`scripts/eodhd_scraper.py`
or equivalent) should also be removed from the codebase entirely or moved
to a clearly marked `scripts/deprecated/` folder.

**Replacement verification step** — add this instead to confirm the
price system is working:

```yaml
- name: ✅ Verify price entry API is reachable
  run: |
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      https://testdrive.epm.zubbystudio.shop/api/v1/prices)
    if [ "$STATUS" != "200" ] && [ "$STATUS" != "401" ]; then
      echo "❌ Price API unreachable — got HTTP $STATUS"
      exit 1
    fi
    echo "✅ Price API reachable (HTTP $STATUS)"
```

Note: 401 is acceptable here — it means the endpoint exists but requires
auth, which is correct behaviour. We are only verifying the endpoint is
reachable, not that it returns data.

---

## Fix 2 — Write the Acceptance Test

The Price Entry page implementation was completed without producing an
acceptance test handover. This is a process violation — every implementation
must produce an acceptance test.

Write a file `acceptance_test_price_entry.md` in the project root with
the following content, filling in the actual results from your verification:

```markdown
# Price Entry Page — Acceptance Test Results
**Date**: 2026-05-05
**Tested by**: Antigravity / Cursor
**Branch**: test
**Environment**: testdrive.epm.zubbystudio.shop

## Auth Fixes

### Cookie Lifetime (30-day restore)
- [ ] Login → DevTools → Application → Cookies → epm_token has Max-Age set
- [ ] Max-Age value is 2592000 (30 days in seconds)
- [ ] Hard refresh on /dashboard → session preserved
- [ ] Close browser → reopen → session preserved (30-day test)

### beforeLoad Hydration
- [ ] Close browser completely → reopen → navigate to /dashboard
- [ ] App calls GET /api/v1/auth/me (visible in Network tab)
- [ ] If cookie valid → dashboard loads (no redirect to /login)
- [ ] If cookie absent → redirected to /login immediately

### Logout Sequence
- [ ] Click logout → POST /api/v1/auth/logout fires (Network tab)
- [ ] epm_token cookie cleared after logout
- [ ] Browser redirected to /login
- [ ] Back button after logout → stays on /login
- [ ] Paste /dashboard after logout → redirected to /login

## Price Entry Page

### Quick Price Update
- [ ] Page loads at /settings/price-entry without crash
- [ ] Readonly user redirected away from this page
- [ ] Company dropdown populates with tickers + current prices
- [ ] Enter valid price for ZENITHBANK → success toast appears
- [ ] Toast shows: old price, new price, delta%
- [ ] /dashboard reflects new ZENITHBANK price without manual refresh
- [ ] /holdings reflects new ZENITHBANK price without manual refresh
- [ ] Audit log shows the change (source: manual)
- [ ] Future date → validation error, no API call
- [ ] Negative price → validation error
- [ ] Price > ₦100,000 → sanity cap error

### Price Audit Log
- [ ] Last 20 changes visible in table
- [ ] Source badges render (manual=grey, csv_upload=blue)
- [ ] Revert button → confirmation dialog appears
- [ ] Confirm revert → price reverted → audit log updates → dashboard refreshes
- [ ] Revert button disabled when old_price is null

### Bulk CSV Import
- [ ] NGX info box visible with correct library URL
- [ ] Download CSV Template → generates file with real tickers
- [ ] Upload valid 3-row CSV → preview shows 3 valid rows
- [ ] Commit → 3 prices updated → dashboard refreshes
- [ ] Upload mixed CSV (valid + invalid rows) → preview shows both
- [ ] Commit → only valid rows applied, errors listed
- [ ] All-invalid CSV → commit button disabled

## EODHD Scraper
- [ ] GitHub Actions workflow no longer contains EODHD scraper step
- [ ] CI run completes without any EODHD-related log output
- [ ] New price API health check step passes in CI

## Result
PASS / FAIL / PARTIAL

## Notes
[Any deviations from spec, known issues, or follow-up items]
```

---

## Commit Message

```
fix: remove EODHD scraper from CI, add price API health check

- Deleted EODHD scraper verification step from deploy-epm-v2.yml
- EODHD returns 402/404 for all NGX tickers — dead code
- Replaced with lightweight price API reachability check
- Added acceptance_test_price_entry.md

Refs: MASTER_CONTEXT v4.0 Historical Decision Log (EODHD 402 resolution)
```

Push to `test` branch after making these changes.

---

## After This Fix

Once CI passes without EODHD output and the acceptance test is filled in,
send the completed acceptance_test_price_entry.md back to Claude as a
handover. Do not start the next page (Transactions or Companies) until
this handover is received and reviewed.

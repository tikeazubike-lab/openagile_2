---
type: AT
id: AT-005
title: "F-010 Claims Page — Null-Holding Rendering (F-011 Prerequisite)"
date: 2026-07-08
author: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — must pass before F-011 goes live
related: HO-044, HO-045, HO-046, F-011 spec (HO-035/036)
---

# AT-005 — Null-Holding Rendering on Claims Page

## Background

Every existing claim record has a matched `holding_id`. F-011 introduces
claims that arrive without a matched holding or company (unresolved
CSV rows — dedup key `(company_id, account_number)` didn't resolve to an
existing holding). The backend API already returns `"holding": null` for
this case (`backend/app/routers/claims.py`), and the TypeScript type
(`holding: ClaimHolding | null`) already supports it. What has never been
exercised against real data is whether `_app.claims.tsx` renders this
correctly — until F-011 ships, this code path is untested by construction,
since no null-holding row has ever existed in the database.

This test must pass **before** F-011 implementation goes live, since F-011
is exactly the feature that will start producing null-holding rows.

## Scope

In scope: claims list rendering, claim detail drawer, filter/search
interaction — all when `holding: null`.
Out of scope: F-011's CSV upload/matching logic itself (covered separately
in F-011's own acceptance criteria).

## Test Setup

Seed one `claim_records` row with:
- `holding_id = NULL`
- `raw_company_name = "UNKNOWN LEGACY HOLDINGS PLC"` (exercises the new
  F-011 schema field from HO-045 §4)
- `lifecycle_status = 'unresolved'`
- `claim_status = 'pending'`
- `claim_reference = 'AT005-TEST-001'`

## Acceptance Criteria (Gherkin)

### AC-01 — Claims list does not crash with a null holding

```gherkin
Given a claim record exists with holding_id = NULL and raw_company_name set
When an ADMIN loads the /settings/claims (or equivalent) page
Then the page renders without a JavaScript error or blank screen
And the claim row appears in the list
```

### AC-02 — Company/registrar columns degrade gracefully

```gherkin
Given the seeded null-holding claim from AC-01
When the claims table renders that row
Then the Company column displays raw_company_name ("UNKNOWN LEGACY HOLDINGS PLC")
  instead of a blank cell or "undefined"
And the Registrar column displays a placeholder (e.g. "—" or "Unmatched")
  instead of a blank cell or "undefined"
And the Shares column displays a placeholder instead of throwing on
  holding.num_shares access
```

### AC-03 — Detail drawer opens without error

```gherkin
Given the seeded null-holding claim from AC-01
When an ADMIN clicks the row to open the claim detail drawer
Then the drawer opens without a JavaScript error
And displays raw_company_name where a matched company name would normally show
And does not attempt to render a null holding's shares/ticker fields directly
```

### AC-04 — Filtering and search still work

```gherkin
Given the seeded null-holding claim from AC-01, alongside existing matched claims
When an ADMIN filters by lifecycle_status = "Unresolved"
Then the null-holding claim appears in the filtered results
When an ADMIN searches by claim_reference "AT005-TEST-001"
Then the null-holding claim appears in the search results
```

### AC-05 — Registrar filter does not exclude or crash on null holding

```gherkin
Given the seeded null-holding claim from AC-01
When an ADMIN applies a Registrar filter for any specific registrar
Then the null-holding claim is correctly excluded from that filtered view
  (it has no registrar) without throwing an error
When an ADMIN clears the Registrar filter
Then the null-holding claim reappears in the unfiltered list
```

## Pass Threshold

5/5 AC must pass. This is a hard prerequisite — F-011 implementation
should not begin frontend integration until AT-005 is green, since F-011
is the feature that will generate these rows in production.

## Notes for Hermes

- `raw_company_name` and nullable `holding_id` already exist per HO-046 §2
  — no further schema work needed for this test.
- If AC-02/03 fail because the frontend code assumes `holding` is always
  present (e.g. `holding.company_name` without an optional chain), the fix
  is straightforward: add `holding?.company_name ?? claim.raw_company_name`
  style fallbacks at each access point rather than a broader refactor.

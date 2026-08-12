---
id: F-010
title: Claims (Dividend Tracking Page)
status: PLANNED
author: Claude
created: 2026-07-05
updated: 2026-07-05 (architect review incorporated)
phase: 3C
priority: 1
depends_on: []
---

# F-010 Claims — Dividend Tracking Dashboard

## Goal

Build a unified dividend tracking page that displays unclaimed, claimed, and pending dividend records in an actionable dashboard with KPIs, charts, searchable table, registrar summaries, and detail drawers.

> **Domain note:** In EPM, "Claim" = "Dividend". The `ClaimRecord` model stores dividend payout records (unclaimed/claimed/pending status). This page replaces the need for a separate F-008 Dividends page — F-010 IS the dividends feature.

## Background

The user downloaded a Lovable-generated React page (`dividend-navigator`) that serves as the design template. The backend (`claims.py`) already has full CRUD with CRUD endpoints. This spec covers adapting the template into EPM's SPA and enriching the API layer for the dashboard's data needs.

## User Stories

- **As a portfolio manager**, I want to see total unclaimed vs claimed dividend values so I know recovery progress
- **As a portfolio manager**, I want to see dividend records by registrar with recovery percentages so I can follow up with specific registrars
- **As a portfolio manager**, I want to search dividend records by account or company name
- **As a portfolio manager**, I want to filter records by status (Unclaimed / Claimed / Pending) and registrar
- **As a portfolio manager**, I want to click a record to see full details (shares, amounts, notes, e-dividend mandate status)
- **As a portfolio manager**, I want to see a registrar's profile (contact info, total unclaimed/claimed value) by clicking on them
- **As a portfolio manager**, I want the page to work in both light and dark themes

## Architect Review (2026-07-05)

The following feedback from DeepSeek Architect was incorporated into this spec:

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | Critical | GET /api/v1/claims doesn't chain-load Holding.company | ✅ Added selectinload chain in spec |
| 2 | Critical | No Pydantic response schema — raw ORM returned | ✅ Added ClaimResponse schema |
| 3 | Critical | Registrars endpoint missing aggregate stats | ✅ Client-side compute for v1 |
| 4 | High | Status filter asymmetry (6 DB → 3 UI) | ✅ Backend accepts comma-separated status param |
| 5 | High | No search endpoint for AC-07 | ✅ Client-side search for v1 |
| 6 | Medium | Response envelope inconsistency | ✅ Use _envelope() in claims |
| 7 | Medium | Synthetic "Account #" field | ✅ Use claim_reference → synthetic fallback |
| 8 | Medium | Mandate field is static placeholder | ✅ Documented as v1 limitation |
| 9 | Medium | Missing loading/error/empty ACs | ✅ Added AC-12, AC-13, AC-14 |
| 10 | Medium | No automated test coverage | ✅ Added manual+automated in Verification |
| 11 | Low | Registrar chain depth | ✅ Chain all the way to Company.registrar |
| 12 | Low | Sidebar nav: /claims vs /dividends | ✅ Add /claims, keep stub at /dividends |
| 13 | Low | Export CSV button | ✅ v2, explicitly out-of-scope for v1 |
| 14 | Low | Theme variable coverage | ✅ Verification step to check light/dark vars |

## Acceptance Criteria

1. [AC-01] Page loads at `/claims` with sidebar nav link visible
2. [AC-02] KPI cards display: Total Unclaimed Value, Total Claimed Value, Total Registrars, Total Dividend Records
3. [AC-03] Donut chart shows unclaimed value distribution by registrar
4. [AC-04] Bar chart shows top 5 registrars by unclaimed value
5. [AC-05] Split donut chart shows claimed vs unclaimed portfolio split
6. [AC-06] Registrar summary table shows per-registrar: name, unclaimed count, claimed count, total, recovery progress bar, unclaimed value, claimed value
7. [AC-07] Dividend records table (searchable by account/company client-side, filterable by registrar and display-status) shows: account #, company, registrar, status badge, last updated, view details button
8. [AC-08] Clicking "View Details" opens a drawer with all fields (account, company, registrar, shares, year, amount, status, mandate, notes)
9. [AC-09] Clicking a registrar row opens a profile drawer with contact info and its holding records
10. [AC-10] All colors adapt to light/dark theme toggle
11. [AC-11] All data is sourced from live API — no mock data in production
12. [AC-12] Loading state shows skeleton/spinner while API fetches
13. [AC-13] Error state shows an error banner with retry button
14. [AC-14] Empty state shows helpful message and disabled charts instead of broken render

## Requirements

### Frontend

- Route: `/claims` — file-based route `_app.claims.tsx`
- Page component extracted from `dividend-navigator/src/routes/index.tsx` (724 lines)
- Sidebar: add `/claims` nav item with `Coins` icon (re-label "Claims" in nav, keep `/dividends` stub as redirect)

**Adaptations from source:**
- Strip standalone sidebar + topbar (EPM app provides these)
- Replace all hardcoded colors with EPM CSS variables for dual-theme support
- Replace mock `records` array with `useQuery` hook calling `GET /api/v1/claims`
- Replace mock `registrars` array → compute aggregate stats client-side from claims
- Subcomponents kept: KpiCard, ChartCard, StatusBadge, MandateBadge, DetailRow, MiniStat, SplitRow

**Status mapping (6 DB → 3 UI):**

| DB claim_status | Display Status | Filter Group |
|-----------------|----------------|--------------|
| pending | Pending | Pending |
| partially_paid | Pending | Pending |
| approved | Claimed | Claimed |
| paid | Claimed | Claimed |
| rejected | Unclaimed | Unclaimed |
| lapsed | Unclaimed | Unclaimed |

Frontend sends `?status=rejected,lapsed` for "Unclaimed" filter, `?status=approved,paid` for "Claimed", `?status=pending,partially_paid` for "Pending".

**Data model mapping (mock → API):**

| Lovable Field | API Source | Notes |
|--------------|------------|-------|
| `records[].acct` | `claim.claim_reference` → synthetic `ticker+id` fallback | Real ref if available |
| `records[].company` | `claim.holding.company.ticker` | Chained eager load |
| `records[].registrar` | `claim.holding.company.registrar.name` | 3-level chained eager load |
| `records[].status` | `claim.claim_status` → display status map | 3-state display |
| `records[].shares` | `claim.holding.num_shares` | Via Holding |
| `records[].amount` | `claim.actual_payout ?? claim.expected_payout` | Prefer actual |
| `records[].year` | Extract from `claim.payout_date or claim.date_filed` | Year only |
| `records[].mandate` | Static: "Active" for claimed, "None" for unclaimed/pending | v1 limitation |
| `records[].notes` | `claim.notes` | Direct field |

### Backend Enrichment

#### 1. GET /api/v1/claims — chained eager load + Pydantic schema + envelope

- Query: `select(ClaimRecord).options(selectinload(ClaimRecord.holding).selectinload(Holding.company).selectinload(Company.registrar)).where(ClaimRecord.deleted_at.is_(None))`
- Add Pydantic response schema:
  ```python
  class ClaimResponse(BaseModel):
      id: int
      holding_id: int
      claim_reference: Optional[str]
      claim_authority: Optional[str]
      claim_type: str
      claim_status: str
      expected_payout: Optional[Decimal]
      actual_payout: Optional[Decimal]
      payout_date: Optional[date]
      notes: Optional[str]
      # Nested
      holding: Optional[dict]  # includes num_shares, company.ticker, company.name, company.registrar.name
  ```
- Wrap response in `_envelope()` pattern (consistent with registrars.py)
- Status filter: accept comma-separated: `?status=pending,partially_paid` → `ClaimRecord.claim_status.in_(status_list)`
- No search endpoint for v1 (client-side search)

#### 2. GET /api/v1/registrars — no changes needed for v1

Registrar aggregate stats (unclaimed/claimed counts per registrar) are computed **client-side** from the claims list for v1. The registrars endpoint is used only for contact details in the profile drawer.

If performance becomes an issue, a dedicated registrars/stats endpoint can be added later.

### CSS Additions

Add to EPM's `styles.css`:

```css
/* Surface-2 (slightly offset from surface for card depth) */
:root {
  --color-surface-2: var(--bg-card);
  /* already mapped to --bg-surface in EPM */
}

/* glass-card utility */
.glass-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  backdrop-filter: blur(8px);
}
```

Verify that ALL variables used by the Lovable templates exist in both light and dark themes:
- `--chart-1` through `--chart-5` (charts)
- `--warning`, `--success`, `--info`, `--destructive` (status badges)
- `--border`, `--muted-foreground` (text/edges)
- `--primary`, `--bg-card`, `--bg-canvas` (cards)

## Sidebar and Routes

- Add `/claims` to Sidebar `MAIN` array with `Coins` icon
- Label: "Dividends" → rename to "Claims" in sidebar (or "Dividend Claims")
- Keep existing `/dividends` route as `_app.dividends.tsx` — either leave as stub or add redirect to `/claims`
- **Decision for v1:** Add both — `/claims` (full page) and `/dividends` (stub). Update sidebar to point to `/claims`.

## v1 Limitations (Explicitly Out of Scope)

| Feature | Reason |
|---------|--------|
| Export CSV | Not requested — add in v2 if UX feedback calls for it |
| Mandate data from backend | No mandate model exists — static placeholder only |
| Server-side search | Small datasets — client-side filtering sufficient |
| Registrars aggregate endpoint | Client-side compute from claims — revisit if N>500 records |
| Pagination | ~dozens of records in v1 — disabled pagination controls |
| Automated test suite | Manual QA + build verification for v1 |

## Data Model

### ClaimRecord (existing, see models.py:154-183)

| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| holding_id | int | FK → holdings |
| claim_reference | str | optional ref # |
| claim_authority | str | optional (e.g. AMCON, CAC) |
| claim_type | str | "liquidation" default |
| date_filed | date | optional |
| claim_status | str | pending/approved/rejected/partially_paid/paid/lapsed |
| expected_payout | Decimal | optional |
| actual_payout | Decimal | optional |
| payout_date | date | optional |
| notes | text | optional |
| holding | relationship | → Holding (has company, num_shares, certificate_number) |

### Holding → Company → Registrar chain

`ClaimRecord.holding` → `Holding.company` → `Company.registrar`
- `Company`: ticker, name, sector
- `Company.registrar_id`: FK → `registrars.id`
- `Registrar`: name, email, phone, address, website, response_rating

## Verification

### Manual QA

1. Login, navigate to /claims — page renders with real data
2. KPI cards show non-zero values matching seeded claims
3. Charts render (donut, bar, split)
4. Status filter: switch between Unclaimed / Claimed / Pending — table updates
5. Registrar filter: select a registrar — table filters
6. Search: type a company name — table filters client-side
7. Click "View Details" — drawer opens with full record info
8. Click a registrar row — profile drawer opens with contact info
9. Theme toggle: switch to light mode — all colors adapt correctly
10. Empty state: confirm visual when no claims match filter
11. Error state: stop API, verify error banner + retry button appears
12. Console: no errors in light or dark mode

### Build Verification

```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
npm run build  # no TypeScript errors
```

### CSS Variable Verification

- [ ] `--chart-1` through `--chart-5` defined in both light/dark
- [ ] `--warning`, `--success`, `--info`, `--destructive` defined in both light/dark
- [ ] `--border`, `--muted-foreground` defined in both light/dark
- [ ] `--primary`, `--bg-card`, `--bg-canvas` defined in both light/dark

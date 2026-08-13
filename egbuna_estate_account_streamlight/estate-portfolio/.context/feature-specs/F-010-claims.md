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

Build a unified dividend tracking page that displays dividend records in 3 states (unresolved, unclaimed, claimed) in an actionable dashboard with KPIs, charts, searchable table, registrar summaries, detail drawers, and a document upload widget shared with the Registrars page.

> **Domain note:** In EPM, "Claim" = "Dividend". The `ClaimRecord` model stores dividend payout records. This page replaces the need for a separate F-008 Dividends page — F-010 IS the dividends feature.

## Dividend State Definitions (3-State Model)

| State | Definition | Transition Trigger |
|-------|------------|-------------------|
| **Unresolved** | Dividend declared by registrar, but administrators have NOT yet met requirements to claim (missing docs, signatures, board resolutions, etc.) | Admin marks requirements as "met" → transitions to **Unclaimed** |
| **Unclaimed** | All admin requirements met, dividend is claimable, but funds NOT YET paid into estate's bank account | Funds received in estate bank account → transitions to **Claimed** |
| **Claimed** | Dividend has been paid into the estate's bank account | Terminal state |

> **Note:** "Unresolved + Unclaimed" = dividend declared but admin work incomplete. "Unclaimed" alone = ready to claim but not yet paid. "Claimed" = money in bank. These are distinct from the legacy `claim_status` enum (pending/approved/paid/rejected/lapsed/partially_paid) — the 3-state model is the UI display layer mapping over the underlying enum.

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
| 4 | High | Status filter asymmetry (6 DB → 3 UI) | ✅ Backend accepts comma-separated status param, updated to 3-state model |
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

**Additional updates from user feedback (2026-07-05):**
- 3-state dividend model (Unresolved/Unclaimed/Claimed) replacing legacy 3-state (Pending/Unclaimed/Claimed)
- Document Upload Widget shared between Claims and Registrars pages
- Requirements Checklist in detail drawer for Unresolved dividends
- State transition endpoints (requirements_met, mark_claimed)
- ClaimDocument model for document management

## Acceptance Criteria

1. [AC-01] Page loads at `/claims` with sidebar nav link visible
2. [AC-02] KPI cards display: Total Unresolved Value, Total Unclaimed Value, Total Claimed Value, Total Registrars, Total Dividend Records
3. [AC-03] Donut chart shows unresolved/unclaimed/claimed value distribution by registrar
4. [AC-04] Bar chart shows top 5 registrars by unresolved value
5. [AC-05] Split donut chart shows claimed vs (unresolved + unclaimed) portfolio split
6. [AC-06] Registrar summary table shows per-registrar: name, unresolved count, unclaimed count, claimed count, total, recovery progress bar, unresolved value, unclaimed value, claimed value
7. [AC-07] Dividend records table (searchable by account/company client-side, filterable by registrar and display-status: Unresolved/Unclaimed/Claimed) shows: account #, company, registrar, status badge, last updated, view details button
8. [AC-08] Clicking "View Details" opens a drawer with all fields (account, company, registrar, shares, year, amount, status, mandate, notes) + **Requirements Checklist** (checkboxes for admin requirements) + **Document Upload Widget** (drag-drop PDF/CSV, list uploaded docs) + **State Transition Buttons** (Mark Requirements Met → Unclaimed; Mark Claimed → Claimed)
9. [AC-09] Clicking a registrar row opens a profile drawer with contact info, its holding records, and Document Upload Widget showing all documents for that registrar
10. [AC-10] All colors adapt to light/dark theme toggle
11. [AC-11] All data is sourced from live API — no mock data in production
12. [AC-12] Loading state shows skeleton/spinner while API fetches
13. [AC-13] Error state shows an error banner with retry button
14. [AC-14] Empty state shows helpful message and disabled charts instead of broken render
15. [AC-15] Registrars page has a "Documents" card widget showing all docs for that registrar, with upload/download/delete functionality
16. [AC-16] Document upload accepts only PDF/CSV, max 10MB, shows progress and error handling
17. [AC-17] State transitions: Unresolved → Unclaimed (via "Mark Requirements Met" button in drawer), Unclaimed → Claimed (via "Mark Claimed" button in drawer), no backward transitions
18. [AC-18] Requirements Checklist visible for Unresolved records, hidden for Unclaimed/Claimed

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

**Document Upload Widget (Shared with Registrars Page):**
- A reusable card/widget component for uploading dividend-related documents (PDF/CSV)
- Uploaded documents are linked to both:
  1. The specific `ClaimRecord` (dividend)
  2. The `Registrar` (for registrar-level document management)
- Accepted formats: `.pdf`, `.csv` only
- Upload endpoint: `POST /api/v1/claims/{claim_id}/documents` (backend to be added)
- Widget displays: upload area, list of uploaded docs with type icons, download/delete actions
- On Registrars page: same widget shows ALL documents for that registrar across all their claims
- On Claims page: widget shows documents for the specific claim record (in detail drawer or inline)

**Claim Detail Drawer Enhancements:**
- Add "Requirements Checklist" section for Unresolved dividends
- Checklist items (configurable per registrar or generic): Board Resolution, Signatures, Certificate, Indemnity Form, Tax Clearance
- "Mark Requirements Met" button (only for Unresolved) → transitions to Unclaimed
- "Mark Claimed" button (only for Unclaimed) → transitions to Claimed (records payout date + actual amount)
- Document upload widget embedded in drawer for easy attachment

**Status mapping (6 DB → 3 UI Display States):**

The underlying `claim_status` enum (6 values) maps to 3 display states:

| DB claim_status | Display State | Filter Group | Notes |
|-----------------|---------------|--------------|-------|
| pending | Unresolved | Unresolved | Admin work not started |
| partially_paid | Unresolved | Unresolved | Partial work done, requirements not met |
| approved | Unclaimed | Unclaimed | Requirements met, awaiting payment |
| paid | Claimed | Claimed | Money in bank |
| rejected | Unresolved | Unresolved | Rejected by registrar, needs re-work |
| lapsed | Unresolved | Unresolved | Expired, may need re-filing |

**Transition Logic:**
- **Unresolved → Unclaimed**: Admin marks all requirements as met (via checkboxes in detail drawer)
- **Unclaimed → Claimed**: Admin confirms funds received in estate bank account (via "Mark Claimed" button)
- **Unresolved** covers: pending, partially_paid, rejected, lapsed — these all mean "admin action required"
- **Unclaimed** covers: approved — ready to claim, just waiting for payment
- **Claimed** covers: paid — terminal state, money received

Frontend sends `?status=pending,partially_paid,rejected,lapsed` for "Unresolved" filter, `?status=approved` for "Unclaimed", `?status=paid` for "Claimed".

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

### Requirements Checklist (per claim record)

For **Unresolved** records, the detail drawer shows a checklist of admin requirements that must be met before transitioning to Unclaimed:

| Requirement | Description | Required For |
|-------------|-------------|--------------|
| Board Resolution | Board resolution authorizing claim | All |
| Indemnity Form | Signed indemnity form | All |
| Death Certificate | If applicable (deceased shareholder) | Deceased estates |
| Probate/Letters of Admin | Court documents | Deceased estates |
| Share Certificate | Original share certificate(s) | All |
| ID Verification | Valid ID of claimant(s) | All |
| Bank Account Details | Estate bank account verification | All |
| Registrar-Specific Form | Registrar's claim form | Registrar-dependent |

- Checkboxes are editable by Admin role only (Readonly role sees read-only view)
- "Mark Requirements Met" button only enabled when ALL required checkboxes are checked
- Clicking "Mark Requirements Met" transitions state: `Unresolved` → `Unclaimed` (updates `claim_status` from `pending/partially_paid/rejected/lapsed` → `approved`)

### Document Upload Widget (Shared Component)

Reusable component used in:
1. **Claims Page** — Detail drawer (per-claim documents)
2. **Registrars Page** — Documents card widget (per-registrar documents across all claims)

**Features:**
- Drag-and-drop zone + click to browse
- Accepts: PDF (`application/pdf`), CSV (`text/csv`)
- Max file size: 10MB
- Shows upload progress bar
- On success: adds document to list with type icon (PDF/CSV), filename, size, upload date, download/delete actions
- Delete: soft delete (admin only), confirmation dialog
- Download: streams file from backend
- Per-claim documents filter by claim_id; Registrar documents filter by registrar_id

**Frontend State:**
- Local state for upload queue, progress, errors
- TanStack Query mutation for upload/delete
- Invalidates `['claims', claimId]` and `['registrars', registrarId]` queries on success

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
- Status filter: accept comma-separated: `?status=pending,partially_paid,rejected,lapsed` → `ClaimRecord.claim_status.in_(status_list)`
- No search endpoint for v1 (client-side search)

#### 2. POST /api/v1/claims/{claim_id}/documents — Document Upload

- Accepts multipart/form-data with file (PDF or CSV)
- Saves file to `uploads/claims/{claim_id}/` with sanitized filename
- Creates `ClaimDocument` record linking to `claim_id` and `registrar_id` (via holding.company.registrar)
- Returns document metadata: id, filename, mime_type, size, uploaded_at, download_url
- Validates: file type (application/pdf, text/csv), max size (10MB)

#### 3. GET /api/v1/claims/{claim_id}/documents — List Documents for Claim

- Returns list of `ClaimDocument` records for the claim
- Used by Claims page detail drawer

#### 4. GET /api/v1/registrars/{registrar_id}/documents — List Documents for Registrar

- Returns list of `ClaimDocument` records where registrar_id matches (via claim.holding.company.registrar)
- Used by Registrars page document widget

#### 5. DELETE /api/v1/claims/{claim_id}/documents/{doc_id} — Delete Document

- Soft delete (sets deleted_at) or hard delete based on policy
- Only accessible to admin role

#### 6. POST /api/v1/claims/{claim_id}/transition — State Transition

- Body: `{ "transition": "requirements_met" | "mark_claimed" }`
- Validates current state allows transition:
  - `requirements_met`: only from Unresolved states (pending, partially_paid, rejected, lapsed) → sets claim_status = 'approved'
  - `mark_claimed`: only from Unclaimed state (approved) → sets claim_status = 'paid', actual_payout = expected_payout (or provided), payout_date = today
- Returns updated claim record
- Requires admin role

#### 7. GET /api/v1/registrars — no changes needed for v1

Registrar aggregate stats (unresolved/unclaimed/claimed counts per registrar) are computed **client-side** from the claims list for v1. The registrars endpoint is used only for contact details in the profile drawer.

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
| Requirements Checklist config per registrar | Generic checklist for v1; per-registrar config in v2 |
| Document versioning/history | Single upload per doc for v1; versioning in v2 |
| Bulk state transitions | One-at-a-time for v1; bulk actions in v2 |
| Email notifications on state change | Not in v1 scope |

## Data Model

### ClaimDocument (new model for document upload)

| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| claim_id | int | FK → claim_records |
| registrar_id | int | FK → registrars (denormalized for query perf) |
| filename | str | Original filename |
| stored_filename | str | Sanitized filename on disk |
| mime_type | str | application/pdf or text/csv |
| file_size | int | Bytes |
| file_path | str | Relative path: uploads/claims/{claim_id}/{stored_filename} |
| uploaded_at | datetime | Auto timestamp |
| deleted_at | datetime | Soft delete |

Relationships:
- `ClaimDocument.claim` → `ClaimRecord` (many-to-one)
- `ClaimDocument.registrar` → `Registrar` (many-to-one, denormalized)

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

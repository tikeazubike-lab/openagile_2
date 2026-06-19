# DECISIONS.md

## Authentication

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Auth mechanism | JWT httpOnly cookie, 30-day | Traefik BasicAuth | No roles, no remember-me, redeploy to change password |
| Token storage | httpOnly cookie | localStorage | Security — XSS cannot steal cookie |
| Session length | 30-day persistent | Session-only | Daily-use personal app — re-login friction unacceptable |
| Password hashing | bcrypt==4.0.1 + passlib 1.7.4 | bcrypt >= 4.1.0 | passlib breaks with newer bcrypt (removed __about__ module) |
| Auth framework | Custom FastAPI deps.py | Streamlit-authenticator | Phase 2 is FastAPI, not Streamlit |

## Frontend Architecture

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Frontend framework | React 18 + TypeScript | Streamlit (v1), Vue.js | Mobile UX ceiling on Streamlit; Vue only for Frappe apps |
| Routing | TanStack Router (file-based) | React Router v6 | TanStack Start chosen by Lovable; file-based routing cleaner |
| Server state | TanStack Query v5 | SWR, Redux | Best invalidation model for multi-page cache updates |
| UI state | Zustand | Redux, Context API | Minimal boilerplate, sufficient for editMode + authStore |
| Tables | TanStack Table v8 | AG Grid, react-table v6 | Same ecosystem, column virtualization available |
| CSS | Tailwind v4 + oklch tokens | Hardcoded hex, CSS modules | Theme switching requires CSS variables, not hex |
| No Supabase | Banned entirely | Supabase client | Lovable default — violates self-hosted constraint |

## Data Model

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Holding classification | holding_type: active / claim | Single table, status filter only | Visual separation essential (two tables in UI) |
| Claims cost basis | cost_basis_override = 0 | Original purchase price | Claims are administrative, not investment positions |
| Soft delete | deleted_at = datetime.now(timezone.utc) | Hard delete | Audit trail, restore capability |
| Monetary storage | Decimal in DB, string in API | Float everywhere | JS float precision loss on financial data |
| Draft/publish | Status column on holdings | Session-based preview | Streamlit session fragility; persistent draft = correct pattern |
| Companies scope | NGX-specific Company model | Generic Asset model | Premature abstraction — extend in Phase 4 |
| Multi-portfolio | user_id FK on all financial tables | Global portfolio assumption | Future-proof for Phase 4 without schema migration |

## Price Data

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Primary price source | NGX Daily Official List PDF (manual upload) | EODHD (402 error), Stooq (no NGX coverage) | Only reliable source for XNSA |
| PDF parsing strategy | Right-to-left column extraction + fuzzy name match | Table extraction (pdfplumber.extract_tables) | NGX PDFs use borderless tables; column count varies by format |
| Dual format support | Daily Official List + Gainers & Losers (column heuristics) | Single format assumption | NGX publishes multiple PDF types |
| CSV format | ticker,price,date (3 columns, no source column) | ticker,price,date,source | Source recorded server-side; Stooq-compatible format |
| Historical ingestion | Manual daily PDFs now; batch endpoint Phase 3C | Automated scraper | NGX has no free API; scraper fragile |
| Price audit | price_audit table with old/new/source/revert | No audit | Revert capability required; data quality critical |

## Infrastructure

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Deployment | GitHub Actions SSH to VPS | Local docker compose | Local workstation OOM crashes; CI is the only safe path |
| Container strategy | Single container (FastAPI + React static) | Separate frontend container | Simpler deployment; no CORS; FastAPI serves static files |
| Database | Shared openagile_postgres | New postgres per service | Resource efficiency; "spin up another" anti-pattern |
| SSL | Traefik + Let's Encrypt | Manual nginx SSL | Auto-renewal, Docker-native |
| File storage | Local volume ./uploads | S3, Google Drive | Self-hosted constraint; no external dependencies |
| SSH heredoc | Quoted << 'ENDSSH' | Unquoted << ENDSSH | Unquoted interpolates variables on runner not server (bug confirmed in production) |
| Frontend hotfix build | docker compose build --no-cache epm | Regular build | Vite NodeJS stage caches .tsx changes — stale builds confirmed |

## Testing

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| BDD framework | Standard pytest + traceability comments | pytest-bdd | pytest-bdd requires live .feature files at runtime; adds complexity |
| Test isolation | Separate schema estate_portfolio_test | Separate postgres container | No new containers; schema creation/teardown by CI job |
| Test location | Tests in repo (reinstated) | Gitignored epm-tests/ | CI cannot run tests not in repo — Option B was an anti-pattern |
| Gherkin .feature files | Documentation in docs/testing/ | Runtime test files | Specs are design artifacts; pytest functions are the executable tests |
| AT naming | AT-003, AT-003-1, AT-003-2 | Mutating AT-003 in place | Full audit trail — original run is immutable historical record |

## Document Governance

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Wiki | docs/README.md in repo | GitHub Wiki | Free GitHub account — Wiki and branch protection disabled |
| Document identity | Type badge in header (BR/ADR/TC/AT/HO) | Folder location only | Type visible at open regardless of file location |
| Archiving | Copy to archived/ with date suffix | Delete or overwrite | Nothing deleted — everything traceable |
| Handover naming | HO-001 sequential | Arbitrary names | Chronological audit trail across all agents |

## Registrar Documents

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Document scope | Per-registrar requirements | Per-company-registrar pair | Requirements apply registrar-wide (not per holding) |
| File versioning | Multiple rows per requirement (latest shown) | Replace in place | History needed for rejected/resubmitted documents |
| Storage path | Structured: {registrar_id}/{req_id}/{timestamp}_{filename} | Flat directory | Collision-free, human-browsable, maps to DB hierarchy |
| File type validation | Magic-byte check + MIME type | MIME type only | Browser can spoof MIME; magic bytes verify actual content |

## Holdings UX

| Decision | Choice | Rejected | Reason |
|----------|--------|----------|--------|
| Add Holding UI | Slide-out drawer (420px) | Inline table row | Inline row is clunky (AT-003 feedback); drawer allows table to remain visible |
| Inline editing | Child component InlineEditRow | Parent table state | Parent re-renders on every keystroke, causing cursor jump |
| Holdings display | Two separate tables (Active + Claims) | Single table with filter | Visual distinction essential; subtotals per category required |
| Delete confirmation | Modal confirmation dialog | Immediate delete | Soft delete is irreversible from user perspective until restore |


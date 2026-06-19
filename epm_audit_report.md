# EPM Codebase Audit Report

**Project:** Estate Portfolio Manager (EPM)  
**Root:** `/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/`  
**Date:** 2026-06-15

---

## 1. Full File Tree (excluding .git, node_modules, __pycache__, venv, migrations/versions, dist, build)

```
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/app.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/env.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic.ini
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/script.py.mako
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/001_create_users_table.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/3f4739d78390_phase_2b_updates.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/4a8f2c1d9e05_phase_3a_price_audits.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/5b9c3e2f4a16_add_registrars_documents_tables.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/6c0d4f3e5b27_registrar_contact_fields.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/alembic/versions/__init__.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/config.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/database.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/deps.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/__init__.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/main.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/models.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/auth.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/claims.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/companies.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/dashboard.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/holdings.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/__init__.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/obsidian.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/prices.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/routers/registrars.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/app/services/portfolio.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/.gitignore
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/requirements.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/scripts/import_obsidian.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/scripts/__init__.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/scripts/seed_admin.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/scripts/seed_ngx_companies.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/conftest.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/contract/test_api_contract.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/db/test_schema_integrity.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/conftest.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/test_auth_integration.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/test_br001_gherkin.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/test_holdings_integration.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/test_prices_integration.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/integration/test_registrars_integration.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/performance/locustfile.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_api_routes.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_auth_logic.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_auth_router.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_business_logic.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_deps.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_holdings_router.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_pydantic_schemas.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backend/tests/unit/test_seed_admin.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backups/pre_migration_20260411.sql
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/CHANGELOG.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/CONTRIBUTING.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/create_tests.sh
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/cron.log
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.cursor/rules/backend.mdc
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.cursor/rules/frontend.mdc
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.cursor/rules/general.mdc
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.cursor/rules/infrastructure.mdc
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/deploy.sh
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/Dialin-—-Analytics-Dashboard-UI-by-Orix-Creative-on-Dribbble.png
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docker-compose.v2.yml
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docker-compose.yml
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/Dockerfile
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/Dockerfile.v2
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/architecture/ADR-001-single-container.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/architecture/ADR-002-shared-postgres.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/architecture/ADR-003-jwt-httponly-cookie.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/architecture/ADR-004-ngx-pdf-parser.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/architecture/ADR-005-local-volume-storage.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/archive/ (16 files)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/context/ (6 files)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/handover/ (14 files: HO-005 through HO-018)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/onboarding/ (2 files: OB-001, OB-002)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/README.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/requirements/ (7 files: BR-001 through BR-005 + 2 specs)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/testing/acceptance-tests/ (8 files)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/testing/features/ (5 files)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/docs/testing/STLC-v1.0.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.env
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.env.example
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.env.v2
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.env.v2.example
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/epm-tests/ (duplicate test tree)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/ (React SPA)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/extract_tickers_from_txt.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/extract_tickers.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.github/ISSUE_TEMPLATE/bug_report.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.github/ISSUE_TEMPLATE/feature_request.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.github/PULL_REQUEST_TEMPLATE.md
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/init_db.sql
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/ngx_companies_list.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/NigerianStocks/ (Obsidian vault)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/requirements.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/scripts/import_obsidian.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/scripts/ngx_scraper.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/scripts/rapidapi_scraper.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/scripts/test_apis.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/scripts/yfinance_scraper.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/setup.sh
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/temp_daily.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/temp_prices1.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/temp_prices2.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/test_pdf.py through test_pdf8.py (8 files)
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/test_regex.py, test_regex2.py, test_regex3.py
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/tickers.txt
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/uploads/registrar_documents/13/1/20260506_044157_new-full-demat-form.pdf
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/uploads/registrar_documents/13/2/20260506_050219_Veritas-Registrars-Find-A-Branch.png
/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/uploads/registrar_documents/1/4/20260509_022228_Veritas-Registrars-Find-A-Branch.png
```

---

## 2. Backend Python Files with Line Counts

```
 6850 total
  620 backend/app/routers/prices.py
  579 backend/app/routers/registrars.py
  562 backend/tests/integration/test_br001_gherkin.py
  374 backend/app/models.py
  317 backend/tests/db/test_schema_integrity.py
  297 backend/tests/unit/test_api_routes.py
  262 backend/tests/unit/test_pydantic_schemas.py
  261 backend/scripts/import_obsidian.py
  259 backend/tests/integration/test_prices_integration.py
  246 backend/app/routers/holdings.py
  225 backend/tests/unit/test_business_logic.py
  220 backend/tests/integration/conftest.py
  213 backend/tests/contract/test_api_contract.py
  211 backend/tests/integration/test_holdings_integration.py
  210 backend/scripts/seed_ngx_companies.py
  192 backend/tests/performance/locustfile.py
  179 backend/tests/unit/test_auth_logic.py
  140 backend/app/routers/dashboard.py
  126 backend/tests/integration/test_auth_integration.py
  124 backend/app/routers/auth.py
  115 backend/app/routers/claims.py
  112 backend/tests/unit/test_seed_admin.py
  108 backend/alembic/versions/3f4739d78390_phase_2b_updates.py
   97 backend/app/main.py
   97 backend/app/deps.py
   77 backend/tests/unit/test_auth_router.py
   68 backend/alembic/versions/5b9c3e2f4a16_add_registrars_documents_tables.py
   67 backend/scripts/seed_admin.py
   59 backend/alembic/env.py
   50 backend/tests/integration/test_registrars_integration.py
   40 backend/app/services/portfolio.py
   40 backend/app/config.py
   40 backend/alembic/versions/4a8f2c1d9e05_phase_3a_price_audits.py
   40 backend/alembic/versions/001_create_users_table.py
   38 backend/alembic/versions/6c0d4f3e5b27_registrar_contact_fields.py
   37 backend/app/routers/companies.py
   35 backend/app/routers/obsidian.py
   35 backend/app/database.py
   34 backend/tests/unit/test_deps.py
   28 backend/tests/unit/test_holdings_router.py
   12 backend/tests/conftest.py
```

---

## 3. Full requirements.txt

```
alembic==1.14.0
asyncpg==0.30.0
bcrypt==4.0.1
cryptography==44.0.0
fastapi==0.115.6
httpx==0.28.1
jsonschema==4.23.0
passlib==1.7.4
pydantic==2.10.3
pydantic-settings==2.7.0
pytest==8.4.1
pytest-asyncio==1.3.0
python-frontmatter==1.1.0
pdfplumber==0.11.4
python-jose==3.3.0
python-multipart==0.0.20
SQLAlchemy==2.0.36
uvicorn==0.32.1
```

---

## 4. SQLAlchemy Models Summary

**14 models, 374 lines in backend/app/models.py:**

| Model | Table | Key Fields |
|-------|-------|------------|
| User | users | username, hashed_password, role (admin/readonly), is_active |
| Registrar | registrars | name, email, phone, address, website, response_rating, status |
| RegistrarContactField | registrar_contact_fields | registrar_id, field_type, field_value, sort_order |
| Company | companies | ticker (unique), name, sector, isin, status, current_price, obsidian_slug |
| Holding | holdings | company_id, num_shares, average_cost_basis, holding_type (active/claim), cost_basis_override |
| ClaimRecord | claim_records | holding_id, claim_status, expected_payout, actual_payout, dates |
| ObsidianSyncLog | obsidian_sync_log | run_at, counts (companies/holdings/dividends new/skip), error_details (JSONB) |
| Transaction | transactions | company_id, holding_id, transaction_type, dates, amounts, fees |
| Dividend | dividends | company_id, payment_date, amount_per_share, dividend_type, payment_status, source |
| PriceHistory | price_history | company_id, price_date, OHLC, volume, source |
| PriceAudit | price_audits | company_id, old_price, new_price, changed_at, changed_by, source |
| RegistrarRequirement | registrar_requirements | registrar_id, task_name, document_title, is_required, sort_order |
| RegistrarDocument | registrar_documents | registrar_requirement_id, company_id, file_name, file_path, status |

All models use soft deletes (deleted_at), SQLAlchemy 2.0 Mapped[] annotations, and PostgreSQL-specific types (JSONB, BigInteger).

---

## 5. API Routes — 40 Endpoints Total

| Router | Prefix | Endpoints | Count |
|--------|--------|-----------|-------|
| auth | /api/v1/auth | POST /login, POST /logout, GET /me, POST /change-password | 4 |
| dashboard | /api/v1 | GET /dashboard | 1 |
| holdings | /api/v1 | GET /holdings, POST /holdings, PATCH /holdings/{id}, DELETE /holdings/{id}, POST /holdings/{id}/publish | 5 |
| companies | /api/v1/companies | GET / | 1 |
| prices | /api/v1/prices | GET /, POST /upload-pdf, GET /history/{id}, POST /quick, POST /bulk-csv, GET /audit, POST /audit/{id}/revert | 7 |
| obsidian | /api/v1/obsidian | POST /import, GET /sync-log | 2 |
| claims | /api/v1/claims | GET /, POST /, PUT /{id}, DELETE /{id} | 4 |
| registrars | /api/v1 | GET /registrars, POST /registrars, GET /registrars/{id}, PUT /registrars/{id}, DELETE /registrars/{id}, GET /registrars/{id}/requirements, POST /registrars/{id}/requirements, PUT /registrar-requirements/{id}, DELETE /registrar-requirements/{id}, POST /registrar-requirements/{req_id}/documents, GET /registrar-documents/{doc_id}/download, PUT /registrar-documents/{id}/status, DELETE /registrar-documents/{id}, GET /registrar-requirements/{req_id}/history, POST /registrars/{id}/companies/{id}, DELETE /registrars/{id}/companies/{id} | 16 |

---

## 6. Frontend Routes (19 files in src/routes/)

```
_app.tsx                    (authenticated shell)
_app.companies.tsx
_app.dashboard.tsx
_app.dividends.tsx
_app.holdings.tsx
_app.index.tsx
_app.nav-history.tsx
_app.price-history.tsx
_app.rebalancing.tsx
_app.registrars.tsx
_app.settings.corporate-actions.tsx
_app.settings.data-import.tsx
_app.settings.deleted-records.tsx
_app.settings.price-entry.tsx
_app.settings.users.tsx
_app.transactions.tsx
_app.watchlist.tsx
__root.tsx                  (root: QueryClientProvider, theme, 404)
login.tsx
```

---

## 7. Frontend Components (64 files in src/components/)

**Domain components (17):**
- holdings/AddHoldingDrawer.tsx
- layout/Navbar.tsx, Sidebar.tsx
- registrars/AddRequirementModal.tsx, DocumentHistoryModal.tsx, DocumentUploadModal.tsx, LinkCompanyModal.tsx, RegistrarDetails.tsx, RegistrarList.tsx, RegistrarModal.tsx, RegistrarRequirements.tsx, RegistrarsLayout.tsx, UpdateDocumentStatusModal.tsx
- shared/Badges.tsx, KpiCard.tsx, StubPage.tsx, ToastContainer.tsx

**shadcn/ui components (47):** accordion, alert-dialog, alert, aspect-ratio, avatar, badge, breadcrumb, button, calendar, card, carousel, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, form, hover-card, input-otp, input, label, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, switch, table, tabs, textarea, toggle-group, toggle, tooltip

---

## 8. TanStack Query Hooks (queries.ts)

**Auth:** useLogin(), useLogout()  
**Dashboard:** useDashboard(), useActionItems()  
**Holdings:** useHoldings(), useAddHolding(), useUpdateHolding(), useDeleteHolding(), usePublishHolding()  
**NAV/Rebalancing:** useNavHistory(), useRebalancing() (enabled: false — not yet wired)  
**Prices:** useCompanies(), usePriceAudit(), usePriceHistory(), useQuickPriceUpdate(), useRevertPrice(), useBulkCsvImport(), useUploadNGXPdf()  
**Registrars:** useRegistrars(), useAddRegistrar(), useUpdateRegistrar(), useDeleteRegistrar(), useLinkCompany(), useUnlinkCompany(), useRegistrarRequirements(), useAddRequirement(), useUpdateRequirement(), useDeleteRequirement(), useUploadDocument(), useUpdateDocumentStatus(), useDeleteDocument(), useDocumentHistory()

All hooks use `credentials: "include"` for httpOnly cookie auth. Error envelope parsing handles FastAPI HTTPException bodies. Mutation hooks invalidate related queries on success.

---

## 9. GitHub Actions Workflows

**None.** No `.github/workflows/` directory exists. Deployment is handled by `deploy.sh`.

---

## 10. Docker Compose Files

### docker-compose.yml — Streamlit v1 (estate.zubbystudio.shop:8501)
- Service: `streamlit`, Python 3.11-slim, cron for weekly price scraper
- Traefik HTTPS via Cloudflare, shared `openagile_openagile_network`

### docker-compose.v2.yml — FastAPI+SPA (demo.estate.zubbystudio.shop:8000)
- Service: `epm`, multi-stage Dockerfile (Node 20 build → Python 3.12-slim)
- Same Traefik/network setup, `.env.v2` for environment
- Volumes: NigerianStocks (ro), uploads

---

## 11. Docs Structure

```
docs/architecture/        — 5 ADRs (single-container, shared Postgres, JWT/cookie, PDF parser, local storage)
docs/archive/             — 16 legacy files from 2026-05-23 root cleanup
docs/context/             — AGENT_STATE.yaml, DELEGATION_REGISTRY, MASTER_CONTEXT, PROJECT_STATUS, WORKFLOW, DOCUMENT_MIGRATION_MAP
docs/handover/            — HO-005 through HO-018 (14 handover docs)
docs/onboarding/          — OB-001, OB-002
docs/requirements/        — BR-001 through BR-005 + 2 spec files
docs/testing/             — 8 acceptance tests, 5 feature/BDD files, STLC-v1.0
```

---

## 12. Alembic Migrations (5 total)

```
001_create_users_table.py                    — Phase 2A: User model
3f4739d78390_phase_2b_updates.py           — Phase 2B: Holdings, claims, ObsidianSyncLog, transactions, dividends
4a8f2c1d9e05_phase_3a_price_audits.py      — Phase 3A: PriceAudit model
5b9c3e2f4a16_add_registrars_documents_tables.py — Phase 3B: RegistrarRequirement, RegistrarDocument
6c0d4f3e5b27_registrar_contact_fields.py   — Phase 3B: RegistrarContactField
```

---

## 13. Test Files

**Backend (17 files in backend/tests/):**
- contract/test_api_contract.py
- db/test_schema_integrity.py
- integration/conftest.py, test_auth_integration.py, test_br001_gherkin.py, test_holdings_integration.py, test_prices_integration.py, test_registrars_integration.py
- performance/locustfile.py
- unit/test_api_routes.py, test_auth_logic.py, test_auth_router.py, test_business_logic.py, test_deps.py, test_holdings_router.py, test_pydantic_schemas.py, test_seed_admin.py

**Duplicate tree (15 files in epm-tests/):** Mirrors backend/tests/ minus integration/registrars and integration/confteprices. Adds frontend e2e (4) and unit (5) tests.

**Frontend (9 files in estate-portfolio-manager/tests/):**
- unit/components/: dashboard.test.tsx, holdings.test.tsx, price_history.test.tsx, registrars.test.tsx
- unit/hooks/: useCountUp.test.ts, useTheme.test.ts
- unit/lib/: format.test.ts
- unit/stores/: authStore.test.ts, uiStore.test.ts

**Scattered root-level tests:** test_pdf*.py (8), test_regex*.py (3), scripts/test_apis.py

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Backend Python files | 42 |
| Total backend Python lines | 6,850 |
| API endpoints | 40 |
| SQLAlchemy models | 14 |
| Alembic migrations | 5 |
| Frontend route files | 19 |
| Frontend component files | 64 |
| TanStack Query hooks | 30+ |
| Backend test files | 17 (+ 12 duplicate in epm-tests) |
| Frontend test files | 9 (+ 5 duplicate in epm-tests) |
| Docker Compose files | 2 |
| GitHub Actions workflows | 0 |
| ADR documents | 5 |
| Handover documents | 14 |

# ARCHITECTURE_SPEC.md

## Deployment Architecture
- Platform: Docker Compose (single monorepo)
- Reverse proxy: Traefik v2.10 (SSL via Let's Encrypt, all HTTP/HTTPS through it)
- Network: openagile_network (external bridge, shared across all services)
- Domain: *.zubbystudio.shop
- Staging: demo.estate.zubbystudio.shop
- Production: estate.zubbystudio.shop (pending cutover from legacy Streamlit)
- Server: Netcup VPS, 8 vCPU, 16GB RAM, 500GB SSD, Ubuntu 24.04
- Local: Fedora 42 workstation — edit + commit + push ONLY, zero execution

## Application Stack
- Backend: FastAPI + SQLAlchemy 2.0 async + asyncpg + Alembic
- Frontend: React 18 + TypeScript + Vite + TanStack Router (file-based)
- State: TanStack Query v5 (server) + Zustand (UI)
- Tables: TanStack Table v8
- Charts: Recharts
- Styling: Tailwind v4 + oklch colour tokens
- Components: shadcn/ui (copy-paste pattern, not package dependency)
- Auth: JWT httpOnly cookie, 30-day persistent, SameSite=Strict
- Container: Single Docker container — FastAPI serves React static files via StaticFiles mount

## Database
- Engine: PostgreSQL 15 (shared openagile_postgres container — never create a new one)
- Database: estate_portfolio
- ORM: SQLAlchemy async, all models in single flat models.py
- Migrations: Alembic
- Soft delete: deleted_at = datetime.now(timezone.utc) — never hard delete
- Test isolation: estate_portfolio_test schema (created/torn down by CI)

## Backend Layout
```
backend/app/
  config.py       — settings from env vars
  database.py     — async engine, get_session() [NOT get_db()]
  deps.py         — create_access_token(user_id, role), get_current_user(), require_admin()
  main.py         — FastAPI factory, StaticFiles mount, SPA catch-all
  models.py       — all SQLAlchemy models (flat, single file)
  routers/        — one file per domain
  services/       — business logic (portfolio.py)
  scripts/        — seed_admin.py, seed_ngx_companies.py, import_obsidian.py
```

## Frontend Layout
```
estate-portfolio-manager/src/
  routes/         — TanStack file-based routing (_app.*.tsx protected, login.tsx public)
  store/          — authStore.ts, uiStore.ts
  hooks/          — useTheme.ts, useCountUp.ts
  api/queries.ts  — all TanStack Query hooks
  lib/format.ts   — fmtNaira(), fmtPct() — null-safe, monetary values always strings
  components/     — layout/, holdings/, dashboard/, registrars/, ui/
```

## API Contract Rules
- Response envelope: { data: ..., meta: { total: N }, error: null }
- Monetary values: always strings in responses ("12345.50" not 12345.50)
- Recharts exception: parse strings to floats at component boundary only
- Soft-deleted records: excluded by default, ?include_deleted=true for admin only
- Draft records: excluded from readonly role responses

## Key Pinned Dependencies
- bcrypt==4.0.1 (passlib 1.7.4 incompatible with >= 4.1.0 — DO NOT UPGRADE)
- scipy==1.13.1 (for XIRR computation)
- pdfplumber==0.11.4 (NGX PDF parsing)
- python-frontmatter==1.1.0 (Obsidian vault import)

## Infrastructure Constraints
- Never create new Postgres container
- Never bypass Traefik
- Never use bind mounts for Frappe assets
- Never install packages in system Python (use bench venv for Frappe)
- Always use quoted heredoc in SSH scripts: << 'ENDSSH'
- Docker --no-cache required for frontend hotfixes (Vite stage caches aggressively)

## File Storage (Registrar Documents)
- Volume mount: ./uploads:/app/uploads (bind mount, survives rebuilds)
- Path pattern: uploads/registrar_documents/{registrar_id}/{requirement_id}/{timestamp}_{filename}
- Access: always via authenticated FastAPI endpoint, never direct path exposure
- Allowed types: PDF, JPG, PNG — magic byte validation, not just MIME type
- Max size: 20MB, validated client-side first (instant feedback) + server-side guard

## Obsidian Vault Sync Architecture
- Vault: ~/ObsidianVault/NigerianStocks (local Fedora)
- Sync: git push to private GitHub repo → vault-sync.yml fires → VPS pulls → import_obsidian.py runs ON VPS
- Volume: ~/ObsidianVaultMirror:/vault:ro mounted into backend container
- SSH key: reuse existing VPS key (no new key generation)
- Import rules: INSERT new records only, never UPDATE existing (web app wins after first import)

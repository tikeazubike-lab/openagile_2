# Phase 2 — Architecture Decisions

## What This Phase Produces
- ADR-001 through ADR-00N files in docs/decisions/
- Updated .context/architecture.md with all invariants locked
- Decisions that are hard to reverse — made explicitly now

---

## Questions to Ask (Group 1 — Auth Strategy)

> "Authentication: how will users log in and stay logged in?
>
>   a) JWT in httpOnly cookie (recommended for web apps)
>      — secure against XSS, works across subdomains
>      — session length: how long? (7 days / 30 days / custom)
>   b) JWT in localStorage
>      — simpler but vulnerable to XSS attacks
>   c) Session-based (server-side sessions + cookie)
>   d) No auth — internal tool only
>
> And for passwords:
>   a) bcrypt (recommended — passlib compatible)
>   b) argon2 (newer, more memory-hard)
>   c) No passwords — SSO/OAuth only"

Flag this if they choose localStorage:
> "Note: localStorage JWT is vulnerable to XSS attacks. For a
> production system I recommend httpOnly cookie. Still want localStorage?"

---

## Questions to Ask (Group 2 — Data Model)

> "Three data model decisions that are hard to reverse:
>
> 1. When a user deletes a record, what happens?
>    a) Soft delete — set deleted_at timestamp, keep in DB (recommended)
>       Allows restore, maintains audit trail, referential integrity safe
>    b) Hard delete — permanently removed from DB
>       Simpler queries, no storage accumulation
>
> 2. How are monetary values stored and sent in API responses?
>    a) Decimal in DB + string in API ('12345.50') (recommended)
>       Prevents JavaScript float precision loss at large numbers
>    b) Float/Decimal in DB + float in API
>       Simpler but ₦12,345,678.90 may become ₦12,345,678.900000001
>
> 3. Record IDs:
>    a) Sequential integers (simple, predictable, fast joins)
>    b) UUID (no enumeration, globally unique across systems)
>    c) NanoID / ULID (URL-safe, sortable)"

---

## Questions to Ask (Group 3 — API Contract)

> "API response shape — every endpoint returns the same envelope.
> Which pattern?
>
>   a) OpenAgile standard (recommended):
>      { 'data': ..., 'meta': {'total': N}, 'error': null }
>
>   b) Simple:
>      { 'result': ..., 'count': N }
>
>   c) JSON:API spec:
>      { 'data': [...], 'included': [], 'links': {} }
>
> And for errors — HTTP status codes:
>   - 200: success
>   - 201: created
>   - 400: bad request (validation failed)
>   - 401: not authenticated
>   - 403: authenticated but not authorised
>   - 404: not found
>   - 409: conflict (duplicate)
>   - 422: unprocessable (Pydantic validation)
>   - 500: server error
>
> Any of these you want to change?"

---

## Questions to Ask (Group 4 — Infrastructure)

> "Infrastructure topology — three decisions:
>
> 1. Container strategy:
>    a) Single container (backend serves frontend static files)
>       Simpler deploy, one port, no CORS, less moving parts
>    b) Separate containers (backend API + frontend nginx/caddy)
>       Independent scaling, separate deploys, CORS required
>
> 2. File uploads (user-uploaded files like documents, images):
>    a) Local volume mount (./uploads → /app/uploads in container)
>       Self-hosted, simple backup with rsync, no external dependency
>    b) S3/compatible object storage (MinIO, Cloudflare R2)
>       Scalable, CDN-friendly, external dependency
>    c) No file uploads in this project
>
> 3. Background tasks:
>    a) APScheduler (runs inside FastAPI process, simple)
>    b) Celery + Redis (separate worker process, more complex)
>    c) Cron on the host OS (simplest, outside application)
>    d) No background tasks"

---

## Questions to Ask (Group 5 — Role Model)

> "Roles and permissions — who can do what?
>
> First: how many distinct roles does this system need?
> (Most systems need 2–3. EPM has Admin + ReadOnly. A SaaS might have
> Owner + Member + Guest.)
>
> For each role, tell me:
> - What pages/routes can they access?
> - What operations can they perform (read / create / update / delete)?
> - What is hidden from them entirely?
>
> Where is authorisation enforced?
>   a) Route level (middleware blocks the request)
>   b) Query level (DB query filters by user role)
>   c) Both (recommended — defence in depth)"

---

## Documents to Produce

For each decision group, produce an ADR:

```
ADR-001 — Authentication Strategy
ADR-002 — Data Deletion Strategy
ADR-003 — Monetary Value Serialisation
ADR-004 — API Response Contract
ADR-005 — Infrastructure Topology
ADR-006 — Role Model and Authorisation
```

Then update `.context/architecture.md`:
- Add all locked invariants from the ADRs
- Every invariant is a one-line rule that agents must never violate

Example invariants block:
```
INVARIANTS (rules the system must never violate):
  bcrypt==4.0.1 — DO NOT UPGRADE (passlib incompatibility)
  Soft delete only: deleted_at = datetime.now(timezone.utc)
  Monetary values: always strings in API responses
  JWT in httpOnly cookie — never localStorage
  get_session() not get_db() — session function name
  All deploys via GitHub Actions — never manual SSH
```

---

## Phase 2 Checklist

```
Decisions Made:
[ ] Auth strategy decided (method + session length + password hashing)
[ ] Data deletion decided (soft recommended)
[ ] Monetary serialisation decided (string recommended)
[ ] API response envelope shape defined
[ ] HTTP status code conventions defined
[ ] Container topology decided
[ ] File storage decided
[ ] Background task mechanism decided
[ ] Role model defined (roles + permissions + enforcement point)

Documents:
[ ] At least 5 ADRs written in docs/decisions/
[ ] .context/architecture.md updated with invariants block
[ ] No decisions left as "we'll figure it out later"

Quality Check:
[ ] Every invariant is a one-line rule (not a paragraph)
[ ] Rejected alternatives documented in each ADR
[ ] Consequences (positive + negative) noted in each ADR
```

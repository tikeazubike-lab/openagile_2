# CONSTRAINTS.md

## Hard Infrastructure Constraints

### Local Workstation (Fedora 42) — Execution Prohibited
- Constraint: kernel OOM crash on Python package install or code execution
- Rule: local machine does ONLY git operations and file editing
- Forbidden locally: docker, pip, npm, pytest, python, any execution
- Allowed locally: git add, git commit, git push, Neovim, Cursor, Antigravity

### Shared PostgreSQL — Never Duplicate
- One shared openagile_postgres container exists
- New services MUST reuse it — never create a second postgres container
- Connection: openagile_network (external bridge)
- Database: estate_portfolio (production), estate_portfolio_test (CI isolation)

### Traefik — All Traffic Must Flow Through It
- Never expose container ports directly to internet
- All HTTP/HTTPS via Traefik labels
- SSL via Let's Encrypt certresolver

### Deployment — GitHub Actions Only
- Never deploy via SSH directly
- Never run docker compose on local machine
- Never scp files to server
- SSH = read and diagnose only

## Hard Dependency Constraints

### bcrypt Pin — Immovable
- bcrypt==4.0.1 pinned permanently
- passlib 1.7.4 incompatible with bcrypt >= 4.1.0
- The dummy test in passlib exceeds 72 bytes and raises ValueError with newer bcrypt
- Do not upgrade regardless of security advisories without first verifying passlib fix

### API Contract — Monetary Values as Strings
- All monetary values returned as JSON strings from API
- Never return floats for financial data (JS precision loss)
- Recharts exception: parse to float at component boundary only
- Field names locked: get_session (not get_db), create_access_token(user_id, role)

### Cookie Lifetime — 30-Day Persistent
- max_age=60*60*24*30 always present on epm_token cookie
- httponly=True, secure=True, samesite="strict"
- Session-only cookie was a bug (Antigravity HO-008) — not the design

## Compute Constraints
- No GPU on VPS — all ML must be CPU-only with small models
- faster-whisper: rejected (OOM on 16GB RAM VPS)
- All AI inference off-VPS or using lightweight models

## Design Constraints

### No Cloud Storage for Documents
- Registrar documents stored in local volume ./uploads
- No S3, no Google Drive — adds external dependency, violates self-hosted preference
- Backup via rsync of uploads/ folder

### No Real-Time Market Data
- NGX does not provide free real-time API
- Price updates are point-in-time (daily), not streaming
- No WebSocket price feeds

### No Automated Broker Integration
- Nigerian brokers have no standard API
- No automated portfolio sync

### Self-Hosted Only
- All data on Netcup VPS — never in third-party cloud
- No external dependencies for core functionality

## Security Constraints
- JWT in httpOnly cookie — never localStorage
- No token in URL parameters
- No CORS for public access — same-origin policy
- File downloads gated by authentication (never direct paths)
- Magic-byte file type validation (not just MIME type from browser)
- Path traversal prevention on all file uploads (sanitise filenames)

## Code Quality Constraints
- No incomplete code ("# rest here" is forbidden)
- No placeholder hell (no YOUR_API_KEY in code)
- No hallucinated version numbers
- All monetary computations use Decimal, not float
- All soft deletes use datetime.now(timezone.utc) not datetime.utcnow()
- All API paths relative (/api/v1/...) not hardcoded domains

## Testing Constraints
- Tests must fail (RED) before production code is written — Uncle Bob rule
- No pytest-bdd — standard pytest + httpx with traceability comments
- No gitignoring test files — tests must travel with code
- epm-tests/ reinstated in repo (was incorrectly gitignored)
- Frontend tests (vitest) written only after backend tests are green


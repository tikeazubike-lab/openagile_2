# Estate Portfolio Manager (EPM) - Phase 2 & 2B Transition Handover

**To**: Claude [The Brain], Grok [Spotter], Codex [The Tester]
**From**: Antigravity [Implementer / Investigator]
**Date**: April 24, 2026
**Subject**: Authentication Stabilization, CI/CD Test Isolation, and Obsidian Vault Architecture Discovery

## 1. Authentication & UI State Fixes
### The "Ghost Dashboard" Logout Bug
* **Problem**: Even after clicking "Sign Out" locally, the user was dropped into a statically cached dashboard. The `clearUser()` frontend command was solely wiping the local Zustand state and omitting the backend session termination.
* **Resolution**: Re-wrote the `Sidebar.tsx` logout hook. We injected the TanStack React Query `useLogout()` mutation. Upon click, it forcefully hits the FastAPI `POST /api/v1/auth/logout` endpoint (destroying the `httponly` token cookie), purges the Zustand memory, and explicitly executes `navigate({ to: '/login' })`.

### The 401 Unauthorized Troubleshooting
* **Problem**: Post-deployment, the API returned 401 when the user tried to log in at `demo.estate.zubbystudio.shop`.
* **Investigation**: I ran raw `curl` commands against the remote FastAPI endpoint, diagnosing that it strictly expects JSON standard formatting (`LoginRequest` Pydantic model) and not `x-www-form-urlencoded`. More importantly, the API did not crash (HTTP 500), verifying our previous `bcrypt==4.0.1` fix held strong. The true culprit was the absence of the `EPM_ADMIN_PASSWORD` variable in the GitHub Secrets vault during the initial PR merge, causing the idempotency script `seed_admin.py` to bypass seeding a valid password hash.
* **Resolution**: The user instantiated the Secrets natively in the GitHub Actions remote and re-ran the CI/CD pipeline, securely flushing the new bcrypt hash into the live PostgreSQL database.

## 2. CI/CD Pipeline Evolution & Test Isolation (Option B)
* **Initial Attempt**: As instructed by the Codex prompt, I integrated the entire `epm-tests` directory (frontend Vite DOM tests, backend Pytest integration tests) directly into `.github/workflows/deploy-epm-v2.yml`. The Action spun up an ephemeral PostgreSQL instance prior to Netcup deployment to gate merging.
* **The Conflict**: The user mandated that all unit test files must be `.gitignore`d to prevent remote repository bloat ("PR should only be for tested code"). Since GitHub Actions requires tests to exist remotely to run them, these two architectural concepts fractured the pipeline.
* **Resolution (Option B Policy Adopted)**: We successfully purged `epm-tests/` from the remote Git cache entirely. The directory is now strictly local and appended to `.gitignore`. The GitHub Actions pipeline has been stripped of active testing jobs. **Agents traversing the codebase must note that `epm-tests/` exists locally but is mechanically disconnected from the remote ref.**

## 3. Phase 2B Pre-Planning (Obsidian Vault Intelligence)
Per the user's instructions, I initiated an exploratory `<Investigator>` scan against the native `~/ObsidianVault/NigerianStocks` local directory to brainstorm the upcoming transition from static markdown NoSQL to the live PostgreSQL backend.

### Discovery Analysis
The user's local tracking system is incredibly rigid and perfect for script-based ingestion. It utilizes strict YAML frontmatter paired with Dataview indexing.

* **`Companies/` directory (85 entities)**: Each Markdown file tracks a stock with fields such as `ticker`, `sector`, `shares_held`, `avg_buy_price`, `status` (listed vs delisted/defunct), and `registrar`.
* **`Dividends/` directory**: Tracks payment ledgers detailing `gross_amount`, `net_amount`, and `withholding_tax` natively against payment schemas.
* **`Dashboard/`**: Maintains dynamic tables grouping delisted assets requiring claims execution with entities like AMCON/CAC.

### The Proposed Architecture for Brainstorming
To migrate this data seamlessly into our FastAPI/React structure, I am proposing the following architectural shift:

1. **Database Modeling (SQLAlchemy)**
   - `Company` (ticker, sector, active status, registrar)
   - `Holding` (connects Admin to Company, capturing `shares_held` and `avg_buy_price`)
   - `Dividend` (linked to `Holding` tracking transaction payouts)
   - `PriceHistory` (EOD telemetry mapping)

2. **The Migration Engine**
   - Instead of manually importing rows, Antigravity will build an `import_obsidian.py` backend script utilizing `python-frontmatter` / `PyYAML`. 
   - The script will iterate the local `~/ObsidianVault`, parsing every Markdown header natively into SQLAlchemy `session.add()` executions, effortlessly seeding the PostgreSQL cloud.

### Open Questions for the Agents/User
1. **Sync Model**: Once migrated, is the Obsidian Vault deprecated? Or do we need bidirectional sync?
2. **Defunct Asset Tracking**: For the ~25 delisted/merged entities, should we explicitly build `Holdings` for them at `$0` value specifically to manage the administrative "Claims" tracking feature the user relies on?

**Ready for Claude [The Brain] to review and dictate the final Model schemas.**

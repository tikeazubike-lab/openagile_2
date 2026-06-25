# EPM Test Case Builder — Build Instructions

Spec-first build, following the gherkin-spec-agent protocol. Five `.feature` files
live alongside this document in `features/` — they are the source of truth. No
production code should be written that isn't traceable to a scenario in one of them.

```
epm-test-builder/
├── BUILD_INSTRUCTIONS.md          ← this file
└── features/
    ├── test_case_management.feature
    ├── test_execution.feature
    ├── reporting.feature
    ├── admin_and_auth.feature
    └── scaffold_generation.feature
```

---

## 1. Decisions locked in during brainstorming

| Question | Decision |
|---|---|
| Where does data live? | localStorage = draft cache, Postgres = source of truth after submit |
| Taxonomy enforcement | Enforced — domain dropdown, ID auto-generated as `DOMAIN-WORKFLOW-LAYER-TYPE-NNN` |
| Domain code list | Editable via admin UI (seeded with the 17 codes from the taxonomy doc) |
| Stack | FastAPI + Jinja2 + vanilla JS (no React/build step) + SQLAlchemy |
| DB engine | Postgres |
| Run history | Versioned — every execution kept, never overwritten |
| File scaffold output | Written directly to a mounted volume at the real repo path |
| Mount target | `/home/zubbyik/openagile_2/.../estate-portfolio/tests/` |
| Reports | Markdown shown inline, downloadable, and saved to DB — same for auto bug reports |
| Bug report on fail | In scope — auto-generated from the EPM Bug Report template |
| Auth | Single shared password, session-based |
| Deploy | Existing Traefik on the host — add router + cert labels only |
| Domain | `testbuild.zubbystudio.shop` |

---

## 2. Data model (Postgres)

```sql
CREATE TABLE domain_codes (
    code        VARCHAR(4) PRIMARY KEY,   -- e.g. 'AUTH'
    label       TEXT NOT NULL,            -- e.g. 'Authentication (login, logout, session, cookie)'
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE test_cases (
    id              VARCHAR(40) PRIMARY KEY,   -- e.g. 'HOLD-CREATE-BE-INT-001'
    domain_code     VARCHAR(4) REFERENCES domain_codes(code),
    workflow        VARCHAR(20) NOT NULL,      -- e.g. 'CREATE'
    layer           VARCHAR(4)  NOT NULL,      -- BE | FE | SEC | INF
    test_type       VARCHAR(4)  NOT NULL,      -- UT | INT | API | E2E | SEC | SMK
    sequence_no     INT NOT NULL,
    title           TEXT NOT NULL,
    requirement_ref TEXT,                      -- e.g. 'REQ-HOLD-001'
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (domain_code, workflow, layer, test_type, sequence_no)
);

CREATE TABLE test_runs (
    id              SERIAL PRIMARY KEY,
    test_case_id    VARCHAR(40) REFERENCES test_cases(id),
    run_number      INT NOT NULL,              -- 1, 2, 3... per test_case_id
    execution_path  TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    actual_result   TEXT NOT NULL,
    status          VARCHAR(10) NOT NULL CHECK (status IN ('Passed','Failed')),
    executed_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE (test_case_id, run_number)
);

CREATE TABLE reports (
    id          SERIAL PRIMARY KEY,
    markdown    TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE bug_reports (
    id          SERIAL PRIMARY KEY,
    test_run_id INT REFERENCES test_runs(id),
    markdown    TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT now()
);
```

`sequence_no` is computed server-side: `MAX(sequence_no)+1` for the same
`(domain_code, workflow, layer, test_type)` tuple, starting at 1 — this implements
the "AUTH-LOGIN-BE-INT-002" scenario in `test_case_management.feature`.

---

## 3. Application routes

```
GET  /login                       login form
POST /login                       verify shared password, set session cookie

GET  /                            redirect → /test-cases

GET  /test-cases                  Add Test Cases page (reads localStorage client-side)
POST /api/test-cases/draft-check  optional: validate a draft client-side before save
POST /api/test-cases/submit       writes all drafted cases to Postgres, clears localStorage

GET  /test-cases/execute          Execute Tests page — lists submitted cases needing a run
POST /api/test-runs                saves one run; if status=Failed, also creates a bug_report row
POST /api/reports/submit           generates report markdown from latest run per test case
GET  /api/reports/{id}/download    streams the saved markdown as a .md file
GET  /api/bug-reports/{id}/download

GET  /admin/domain-codes           list + add/edit form
POST /admin/domain-codes
PUT  /admin/domain-codes/{code}

POST /api/test-cases/{id}/scaffold  writes folder + .py stub to the mounted volume
```

---

## 4. Markdown report template (rendered server-side)

```
# Test Run Report — {generated_at}

| Test ID | Status | Expected | Actual |
|---|---|---|---|
| HOLD-CREATE-BE-INT-001 | Passed | ... | ... |
| PRIC-PDF-BE-INT-001    | Failed | ... | ... |
```

## 5. Bug report auto-fill mapping

From the EPM Bug Report template, fields are pre-filled like this from a failed `test_runs` row:

- **What I Did** ← `execution_path`
- **What I Expected** ← `expected_result`
- **What Actually Happened** ← `actual_result`
- **Feature Affected** ← `domain_codes.label` for the test case's `domain_code`
- **Severity, Layer, Evidence** ← left blank for the tester to fill in manually
- **Agent Instructions** section is copied verbatim, unmodified, from the template

---

## 6. Test file scaffold template (written to the mounted volume)

Generated at `{mount}/backend/{domain_folder}/{workflow_folder}/{layer_folder}/{TEST_ID}.py`,
following the exact docstring + class + async test shape from the taxonomy's
"New Test File Template," populated with the test case's title, domain, workflow,
layer, and requirement ref. The function body is **not** a stub — it contains the
test case's `execution_path` as a comment and an `assert False  # TODO: implement`
so it fails loudly instead of passing silently, per the skill's "no `pass`, no
pending()" rule. This keeps the implementation gate honest: nobody can claim a
test passes until they've actually written it.

Folder mapping (domain_code → folder) lives in one Python dict, e.g.:
```python
DOMAIN_FOLDERS = {
    "AUTH": "auth", "HOLD": "holdings", "PRIC": "prices", "PRIH": "price-history",
    "DASH": "dashboard", "REGR": "registrars", "CLAM": "claims", "DIVD": "dividends",
    "TRAN": "transactions", "NAVH": "nav-history", "WTCH": "watchlist",
    "COMP": "companies", "ADMN": "admin", "USER": "admin/users",
    "OBSD": "admin/obsidian", "CHAT": "chat", "SEC": "../security", "INF": "../infrastructure",
}
```
New domain codes added via the admin UI need a folder mapping too — surface a
required "folder slug" field on the add-domain-code form so this never falls out
of sync.

---

## 7. Docker Compose service + Traefik labels

```yaml
services:
  test-builder:
    build: .
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://USER:PASS@HOST:5432/test_builder
      SHARED_APP_PASSWORD: ${TEST_BUILDER_PASSWORD}
      SESSION_SECRET: ${TEST_BUILDER_SESSION_SECRET}
      REPO_TESTS_PATH: /repo/tests
    volumes:
      - /home/zubbyik/openagile_2/.../estate-portfolio/tests:/repo/tests
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.test-builder.rule=Host(`testbuild.zubbystudio.shop`)"
      - "traefik.http.routers.test-builder.entrypoints=websecure"
      - "traefik.http.routers.test-builder.tls.certresolver=cloudflare"
      - "traefik.http.services.test-builder.loadbalancer.server.port=8000"

networks:
  traefik-public:
    external: true
```

Adjust `certresolver` and network name to whatever the existing Traefik instance
is already using — confirm both before deploying (`docker inspect traefik` or
check the existing `traefik.yml`/dynamic config for the resolver name).

---

## 8. Implementation order (do not skip ahead)

1. Confirm all 5 `.feature` files above are correct — make changes there first, never directly in code.
2. Stand up Postgres schema (Section 2) in the shared instance, in its own DB/schema (e.g. `test_builder`).
3. Scaffold FastAPI app: routes (Section 3), SQLAlchemy models, Jinja2 templates, one vanilla JS file for localStorage handling.
4. Generate pytest tests from each `.feature` file's scenarios (per the skill's Step 4 — one test per scenario, traceability comment citing the feature file and step).
5. Run the generated test suite against the scaffolded routes — expect red.
6. Implement just enough route/model logic to turn each test green, in this order: test case management → execution/runs → reporting/bug reports → admin domain codes → auth → scaffold generation (most complex, do last).
7. Re-run the full suite — confirm all green, fill in the traceability matrix.
8. Add the Docker Compose service + Traefik labels (Section 7), confirm the volume mount path is correct and writable.
9. Point Cloudflare DNS for `testbuild.zubbystudio.shop` at the host (or confirm it already resolves there), deploy, hit `/login`.
10. Smoke test end-to-end: add a test case → submit → execute → mark failed → confirm bug report generated → submit report → confirm scaffold file written to the real repo path.

---

## 9. Open items to confirm before Step 8 (deployment)

- Exact Traefik cert resolver name in use on the host.
- Whether `traefik-public` (or equivalent) network name matches what's already there.
- Postgres connection details (host/port/db name) for the shared instance.

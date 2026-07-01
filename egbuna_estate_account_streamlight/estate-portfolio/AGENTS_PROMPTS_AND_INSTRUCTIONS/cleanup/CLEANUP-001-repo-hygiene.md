# CLEANUP-001 — Repository Debris Removal & Test Tree Consolidation
**From**: Claude (The Brain)
**To**: Antigravity OR Deepseek v4 (whoever picks this up first)
**Date**: 2026-06-15
**Branch**: test
**Commit type**: chore
**Rule**: ONE commit, NO production code changes, NO logic changes

---

## What This Task Is

A pure repository hygiene commit. No backend logic changes. No frontend
logic changes. Move files, delete files, update .gitignore. Nothing else.

If you are unsure whether a file is safe to delete, move it to
`scripts/experiments/` instead. Do not delete anything you cannot
confirm is truly unused.

---

## Step 1 — Consolidate Test Trees

The authoritative test tree is `backend/tests/`. The `epm-tests/` directory
is a partial duplicate. Merge anything unique from `epm-tests/` into
`backend/tests/` then delete `epm-tests/`.

```bash
# On VPS — SSH to diagnose first
cd /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio

# List what is in epm-tests/ but NOT in backend/tests/
diff -rq epm-tests/ backend/tests/ --exclude="*.pyc" 2>/dev/null

# If any files are unique to epm-tests/, copy them:
# cp epm-tests/unique_file.py backend/tests/appropriate_location/

# Then remove the duplicate tree
rm -rf epm-tests/
```

Add to `.gitignore`:
```
epm-tests/
```

---

## Step 2 — Delete Root-Level Debris Files

These files have no purpose in the production codebase:

```bash
cd /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio

# Temp data files
rm -f temp_daily.txt temp_prices1.txt temp_prices2.txt

# Log file (add to .gitignore instead of committing)
rm -f cron.log

# Design reference image (not source code)
rm -f "Dialin-—-Analytics-Dashboard-UI-by-Orix-Creative-on-Dribbble.png"
```

Add to `.gitignore`:
```
cron.log
*.log
temp_*.txt
```

---

## Step 3 — Move PDF Parser Experiments to experiments/

These are development scratch files used while building the PDF parser.
They are not tests, not scripts, not production code. Move, don't delete
— they document how the parser was developed.

```bash
mkdir -p scripts/experiments/pdf_parser
mkdir -p scripts/experiments/regex

mv test_pdf.py test_pdf2.py test_pdf3.py test_pdf4.py \
   test_pdf5.py test_pdf6.py test_pdf7.py test_pdf8.py \
   scripts/experiments/pdf_parser/

mv test_regex.py test_regex2.py test_regex3.py \
   scripts/experiments/regex/
```

---

## Step 4 — Organise Root-Level Script Files

```bash
mkdir -p scripts/utils
mkdir -p scripts/data

# Ticker utilities (one-off tools, keep but organise)
mv extract_tickers.py scripts/utils/
mv extract_tickers_from_txt.py scripts/utils/

# Data files (reference data, not code)
mv tickers.txt scripts/data/
mv ngx_companies_list.txt scripts/data/
```

---

## Step 5 — Handle Defunct Scrapers

These scrapers are confirmed dead or have no NGX coverage:

```bash
# yfinance has no NGX (XNSA) coverage — confirmed defunct
# rapidapi_scraper — status unknown, no active use confirmed
# Move to experiments rather than delete in case code is reused

mkdir -p scripts/experiments/scrapers
mv scripts/rapidapi_scraper.py scripts/experiments/scrapers/
mv scripts/yfinance_scraper.py scripts/experiments/scrapers/

# ngx_scraper.py — status unclear, keep in scripts/ for now
# DO NOT move or delete without confirming it is not called anywhere
grep -r "ngx_scraper" . --include="*.py" --include="*.yml" --include="*.sh"
# If no references found: mv scripts/ngx_scraper.py scripts/experiments/scrapers/
```

---

## Step 6 — Gitignore the Obsidian Vault

The NigerianStocks/ directory is the Obsidian vault. It should never
be committed to the repo. It belongs on the local machine only and
syncs to the VPS via the private vault GitHub repo.

```bash
# Check if NigerianStocks/ is tracked by git
git ls-files NigerianStocks/ | head -5

# If tracked, remove from git index (keeps files on disk):
git rm -r --cached NigerianStocks/
```

Add to `.gitignore`:
```
NigerianStocks/
uploads/
*.log
cron.log
temp_*.txt
epm-tests/
```

Note: `uploads/` should also be gitignored — real uploaded documents
(registrar PDFs/images) should not be in version control.

---

## Step 7 — Clean Up Duplicate Env Files

```bash
# .env contains real secrets — should NEVER be in git
git ls-files .env .env.v2 | head

# If tracked, remove from git index:
git rm --cached .env .env.v2 2>/dev/null

# Keep .env.example and .env.v2.example (templates are fine)
```

Add to `.gitignore`:
```
.env
.env.v2
.env.local
```

---

## Step 8 — Mark v1 Legacy Files Clearly

Do NOT delete the v1 files yet — the Streamlit app is still running
at production. Just add a README note:

Create `LEGACY_V1_README.md` in root:
```markdown
# Legacy v1 Files

The following files belong to EPM v1 (Streamlit) and will be retired
after production cutover to v2 (FastAPI + React):

- app.py — Streamlit entry point
- docker-compose.yml — Streamlit Docker config
- Dockerfile — Streamlit Dockerfile
- requirements.txt (root) — Streamlit dependencies

Do not modify these files. They are kept only until cutover is complete.
Production cutover checklist: see PROJECT_STATUS.md
```

---

## Step 9 — Update .gitignore Comprehensively

Final `.gitignore` additions (append to existing backend/.gitignore
or create root-level .gitignore if missing):

```gitignore
# Secrets
.env
.env.v2
.env.local

# Logs
*.log
cron.log

# Temp files
temp_*.txt

# Obsidian vault (synced separately via private repo)
NigerianStocks/

# Uploaded documents (production data, not source code)
uploads/

# Duplicate test tree (consolidated into backend/tests/)
epm-tests/

# Python cache
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Node
node_modules/
dist/
build/

# OS
.DS_Store
Thumbs.db
```

---

## The Commit

After all steps above are complete:

```bash
git add -A
git status  # review everything before committing

git commit -m "chore: repository cleanup — consolidate test trees, remove debris, update gitignore

- Merged epm-tests/ into backend/tests/, deleted duplicate tree
- Moved PDF parser experiments to scripts/experiments/pdf_parser/
- Moved regex experiments to scripts/experiments/regex/
- Moved defunct scrapers to scripts/experiments/scrapers/
- Moved ticker utilities to scripts/utils/
- Moved data files to scripts/data/
- Removed temp files (temp_daily.txt, temp_prices1.txt, temp_prices2.txt)
- Removed design reference image
- Added NigerianStocks/ to .gitignore (vault synced separately)
- Added uploads/ to .gitignore (production data)
- Added .env files to .gitignore (secrets)
- Added cron.log to .gitignore
- Created LEGACY_V1_README.md for v1 Streamlit files"

git push origin test
```

---

## Acceptance Criteria

```
[ ] epm-tests/ directory no longer exists in repo
[ ] backend/tests/ contains all unique tests from both trees
[ ] Root directory contains only: AGENTS.md, CHANGELOG.md,
    CONTRIBUTING.md, Dockerfile.v2, LEGACY_V1_README.md,
    PROJECT_STATE.json, app.py (v1), deploy.sh, docker-compose*.yml,
    .env.example files, .gitignore, and the main project directories
[ ] git status shows clean working tree after commit
[ ] No .env or NigerianStocks/ in git ls-files output
[ ] scripts/ contains only production-ready scripts + clearly labelled experiments/
[ ] backend/tests/ pytest runs without import errors after consolidation
```

---

## What This Task Does NOT Do

```
❌ Does not change any Python logic
❌ Does not change any React code
❌ Does not modify any API endpoint
❌ Does not touch any migration
❌ Does not add new features
❌ Does not fix any bugs

This is purely a file organisation task.
```

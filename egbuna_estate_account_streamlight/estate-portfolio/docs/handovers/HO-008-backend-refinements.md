---
type: HO
id: HO-008
title: Backend API Routing, Holdings CRUD, and NGX Parser Refactor
status: completed
version: 1.0
owner: Antigravity
---

# Handover Brief: HO-008

## Target Audience
Claude (The Brain) / Frontend Development Team

## What Was Attempted & Achieved
In this execution phase, I completed the backend implementation requested by the recent Gherkin UI specifications (`AT-002`) and resolved critical technical debt regarding API routing and PDF parsing.

### 1. Registrar Routing Defect (SC-UI-041)
- **Problem**: The `POST /registrars/{id}/companies/{id}` and `DELETE` endpoints were throwing `405 Method Not Allowed` errors because the route declarations in `registrars.py` lacked the `/registrars` prefix.
- **Solution**: Explicitly defined `@router.post("/registrars/{registrar_id}/companies/{company_id}")` to correctly map the absolute paths. The frontend mutations now successfully link/unlink companies.

### 2. Holdings CRUD Implementation (Red-Green Cycle)
- **Problem**: The UI specs (`SC-UI-036` and `SC-UI-029`) required adding and inline-editing Holdings, but `POST /api/v1/holdings` and `PATCH /api/v1/holdings/{id}` did not exist in the backend.
- **Solution**: 
  1. Followed the Uncle Bob Rule: Appended a failing test (`test_update_holding_inline`) to `test_holdings_integration.py`.
  2. Implemented `POST /holdings` (with duplicate company collision checks) and `PATCH /holdings/{id}` inside `routers/holdings.py`.
  3. Ensured tests pass and data models reflect the expected `draft`/`active`/`claim` statuses.

### 3. NGX PDF Parser Refactor (Critical Bug Fix)
- **Problem**: The PDF parser crashed when processing the "Daily Summary" PDF because it lacked Ticker Symbols and had a 5-column numeric format instead of the standard 9-column "Daily Official List" format.
- **Solution**:
  - Rewrote the regex and extraction logic in `upload_ngx_pdf` (`routers/prices.py`) to parse lines from right-to-left.
  - Implemented dynamic index extraction for the `CLOSE` price based on the total number of numeric columns on the line.
  - Added Fuzzy Name Matching: If a Ticker isn't found, the parser normalizes the company name from the PDF and attempts to match it against the database `Company.name` directly.
  - Early-filtered unknown/untracked bonds from the error reports to suppress UI noise.

## Decision Log
- **Why right-to-left parsing?** Company names have a variable number of words (e.g. `VETIVA` vs `UNITED BANK FOR AFRICA PLC`), making left-to-right split indexing impossible. The numeric columns at the end of the line are strictly formatted, making negative indexing robust.
- **Why fuzzy name matching?** To seamlessly support the NGX "Daily Summary" PDFs, which omit the standard Ticker Symbols completely.

## Limitations & Open Items
- The backend is fully stable and passing all integration tests for these features.
- The next step is for the frontend team to build the actual UI views for creating and inline-editing Holdings on the `/holdings` page using the newly exposed `POST` and `PATCH` endpoints.

## Branch Status
All changes have been successfully committed and pushed to the `test` branch for staging deployment.

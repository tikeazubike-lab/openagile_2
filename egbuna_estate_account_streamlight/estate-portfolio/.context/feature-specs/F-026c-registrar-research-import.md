# F-026c: Registrar research import (contacts, duplicate merge, company links)

| Field | Value |
|---|---|
| Status | Approved scope (Product Owner, 2026-11-27): option 3; Low-confidence mappings held back |
| Author | Claude Code (architect), 2026-11-27 |
| HO | HO-160 (block HO-159..HO-208) |
| Branch | `feature/f-026c-registrar-research-import`, stacked on PR #10 (`feature/f-026-dashboard-and-f-026b-reminders`) |
| Source data | `docs/registrars/registrars_contact_details_final.md` (sha256 `87ff3927b391151dd4ba3024666a789268725cbcb8d1b13596c096be6cc45ea9`), vouched for by the Product Owner |
| Related | F-026 `F-026-registrar-dashboard.md`; MASTER_CONTEXT v4.8 seed incident (HO-101..106) |

## 1. Purpose
Fill the registrars page with researched contact details, show each registrar once, and point each
company at its correct registrar. This is a **data change only**: no application code, schema, or
migration changes. It ships as one committed script with a read-only preview and an undo file.

## 2. Facts this spec relies on (verified 2026-11-27 against production, read-only)
- F1. The registrar detail page lists companies from the legacy FK `companies.registrar_id`
  (`backend/app/routers/registrars.py:85`, `:383`; same in the running container). The dashboard reads
  `company_registrars` (`:152`). Today 71 companies have the FK set, but 146 have a join-table link:
  75 linked companies never appear on a registrar's detail page. **The import writes both stores.**
- F2. `RegistrarDetails.tsx:82` shows `contact_fields` when any exist, and only otherwise the legacy
  columns `email/phone/website/address`. Adding fields to a registrar with hand-entered legacy values
  would hide them, so those values are carried into `contact_fields` first (§4.3).
- F3. `field_type` `website`/`email`/`phone` render as links. Any other type (e.g. `other`, `address`)
  renders as plain text. `label` is max 100 chars, `field_type` max 20.
- F4. `company_registrars` has UNIQUE (company_id, registrar_id), including soft-deleted rows. To
  relink, reactivate an existing row (`deleted_at = NULL`); never insert a second one.
- F5. Document downloads use the stored `registrar_documents.file_path`
  (`registrars.py:677`), so moving a requirement to another registrar does not break its files.

## 3. Registrar resolution table (authoritative; the script hard-codes it, it does not guess)
Canonical = the record that keeps the data. Duplicates are merged into it and then soft-deleted.

| File slug | Canonical id | Duplicates merged | Final name |
|---|---|---|---|
| meristem | 2 | 9, 57 | keep "Meristem Registrars" |
| africa-prudential | 50 | 6 | keep |
| first-registrars | 52 | 11 | keep |
| greenwich | 8 | 3, 56 | "Greenwich Registrars & Data Solutions Limited" |
| coronation | 51 | 12 | keep |
| cardinalstone | 55 | 21 | keep |
| veritas | 13 | 53 | "Veritas Registrars Limited" |
| unity | 1 | 17 | keep "Unity Registrars" |
| atlas | 7 | — | "Atlas Registrars Limited" |
| datamax | 54 | — | keep |
| pace | 58 | — | keep |
| crescent | 59 | — | keep |
| carnation | 61 | — | keep |
| apel | new | — | "Apel Registrars And Corporate Services Limited" |
| cordros | new | — | "Cordros Registrars Limited" |
| lighthouse | new | — | "Lighthouse Registrars Ltd" |
| pac | new | — | "PAC Registrars & Investor Services Limited" |
| lancelot | new | — | "Lancelot Registrars And Investors Relations Limited" |
| fsl | new | — | "FSL Registrars Limited" |
| paxhil-minerva | new | — | "Paxhil Minerva Registrars Limited" |

New registrars get `jurisdiction='nigeria'`, `status='active'`. Before writing, the script verifies that each
listed id exists, is not soft-deleted, and has a name containing the slug's first word (case-insensitive).
On any mismatch it aborts with no writes. Records not in this table (ids 4, 5, 10, 14, 15, 16, 18, 19, 20, 22,
23, 60, 62) are not touched, except that their links to companies the file maps firmly are replaced (§4.4).

## 4. Rules
### 4.1 Merge (per duplicate D into canonical K)
1. `company_registrars` rows of D: if K already has a row for that company (active or not), soft-delete D's row.
   Otherwise re-point it to K. If both are active primaries, keep one.
2. `companies.registrar_id = D` becomes K.
3. `registrar_requirements.registrar_id = D` becomes K. Documents follow their requirement.
4. Active `registrar_contact_fields` of D move to K unless K already has the same normalised value
   (case-folded, whitespace-collapsed, digits-only for phones).
5. `response_rating`: copy D's onto K only if K's is NULL. `notes`: append D's to K's, with the prefix `[merged from #D] `.
6. Soft-delete D (`deleted_at = now()`). Never hard-delete anything.

### 4.2 Contacts from the file (per registrar)
- Phones: one `phone` field per entry. Value = `e164`. Label = the file `label` (or "Phone"), plus
  ` — ` + `warning` if the warning is set, cut to 100 chars.
- Emails: only `show_on_page: true`. Value = `address`, label = file label or "Email".
- Website: `field_type='website'` only if `safe_to_link: true`. Otherwise `field_type='other'` with the label
  "Website (not verified, copy manually)" so it renders as text. A null website adds nothing.
- Portals: same rule as websites, label = `description` or "Online portal".
- Offices: only `show_on_page: true`, and **skip** offices whose `type` starts with "Group" (they belong to a
  parent or sister company). `field_type='address'`, value = `address`, label = office `type`. Append
  " (please confirm)" when the office's `confidence` is not High, or when it is the head office and
  `head_office.flag` is not OK.
- `sort_order`: head office address 1, then phones, emails, website/portals, other offices, from 10 in steps of 10,
  after any existing fields.
- Skip any value K already has, by the normalisation in 4.1.4. Never edit or delete an existing field.
- Legacy columns on K (`email`, `phone`, `address`, `website`): fill only those that are NULL, from
  `primary_email`, `primary_phone`, `head_office.address`, and `website.url` (only if safe_to_link).
  Never overwrite a non-NULL value.
- Never use `internal_research_notes`, `evidence_sources` or `latest_operating_evidence`.

### 4.3 Hand-entered values are preserved (F2)
Before adding file fields to K: for each non-NULL legacy column on K (and on its duplicates, from
the merge) that has no matching field, add a field with that type and the label "Entered manually".
After the import, every value that was visible on the page before is still visible.

### 4.4 Company links
A file client is **firm** if `mapping_confidence != 'Low'` and `mapping_flag != 'UNVERIFIED'`. Otherwise it is **weak**.
Match companies only by exact upper-cased `ticker` against active `companies.ticker`. Never by name.
- Firm and matched: the file registrar becomes the company's only active `primary`. Set
  `companies.registrar_id = K`, reactivate or create the (company, K) `primary` row, and soft-delete the
  company's other active `primary` rows. `co_registrar` rows are never touched (e.g. SEPLAT / Computershare UK).
- Weak and matched (13 today): **no link change**, beyond what the §4.1 merge re-points. Listed in the report for
  the Product Owner to decide one by one.
- Unmatched (no ticker, or a ticker not in `companies`; 53 today), and `without_contact_record` (5 rows):
  no company is created and no link is written. Listed in the report.
- Companies not in the file: untouched, except for the §4.1 re-pointing.

### 4.5 Execution
- Script: `backend/scripts/import_registrar_research.py`. The file is parsed from its single ```json block.
- Default mode is **preview**. The session runs `SET TRANSACTION READ ONLY`, so Postgres itself rejects any write.
  It prints the full plan (per registrar, per company, with before → after) and the counts.
- `--apply --confirm-db <dbname>`: refuses unless `<dbname>` equals the connected database name. Runs in
  **one transaction**: all or nothing. Writes an undo file
  `docs/registrars/import-runs/<UTC timestamp>-<dbname>.json` holding every row touched, with its previous values
  and the ids of the rows it inserted.
- `--undo <file> --confirm-db <dbname>`: restores the previous values, soft-deletes the inserted rows, and
  reactivates the merged duplicates, in one transaction.
- The script refuses to run if `DATABASE_URL` is unset, and never prints the URL or its password.
- Idempotent: a second `--apply` on the same data plans zero changes.

## 5. Acceptance criteria (AT-026c)
| AC | Given | When | Then |
|---|---|---|---|
| AC-1 | the file and a DB | preview runs | no row changes; any write attempted fails as read-only; the plan and counts are printed |
| AC-2 | duplicates 9 and 57 of canonical 2, each with company links | apply | links point to 2 (no unique violation); 9 and 57 are soft-deleted; the list endpoint shows Meristem once |
| AC-3 | Greenwich dup 3 with rating 4 and an `other` field, canonical 8 with 2 requirements and their documents | apply | 8 has rating 4, the field, and both requirements; each document still downloads from its stored path |
| AC-4 | a registrar with hand-entered legacy email/phone and no fields | apply | its legacy values appear as fields labelled "Entered manually"; the legacy columns are unchanged |
| AC-5 | a website with `safe_to_link: false` | apply | stored as `field_type='other'` (renders as text), not `website` |
| AC-6 | an email or office with `show_on_page: false`; a "Group office" | apply | not stored |
| AC-7 | a head office with confidence Medium, or flag CONFLICT/STALE | apply | its label ends with "(please confirm)" |
| AC-8 | a firm mapping for company C, currently a primary of registrar X | apply | C's only active primary is K; `companies.registrar_id = K`; the old row is soft-deleted; C appears on K's detail page |
| AC-9 | C also has a `co_registrar` link | apply | the co_registrar link is unchanged |
| AC-10 | a weak mapping for company W | apply | W's links are unchanged (except merge re-pointing); W is listed under "held back" |
| AC-11 | a file ticker not present in `companies` | apply | no company is created; listed under "unmatched" |
| AC-12 | apply has run | apply runs again | zero planned changes |
| AC-13 | apply has run and its undo file exists | undo runs | every touched row matches its pre-apply state; the duplicates are active again |
| AC-14 | `--confirm-db` differs from the connected DB, or a §3 id check fails | apply | aborts before any write, exit code non-zero |
| AC-15 | any error mid-apply | apply | the transaction rolls back; nothing changed |

## 6. Tests
- Unit (`backend/tests/unit/test_import_registrar_research.py`): parsing, firm/weak classification, label rules,
  normalisation, and plan building from an in-memory snapshot. AC-5, AC-6, AC-7, AC-10, AC-11, AC-14 (name check).
- Integration (`backend/tests/integration/test_import_registrar_research.py`), real Postgres, **`epm_test` only**:
  builds its own fixture rows, runs preview/apply/undo, and asserts AC-1..AC-4, AC-8, AC-9, AC-12, AC-13, AC-15.
  Skips only when `epm_test` is unreachable. Mocked sessions do not count as SQL proof.
- Trace comment on each test: `# Spec: F-026c-registrar-research-import.md | AC-N`.

## 7. Production run procedure (orchestrator; each step needs the Product Owner's go)
1. Preview against production (read-only). The plan is saved under HO-160 for review.
2. Product Owner go → `pg_dump` of `registrars`, `registrar_contact_fields`, `company_registrars`,
   `registrar_requirements`, and `companies` (id, registrar_id), kept outside git.
3. Apply with `--confirm-db`. Commit the undo file and the run output to the branch, and report the SHA.
4. Verify on the page (Playwright): a merged registrar shows once, its contacts show, and its companies list includes the
   newly linked companies.
There is **no** production run before the PR passes auditor review and the Product Owner approves the preview.

## 8. Out of scope / follow-ups
- The 13 weak mappings and 53 unmatched rows (the Product Owner decides).
- United Securities duplicates (20, 60) and the other non-file records (not in the research file).
- Retiring `companies.registrar_id` from the detail page code (F1 drift; MASTER_CONTEXT says the column is
  unused, but the code still reads and writes it). Log it for v4.11.

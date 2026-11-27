Fix round 1 for HO-160. Spec: `.context/feature-specs/F-026c-registrar-research-import.md`, **§9 amendment A-1..A-7** (read it first).
Auditor findings and responses: `docs/handovers/HO-160-registrar-research-import.md` §4.3.

ENVIRONMENT: same as `HO-160-brief-builder-continue.md` (python path, unit command with a dead DB URL).
Do NOT query documentation, Context7 or the web. Do not run tests/integration. Do not connect to any database.
The host is short on memory: run only the single unit test file while iterating, and the full unit suite once at the end.

FILES IN SCOPE: backend/scripts/import_registrar_research.py, backend/tests/unit/test_import_registrar_research.py,
backend/tests/integration/test_import_registrar_research.py. Existing assertions may only be changed where the amendment changes the rule
(A-4 sort orders, A-7 CLI flags); say which ones in the report.

STEPS (one commit each, `fix(f-026c):` / `test(f-026c):`, ending `Co-Authored-By: OpenCode <noreply@opencode.ai>`):
1. RED unit tests: A-1, A-2, A-3 (a second build_plan on the post-apply state plans zero ops), A-4, A-5, A-6 (no row/column changed
   twice; a merged company that is also firm-mapped gets one consistent "before"; counts equal distinct rows), A-7/AC-17
   (CLI `--apply` without `--undo-out` exits non-zero; the undo writer is called before commit, and a writer failure → rollback,
   tested with a fake session/engine).
2. Implement A-6 first (a working copy of the snapshot that each planned op updates), then A-1..A-5, then A-7.
3. Integration file: make the AC-1 test call the real preview entry (`_run_preview` or `cli`) against the fixture DB; make AC-13
   round-trip the undo record through `to_json` → `json` → `from_json` before `undo`. Do not run it.
4. Full unit suite; paste the raw summary line.

REPORT: full 40-char SHAs, raw summary lines, any assertion you changed and why.

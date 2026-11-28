Advisory review (read-only) for HO-160 / F-026c. Do not edit files, do not run anything that writes, do not connect to any database.

Spec: `.context/feature-specs/F-026c-registrar-research-import.md`.
Diff to review: `git diff 696254e32e46c518e151e0a1a47921ac129d4467..HEAD -- backend/` (script, unit tests, integration tests, fixture).
Evidence: `docs/handovers/HO-160-preview-prod-2026-11-27.md` (read-only production preview output).

Focus, in order:
1. Data safety of `apply_plan` and `undo`: can any path hard-delete, touch rows outside the plan, violate
   UNIQUE(company_id, registrar_id), leave a company with two active primaries, or touch a `co_registrar` row?
   Does undo restore every changed column and reactivate merged duplicates?
2. Spec conformance: §3 resolution checks, §4.1 merge order, §4.2 label/visibility rules, §4.3 hand-entered values,
   §4.4 firm/weak/unmatched, §4.5 read-only preview and --confirm-db before any write.
3. Test quality: do tests assert behaviour or only mirror the implementation? Any tautologies?

Output: numbered findings, each with file:line, severity (blocker / should-fix / nit), and a one-line fix. End with SHIP or HOLD.

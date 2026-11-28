You are the frontend builder. Work only in this worktree's epm directory (the folder containing estate-portfolio-manager/).

Read and execute exactly: docs/handovers/HO-159-pr10-completion-brief.md, section "Part G — tabs on /registrars".
Governing spec: .context/feature-specs/F-026-registrar-dashboard.md (§5, §6 AC-7/AC-8, §9).

Commands (run from estate-portfolio-manager/):
- tests:   npx vitest run
- one file: npx vitest run src/components/registrars/__tests__/RegistrarsLayout.test.tsx
- types:   npx tsc --noEmit -p tsconfig.json

Rules: edit only the two files named in Part G. Commit G1 (RED test) and G2 (implementation) separately with
messages starting "test(f-026): G1" and "feat(f-026): G2". Do not push, do not install packages, do not touch backend.

Final report (under 40 lines): files changed, commit SHAs (full 40 chars), raw vitest summary line(s) for the RED run
and the GREEN run, raw tsc error count with file names, anything you could not do.

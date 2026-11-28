Execute ONLY Part D of the brief below (Parts A-C are done). Working directory is the EPM project dir.


## Part D — make the new frontend tests run under `npm run test` (role: builder) — added 2026-11-23
Architect ruling on Part C escalation C1: tests that the project runner skips do not count.
Scope: `estate-portfolio-manager/vitest.config.ts` only, plus deleting the scratch file below.

1. In `estate-portfolio-manager/vitest.config.ts`:
   - add `"src/**/__tests__/**/*.test.ts"` and `"src/**/__tests__/**/*.test.tsx"` to `test.include`
     (keep the existing `tests/**` entries);
   - add `resolve.alias` so `@` maps to `./src` (same as `vite.config.ts`; use
     `fileURLToPath(new URL("./src", import.meta.url))` or `path.resolve(__dirname, "src")`).
2. Delete the untracked scratch file `vitest.ho159-scratch.config.ts` at the worktree root
   (two levels above the EPM dir: `../../vitest.ho159-scratch.config.ts`). Do not commit it.
3. Run `cd estate-portfolio-manager && npx vitest run` and paste the raw summary. Expected: the 3 new
   `src/**/__tests__` files (12 tests) now run and pass; the 4 pre-existing jest-dom import failures remain
   (do not install packages, do not touch those files).
4. Commit: `test(config): collect src/**/__tests__ and add @ alias in vitest (HO-159 Part D)`.

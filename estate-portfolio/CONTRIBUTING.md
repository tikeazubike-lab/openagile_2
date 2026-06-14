# Contributing to Estate Portfolio Manager

## Branch Strategy
- `main` — production only. Protected. No direct pushes.
- `test` — all active development. PRs merge here first.
- `feature/xyz` — short-lived feature branches off test
- `fix/xyz` — bug fix branches off test
- `docs/xyz` — documentation-only changes

## Conventional Commit Messages
Format: `<type>(<scope>): <description>`

Types:
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `test` — adding or updating tests
- `chore` — dependency updates, config changes
- `refactor` — code restructure, no behaviour change
- `perf` — performance improvement

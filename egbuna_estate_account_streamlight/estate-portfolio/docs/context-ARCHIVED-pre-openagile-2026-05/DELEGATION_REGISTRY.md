---
type: CONTEXT
id: EPM-DELEGATION-REGISTRY
title: EPM Agent Delegation Registry
status: ACTIVE
version: 2.0
updated: 2026-06-19
---

# EPM Agent Delegation Registry

## Active Agents

| Agent | Role | Write Scope | Notes |
|---|---|---|---|
| DeepSeek v4 | Reviewer / Architect | None (read-only) | Architecture validation, code review gatekeeping, final correctness validation. No code execution. |
| Owl Alpha | Backend Builder | `backend/`, backend tests, backend migrations | Owns API contract, database logic, test writing. |
| Nex N2 | Frontend Builder | `estate-portfolio-manager/src/` | Owns React UI only. Reads backend contracts, never modifies backend. |

## Conflict Rules

- Agents working in the same local checkout do not need push/pull choreography
  between themselves.
- Use path ownership to avoid conflicts.
- If a change crosses backend and frontend contracts, Owl Alpha updates backend
  contract first, Nex N2 adapts frontend second, then DeepSeek performs
  final integration review.
- Root-level files remain in place unless an approved migration explicitly
  moves them.

## Final Push Rule

Owl Alpha is the preferred final pusher for backend contract fixes.
Nex N2 pushes frontend changes after backend is stable.
DeepSeek performs final review before any merge to main.

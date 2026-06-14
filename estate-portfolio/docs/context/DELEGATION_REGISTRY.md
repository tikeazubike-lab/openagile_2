---
type: CONTEXT
id: EPM-DELEGATION-REGISTRY
title: EPM Agent Delegation Registry
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# EPM Agent Delegation Registry

## Active Agents

| Agent | Role | Write Scope | Notes |
|---|---|---|---|
| Deepseek v4 | Backend Builder + Final Integrator | `backend/`, backend tests, backend migrations | Owns API contract fixes and final push after integration review. |
| Antigravity (Gemini model) | Frontend Builder | `estate-portfolio-manager/src/` | Owns React UI fixes only. |
| Grok | Spotter | None | Read-only review of contracts, tests, and handover consistency. |
| Codex | Context Orchestrator | `docs/` unless reassigned | Maintains local context engine and corrected handovers. |

## Conflict Rules

- Agents working in the same local checkout do not need push/pull choreography
  between themselves.
- Use path ownership to avoid conflicts.
- If a change crosses backend and frontend contracts, Deepseek updates backend
  contract first, Antigravity adapts frontend second, then Deepseek performs
  final integration review.
- Root-level files remain in place unless an approved migration explicitly
  moves them.

## Final Push Rule

Deepseek v4 is the preferred final pusher for this sprint, because backend
contract fixes are the highest-risk part of AT-003-2.


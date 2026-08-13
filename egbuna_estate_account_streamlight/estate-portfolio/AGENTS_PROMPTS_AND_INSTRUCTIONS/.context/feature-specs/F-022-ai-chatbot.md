---
type: F
id: F-022
title: AI-Assisted Interactive Chatbot (Read-Only Q&A)
status: Spec complete, all Open Questions resolved — pending Zone 2 consensus (DeepSeek Pro) before implementation
author: Claude Web (The Brain / Architect)
date: 2026-07-16
related: Locked decision "RuleBasedRouter first, for AI chatbot feature F-022"
supersedes: any prior content in .context/feature-specs/F-022-ai-chatbot.md — reconcile before overwriting
---

# F-022 — AI-Assisted Interactive Chatbot

## 0. Scope Guardrail (read this first)

This was originally floated as a platform-agnostic chatbot product usable
across estate-agent, insurance, and marketing platforms. **That idea is
explicitly deferred, not part of this spec.** F-022 is narrowly scoped to
EPM only. If a genuinely generic version is ever built, it will emerge
from this one real implementation, not be designed speculatively ahead of
it — see the multi-tenant EPM discussion (2026-07-16) for the reasoning.

## 1. Purpose

A floating chat widget, available on every authenticated page, that
answers questions about the estate's own portfolio data — "what's my
current NAV," "how many holdings do I have in banking," "what's the
status of my dividend claim for X" — without the user navigating to the
relevant page. Read-only for v1: it answers, it does not act.

## 2. Scope

**In scope:**
- Floating widget UI (frontend already built via Lovable — see §6),
  available on every page for any authenticated user
- Read-only Q&A against existing, already-shipped data domains (see §2.1)
- Rule-based intent matching first (locked architectural decision), with
  deterministic answers pulled from existing API endpoints — never
  invented figures
- RBAC-aware: a USER only ever sees what they're already permitted to see
  elsewhere in the app; no new data-visibility rules invented for the bot

**Out of scope for v1 (explicitly deferred, per 2026-07-16 discussion):**
- Any action-triggering capability (e.g. "recalculate my NAV" via chat) —
  confirmed read-only-only for this version
- Platform-agnostic / multi-tenant genericization
- Free-form financial advice or analysis beyond what's directly queryable
- Document/PDF Q&A (RAG) — not needed since v1 is structured-data-only
- Persisted, user-browsable chat history (see §8, OQ-3)
- Voice, multi-language

### 2.1 Data Domains In Scope for V1 — Confirmed 2026-07-16

All four already-shipped domains are in scope from day one — nothing
here is still in flux, so there's no real risk in covering all of them
at once rather than staging a fast-follow:

- **Holdings** (F-003) — share counts, current value, sector, return %
- **NAV** (F-007, fully shipped) — current NAV, 7D/30D/YTD change,
  coverage disclosure (bot must mention the same 34%-coverage caveat the
  dashboard shows, not a cleaner number that hides the same gap)
- **Claims/Dividends** (F-010/F-011) — claim status (unresolved/unclaimed/
  claimed), expected/actual payout
- **Companies** (F-013) — sector, registrar, ticker lookups
- **Price History** (F-005) — recent price for a given ticker, date-range
  lookups

## 3. Architecture — RuleBasedRouter (locked decision)

```
User message
    ↓
RuleBasedRouter: match against known intent patterns
    ↓
Matched → call the corresponding EXISTING API endpoint directly
    (GET /api/v1/nav, GET /api/v1/holdings, GET /api/v1/claims, etc.)
    → return structured data, phrase as a short natural-language reply
    ↓
Unmatched → see §8, OQ-1 (fallback behavior not yet decided)
```

**Hard rule, non-negotiable**: the bot never generates a number itself.
Every figure it states must trace back to a real API call against real
data — this is the same "monetary values never invented" discipline
already locked for the rest of this codebase, applied to conversational
output instead of a UI table.

No new data-access logic is written for this feature — the router calls
the same endpoints a human already uses via the UI, respecting the same
auth/RBAC those endpoints already enforce. This is a routing and
phrasing layer on top of existing, already-audited data paths, not a new
data layer.

## 4. Data Model

New table: `chatbot_conversations` — a lightweight, server-side log, not
a user-facing history feature (see §8, OQ-3 for whether this is wanted
at all).

```sql
CREATE TABLE chatbot_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    matched_intent VARCHAR(100),        -- NULL if unmatched
    response TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Purpose: lets a future session see which questions are actually being
asked, to prioritize which intents to add next — informed by real usage
rather than guessing. Not exposed as a "chat history" feature to the end
user in v1.

## 5. API Contract

### `POST /api/v1/chatbot/query`
- **Auth**: any authenticated user (widget is available to all roles)
- **Request**: `{ "message": "what's my current NAV?" }`
- **Response**:
  ```json
  {
    "data": {
      "matched_intent": "current_nav",
      "response": "Your current NAV is ₦43,174,252.02, based on 25 of 73 holdings with price data (34%).",
      "raw_data": { "total_value": "43174252.0200", "coverage": {...} }
    },
    "meta": null,
    "error": null
  }
  ```
- Monetary values in `raw_data` as strings, per standing convention.
- If unmatched, `matched_intent: null` and `response` is whatever §8 OQ-1
  decides the fallback behavior is.
- Every call writes a row to `chatbot_conversations` (§4).

## 6. Frontend Requirements

**The floating widget component already exists** — built in React via
Lovable, ready to hand over. Per this project's established Lovable
pipeline (Lovable → builder review/hardening → Kimi escalation if
needed), **this component should go through the same hardening pass any
Lovable output gets before being wired to real endpoints** — null-safety
per `code-standards.md` conventions (optional chaining, no raw `.map()`
on possibly-undefined data), RBAC-awareness (the widget must not cache or
display data a role shouldn't see), and integration with the real
`POST /api/v1/chatbot/query` endpoint rather than whatever mock data it
currently uses.

- Available on every authenticated route, floating (not a full page)
- Wire to `POST /api/v1/chatbot/query`
- Loading state while awaiting response
- Empty/error state per `ui-context.md`'s mandatory empty-state pattern
  if the query fails or returns nothing useful

## 7. Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AT-F022-001 | Widget renders and is accessible on every authenticated page |
| AT-F022-002 | A matched intent (e.g. "what's my NAV") returns the real current value, matching what `/api/v1/nav` returns independently |
| AT-F022-003 | A USER-role query never returns data a USER isn't otherwise permitted to see (cross-check against existing RBAC rules) |
| AT-F022-004 | An unmatched query does not crash and returns whatever §8 OQ-1 decides as fallback behavior |
| AT-F022-005 | Every query writes a row to `chatbot_conversations`, with the correct `user_id` |
| AT-F022-006 | Widget handles a failed API call gracefully — error state, not a blank/broken widget |
| AT-F022-007 | NAV-related answers include the same coverage disclosure the dashboard shows, not a cleaner/misleading number |
| AT-F022-008 | A Companies-domain query (e.g. sector/registrar lookup for a ticker) returns data matching what `/api/v1/companies` returns independently |
| AT-F022-009 | A Price-History-domain query (e.g. "what's the latest price for X") returns data matching what the price history endpoint returns independently |

## 8. Open Questions — All Resolved 2026-07-16

| ID | Question | Answer |
|----|----------|--------|
| OQ-F022-1 | Should unmatched queries fall back to an LLM for natural-language phrasing, or return a fixed "I don't understand, try one of these examples" message? | **Fixed message.** Keeps behavior fully deterministic and free. LLM-phrasing may be revisited as a v2 enhancement once real usage data (via `chatbot_conversations`) shows what people actually ask. |
| OQ-F022-2 | Confirm data domains in scope for v1 — Holdings/NAV/Claims only, or include Companies/Price History from day one? | **All four domains from day one** — Holdings, NAV, Claims, Companies, Price History. All already shipped and stable, no staged rollout needed. |
| OQ-F022-3 | Should `chatbot_conversations` ever be exposed as a browsable history to the end user, or stay purely a server-side log? | **Server-side log only for v1.** A user-facing history feature is a separate, later decision, not needed for the core Q&A capability. |

## 9. Dependencies

Unlike the original "blocked on F-007–F-016" note in `progress-tracker.md`,
this is now genuinely unblocked — both are fully shipped:
- **F-007 NAV History** — complete (backend, frontend, backfill, cron)
- **F-016 User Management** — shipped
- **F-010/F-011 Claims** — shipped
- **F-003 Holdings** — shipped

No outstanding upstream blockers for the recommended v1 scope.

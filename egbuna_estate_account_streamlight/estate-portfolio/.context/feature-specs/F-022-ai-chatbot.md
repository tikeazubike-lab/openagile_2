---
id: F-022
title: AI Assisted Interactive ChatBot
status: PLANNED
owner-backend: Deepseek:flash
owner-frontend: Nemotron
architect: DeepSeek v4
reviewer: DeepSeek v4
sprint: Phase 4 (future — blocked on F-007 through F-016)
grok-gaps-resolved: all 7
---

# F-022 — AI Assisted Interactive ChatBot

## Goal
A floating AI assistant on every authenticated page that answers natural language questions about the user's portfolio using data retrieved from the EPM database at query time. No model training required. No LLM calls on every query (rule-based first).

## Why Phase 4 (Do Not Build Yet)

The IntentRouter's intents map directly to EPM features:
- "What is my portfolio value?" → requires F-007 NAV History data
- "Show my top holdings" → requires F-003 Holdings stable
- "Which dividends are unclaimed?" → requires F-008 Dividends
- "What claims are pending?" → requires F-010 Claims

Building the chatbot before these features exist means building intents with no data to query. Complete F-007 through F-016 first, then F-022 has real targets to route to.

## Architecture Overview

```
User types query
       ↓
GatekeeperFilter (length check, auth, content policy)
       ↓
RuleBasedRouter (keyword/pattern matching — Stage 1)
       ↓ [if confidence < threshold]
OllamaRouter (local LLM fallback — Stage 2, optional)
       ↓ [if still unresolved]
FallbackHandler (unsupported_query response)
       ↓
IntentHandler (queries PostgreSQL, formats response)
       ↓
Response: { data: { text, chart? }, meta: { intent, router }, error: null }
```

## Frontend

### Position & Visibility
- Floating launcher button: **bottom-right**, `z-[9999]`, fixed position
- **Auth guard:** Hidden on login/register pages (unauthenticated routes)
- Visible on ALL authenticated routes including admin

### 3-Stage Flow
```
Stage 1 — Launcher: 52px circle, Sparkles icon, lavender glow
Stage 2 — Input Bar: 320px width, expands right → left
Stage 3 — Chat Panel: 380px width, 500px max-height, scrollable
```

### Dismiss Behavior
- Clicking outside the panel at **any stage** → returns to launcher
- **Draft text preserved:** Unsubmitted input text is kept in state
- Re-opening launcher restores the unsent prompt
- Submitted prompts clear the input field

### Chart Rendering
Reuse existing Recharts patterns (no new chart components):
- `pie` → SectorAllocationChart pattern
- `bar` → TopHoldingsChart pattern
- `line` / `area` → PriceHistoryChart pattern

## Backend

### Endpoint
```
POST /api/v1/chat/query
Auth: Depends(get_current_user)
Router: APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

### Request
```json
{ "query": "What is my portfolio worth today?" }
```

### Success Response
```json
{
  "data": {
    "text": "Your active portfolio is worth ₦12,345,678.00 as of today.",
    "chart": {
      "type": "pie",
      "title": "Sector Allocation",
      "data": [
        { "name": "Financial Services", "value": "6500000.00" },
        { "name": "Industrial Goods", "value": "3200000.00" }
      ],
      "x_key": "name",
      "y_key": "value"
    }
  },
  "meta": { "intent": "portfolio_value", "router": "rule_based", "query_length": 38 },
  "error": null
}
```

### Chart Types (locked)
`line` | `bar` | `pie` | `area` — no other types. Frontend only renders these four.

### Chart Data Contract
All monetary values as **JSON strings** (not floats). Frontend parses at Recharts boundary.
```json
{
  "type": "pie | bar | line | area",
  "title": "Human-readable title",
  "data": [{ "name": "label", "value": "string" }],
  "x_key": "name",
  "y_key": "value"
}
```

### Error Contract
```json
{
  "data": null,
  "meta": {},
  "error": { "code": "QUERY_TOO_LONG", "message": "Query exceeds 500 characters." }
}
```

| Code | HTTP | Meaning |
|------|------|---------|
| EMPTY_QUERY | 400 | Query is blank |
| QUERY_TOO_LONG | 400 | Exceeds 500 chars |
| POLICY_VIOLATION | 400 | Forbidden content |
| INTENT_ERROR | 500 | Handler exception |
| UNAUTHORIZED | 401 | Not authenticated |
| unsupported_query | 200 | Valid but out of scope |

### Conversation Mode
**Stateless.** Every request is independent. No chat history persisted to DB. UI shows visual memory only.

### GatekeeperFilter (runs before any router)
```python
class GatekeeperFilter:
    MAX_QUERY_LENGTH = 500

    def validate(self, query: str) -> GatekeeperResult:
        # 1. Length check
        # 2. Content policy (no password/token/SQL injection patterns)
        # Returns GatekeeperResult(allowed, reason, message)
```

### IntentRouter Interface (Stage 1 → Stage 2 upgrade path)
```python
class IntentRouter:
    def route(self, query: str) -> Intent: ...
```
- Stage 1: `RuleBasedRouter(IntentRouter)` — regex keyword matching
- Stage 2: `LLMRouter(IntentRouter)` — local Ollama drop-in replacement

### Stage 1 Intents (8 intents)
```python
INTENTS = {
    "portfolio_value":   {"patterns": [r"portfolio.*(value|worth|total)", ...], "requires": ["F-007"]},
    "holdings_summary":  {"patterns": [r"(show|list|what).*(holding|stock|share)", ...], "requires": ["F-003"]},
    "price_query":       {"patterns": [r"(price|cost|value).*(of|for)\s+[A-Z]{2,6}", ...], "requires": ["F-004","F-005"]},
    "dividend_query":    {"patterns": [r"dividend", ...], "requires": ["F-008"]},
    "claims_query":      {"patterns": [r"claim", ...], "requires": ["F-010"]},
    "performance_query": {"patterns": [r"(return|performance|gain|loss|profit)", ...], "requires": ["F-007"]},
    "sector_query":      {"patterns": [r"sector", ...], "requires": ["F-002"]},
    "unsupported_query": {"patterns": [], "requires": []},  # catch-all
}
```

### Stage 2 — OllamaRouter (Optional, Future)
Local LLM on VPS. Receives pre-fetched DB data as context in prompt (RAG pattern). LLM never accesses DB directly.

## Backend File Structure
```
backend/app/routers/chat.py              — endpoint + request/response models
backend/app/services/chat/
  __init__.py
  gatekeeper.py                          — GatekeeperFilter
  router.py                              — RuleBasedRouter (Stage 1)
  ollama_router.py                       — OllamaRouter (Stage 2, optional)
  intents/
    __init__.py
    portfolio_value.py
    holdings_summary.py
    price_query.py
    dividend_query.py
    claims_query.py
    performance_query.py
    sector_query.py
    fallback.py
```

## Frontend File Structure
```
estate-portfolio-manager/src/components/chat/
  AiAssistant.tsx        — Main component (launcher + input + panel)
  MessageBubble.tsx      — User/assistant message rendering
  InlineChart.tsx        — Bar chart + sparkline rendering (Recharts)
  LauncherButton.tsx     — Floating sparkle button
estate-portfolio-manager/src/routes/__root.tsx  — Add <AiAssistant /> with auth guard
estate-portfolio-manager/src/api/queries.ts     — Add useChatQuery hook
```

## Frontend State (Zustand)
```typescript
interface ChatStore {
  stage: 'launcher' | 'input' | 'panel'
  draftText: string           // preserved across stage collapses
  messages: ChatMessage[]     // visual history, session only
  pending: boolean            // loading state
}
```

## Acceptance Checklist

### [DB]
- [ ] No new tables required for Stage 1 (stateless)
- [ ] Intent handlers query existing tables only
- [ ] No chat history persisted to DB

### [API]:
- [ ] POST /api/v1/chat/query with "what is my portfolio worth" → 200, intent=portfolio_value
- [ ] POST with empty string → 400, code=EMPTY_QUERY
- [ ] POST with 501+ char string → 400, code=QUERY_TOO_LONG
- [ ] POST with unrelated query → 200, intent=unsupported_query
- [ ] POST without auth → 401
- [ ] Response chart.type is one of: line | bar | pie | area | null
- [ ] All chart data values are JSON strings (not floats)
- [ ] meta.intent field present in every response
- [ ] meta.router field present: "rule_based" | "ollama" | "fallback"
- [ ] Unknown queries return 200 with helpful fallback text (not 4xx)

### [UI]:
- [ ] Sparkle button visible bottom-right on authenticated pages
- [ ] Sparkle button NOT visible on /login
- [ ] Click button → input bar expands
- [ ] Type text → click outside → collapses → reopen → text preserved
- [ ] Submit query → loading dots → response text shown
- [ ] Response with chart → chart renders inline (correct type)
- [ ] Response without chart → text only, no empty chart container
- [ ] Query > 500 chars → error shown, no API call
- [ ] Visible on /admin/* routes
- [ ] Dark theme compatible (CSS variables, oklch colors)
- [ ] z-[9999] above all content
- [ ] No console errors

## Dependencies
- Backend: No new packages (reuses FastAPI, SQLAlchemy)
- Frontend: `recharts` (already in EPM), `lucide-react` (already in EPM)
- Stage 2 only: `ollama` Python package + local model

## Sign-Off Criteria

Status moves to APPROVED_FOR_IMPLEMENTATION when:
- [ ] F-007 through F-016 are complete (intent targets exist)
- [ ] All acceptance checklist items are reviewable
- [ ] Ollama decision made (use or skip Stage 2)
- [ ] progress-tracker.md updated to IN-PROGRESS

Current status: PLANNED — blocked on prerequisite features.
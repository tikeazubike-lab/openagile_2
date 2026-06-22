---
id: F-022
title: AI Assisted Interactive ChatBot
status: PLANNED
owner-backend: Antigravity (Owl Alpha)
owner-frontend: Deepseek v4 (Nex N2)
architect: Claude (The Brain)
reviewer: Grok (Spotter)
sprint: Phase 4 (future — blocked on F-007 through F-016 completing first)
replaces: Deepseek draft F-017 (renumbered — F-017 is reserved for editMode removal)
grok-gaps-resolved: all 7
---

# F-022 — AI Assisted Interactive ChatBot

## Goal

A floating AI assistant on every authenticated page that answers
natural language questions about the user's portfolio using data
retrieved from the EPM database at query time. No model training
required. No LLM calls on every query (rule-based first).

---

## Why Phase 4 (Do Not Build Yet)

The IntentRouter's intents map directly to EPM features:
  - "What is my portfolio value?" → requires F-007 NAV History data
  - "Show my top holdings" → requires F-003 Holdings stable
  - "Which dividends are unclaimed?" → requires F-008 Dividends
  - "What claims are pending?" → requires F-010 Claims

Building the chatbot before these features exist means building
intents with no data to query. Complete F-007 through F-016 first,
then F-022 has real targets to route to.

---

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
Response: { text, chart? }
```

---

## Stage 1 — RuleBasedRouter

Build this first. Test it until its failure modes are clear.
Only then evaluate whether Ollama is needed.

Rationale:
1. Rule-based is free — no per-query cost
2. Failures are observable and debuggable (exact keyword that missed)
3. Most EPM queries are formulaic ("what is X", "show me Y")
4. A well-designed rule set may be sufficient for 90% of queries

### Intent Definitions (Stage 1 — 8 intents)

```python
INTENTS = {
    "portfolio_value": {
        "patterns": [
            r"portfolio.*(value|worth|total)",
            r"(what|how much).*(own|have|worth)",
            r"total.*(asset|portfolio)",
            r"net worth",
        ],
        "requires_features": ["F-007"],
    },
    "holdings_summary": {
        "patterns": [
            r"(show|list|what).*(holding|stock|share)",
            r"top.*(holding|stock|position)",
            r"(my|current).*(portfolio|investment)",
        ],
        "requires_features": ["F-003"],
    },
    "price_query": {
        "patterns": [
            r"(price|cost|value).*(of|for)\s+[A-Z]{2,6}",
            r"[A-Z]{2,6}.*(price|trading|worth)",
            r"(current|latest|today).*(price|close)",
        ],
        "requires_features": ["F-004", "F-005"],
    },
    "dividend_query": {
        "patterns": [
            r"dividend",
            r"(unclaimed|unpaid).*(income|payment)",
            r"(how much|any).*(dividend)",
        ],
        "requires_features": ["F-008"],
    },
    "claims_query": {
        "patterns": [
            r"claim",
            r"(delisted|defunct|amcon|cac)",
            r"(pending|outstanding).*(claim|payout)",
        ],
        "requires_features": ["F-010"],
    },
    "performance_query": {
        "patterns": [
            r"(return|performance|gain|loss|profit)",
            r"(up|down|change).*(percent|%)",
            r"(how|well|bad).*(perform|doing|grown)",
        ],
        "requires_features": ["F-007"],
    },
    "sector_query": {
        "patterns": [
            r"sector",
            r"(banking|financial|industrial|consumer|oil|telecoms)",
            r"(allocation|exposure|breakdown).*(sector|industry)",
        ],
        "requires_features": ["F-002"],
    },
    "unsupported_query": {
        "patterns": [],   # catch-all — see GatekeeperFilter below
        "requires_features": [],
    },
}
```

### Confidence Threshold

```python
CONFIDENCE_THRESHOLD = 0.7

# If highest-matching intent scores below threshold:
#   Stage 1 → Stage 2 (Ollama) if configured
#   Stage 2 absent → FallbackHandler (unsupported_query)
```

---

## Stage 2 — OllamaRouter (Optional, Future)

Local LLM using Ollama on the VPS. Acts as drop-in replacement
for RuleBasedRouter when confidence is low.

**How it works (no training required)**:
The LLM does not need to know about EPM. It receives:
```
System: You are a router. Classify the user query into one of these
        intents: [list]. Return only the intent name. If none match,
        return "unsupported_query".
User: [the query]
```
The LLM returns an intent name. The IntentHandler then queries the
database and formats the response. The LLM never sees the data itself.

**Why local Ollama instead of cloud LLM**:
- No per-query API cost
- Data stays on the VPS
- llama3.2 (3B) is sufficient for intent classification — this is
  not a generation task, it is a classification task

**Data retrieval (RAG pattern)**:
For IntentHandlers that need to include DB data in the response text,
inject it as context:
```python
# Example for portfolio_value intent:
db_data = await get_portfolio_summary(db)  # fast DB query
prompt = f"User has portfolio worth {db_data.total}. Answer: {query}"
# LLM generates a natural-language sentence from the data
```
The LLM never accesses the database directly. It receives pre-fetched
data as text in the prompt. This is the entire RAG pattern for this
use case.

---

## GatekeeperFilter (Required — Runs Before Any Router)

```python
class GatekeeperFilter:
    MAX_QUERY_LENGTH = 500  # characters

    def validate(self, query: str) -> GatekeeperResult:
        # 1. Length check
        if len(query.strip()) == 0:
            return GatekeeperResult(allowed=False, reason="EMPTY_QUERY")
        if len(query) > self.MAX_QUERY_LENGTH:
            return GatekeeperResult(allowed=False, reason="QUERY_TOO_LONG",
                message=f"Query exceeds {self.MAX_QUERY_LENGTH} characters.")

        # 2. Content policy (basic — no personal data injection)
        forbidden_patterns = [
            r"(password|token|secret|api.?key)",
            r"(drop|delete|truncate|insert|update)\s+table",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return GatekeeperResult(allowed=False, reason="POLICY_VIOLATION")

        return GatekeeperResult(allowed=True)
```

---

## API Contract (Fully Locked — Resolves Grok Gap #1 #2 #3 #4 #5 #6)

### Endpoint

```
POST /api/v1/chat/query
Auth: Depends(get_current_user) — all authenticated roles
Router: APIRouter(prefix="/api/v1/chat", tags=["chat"])
```

### Request

```json
{
  "query": "What is my portfolio worth today?"
}
```

Validation:
- `query` required, non-empty string
- Maximum length: 500 characters (enforced by GatekeeperFilter)
- No system prompt injection — `query` is user text only

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
        { "name": "Industrial Goods",   "value": "3200000.00" },
        { "name": "Consumer Goods",     "value": "2645678.00" }
      ]
    }
  },
  "meta": {
    "intent": "portfolio_value",
    "router": "rule_based",
    "query_length": 38
  },
  "error": null
}
```

**Chart is optional** — only included when the intent warrants it.
If no chart: `"chart": null`

### Supported Chart Types (Grok Gap #1 — resolved)

```
line  — price history over time
bar   — top holdings by value or shares
pie   — sector allocation
area  — NAV history trend
```

No other types. If a handler produces a chart, it must use one of these
four types. Frontend only renders these four. Any other type is ignored.

### Chart Data Contract (Grok Gap #2 — resolved)

All chart types use this shape:

```json
{
  "type": "pie | bar | line | area",
  "title": "Human-readable chart title",
  "data": [
    { "name": "string label", "value": "string monetary or numeric" }
  ],
  "x_key": "name",
  "y_key": "value"
}
```

For time series (line, area):
```json
{
  "type": "line",
  "title": "Portfolio NAV — Last 30 Days",
  "data": [
    { "name": "2026-05-01", "value": "12100000.00" },
    { "name": "2026-05-02", "value": "12234000.00" }
  ],
  "x_key": "name",
  "y_key": "value"
}
```

Monetary values: always strings. Frontend parses to float at Recharts
boundary only (consistent with existing EPM contract).

### Unknown Query Response (Grok Gap #3 — resolved)

```json
{
  "data": {
    "text": "I can currently answer portfolio-related questions only. Try asking about your portfolio value, holdings, dividends, claims, or price history.",
    "chart": null
  },
  "meta": {
    "intent": "unsupported_query",
    "router": "fallback"
  },
  "error": null
}
```

Unknown queries always return 200 with `intent: unsupported_query`.
They are NOT 4xx errors — the API worked, the query was just out of scope.

### Conversation Mode (Grok Gap #5 — resolved)

```
conversation-mode: stateless

Every request is independent.
No chat history is persisted in the database.
No session context is carried between requests.
The UI may show previous messages visually, but the backend
treats each POST /api/v1/chat/query as a fresh request.
```

If multi-turn memory is added in the future, it is a new feature
(F-023) with its own migration and spec — it is NOT assumed here.

### Error Contract (Grok Gap #6 — resolved)

```json
{
  "data": null,
  "meta": {},
  "error": {
    "code": "QUERY_TOO_LONG",
    "message": "Query exceeds 500 characters. Please be more concise."
  }
}
```

Error codes:
```
EMPTY_QUERY         — query is blank
QUERY_TOO_LONG      — exceeds 500 characters
POLICY_VIOLATION    — forbidden content detected
INTENT_ERROR        — handler raised an exception (DB error, etc.)
UNAUTHORIZED        — not authenticated (standard 401)
```

HTTP status codes:
```
200  — success (including unsupported_query — it is a valid response)
400  — EMPTY_QUERY, QUERY_TOO_LONG, POLICY_VIOLATION
401  — UNAUTHORIZED
500  — INTENT_ERROR (handler failed — bug)
```

---

## AuthGuard Visibility (Grok Gap #7 — resolved)

```
Visible on: every route protected by the _app.tsx AuthGuard
Hidden on:  login page, register page (if added), any public route

Explicit inclusion list:
  /dashboard, /holdings, /companies, /dividends,
  /price-history, /transactions, /registrars, /watchlist,
  /nav-history, /rebalancing, /admin/*

This means ALL authenticated routes including admin routes.
Admin users benefit from chatbot access in the admin section.
```

Implementation: floating button rendered in `__root.tsx` inside
the `<Outlet />` wrapper for authenticated routes, not in the
login route file.

---

## Frontend — 3-Stage Flow

### Stage Layout

```
Stage 1 — Launcher (default):
  Floating sparkle button, bottom-right, fixed position
  z-index: 9999 (above all other content)
  Size: 52px circle, accent-lavender background
  Icon: Sparkles (Lucide)

Stage 2 — Input Bar:
  Expands from launcher position upward
  Width: 320px
  Input field with placeholder: "Ask about your portfolio..."
  Send button (arrow icon)
  Pressing Enter submits
  Clicking outside → collapse to Stage 1, PRESERVE typed text

Stage 3 — Chat Panel:
  Width: 380px, max-height: 500px, scrollable
  Previous messages shown (visual history, not persisted)
  Current query processing: loading spinner
  Response: text + chart (if applicable)
  Chart renders inline using existing Recharts components
  Clicking outside → collapse to Stage 1, PRESERVE unsent draft text
```

### Draft Text Preservation

```typescript
// In chat store (Zustand):
interface ChatStore {
  stage: 'launcher' | 'input' | 'panel'
  draftText: string        // preserved across stage collapses
  messages: ChatMessage[]  // visual history, memory only (not persisted)
  setStage: (s: Stage) => void
  setDraft: (t: string) => void
  submitQuery: (query: string) => Promise<void>
}

// On outside click at any stage:
setStage('launcher')
// draftText is NOT cleared — preserved for re-open

// On submit:
setDraft('')             // clear draft ONLY after successful submit
messages.push(newMsg)   // add to visual history
```

### Chart Rendering

Reuse existing Recharts components already in the codebase:
- `pie` → existing SectorAllocationChart pattern
- `bar` → existing TopHoldingsChart pattern
- `line` / `area` → existing PriceHistoryChart pattern

Do not create new chart components. Pass the chart data from the
API response into the existing component interfaces.

---

## Backend File Structure

```
backend/app/routers/chat.py           — endpoint + request/response models
backend/app/services/chat/
  __init__.py
  gatekeeper.py                       — GatekeeperFilter
  router.py                           — RuleBasedRouter (Stage 1)
  ollama_router.py                    — OllamaRouter (Stage 2, optional)
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

Each intent handler is a standalone function:
```python
# intents/portfolio_value.py
async def handle(db: AsyncSession, user_id: int) -> ChatResponse:
    data = await get_portfolio_summary(db, user_id)
    return ChatResponse(
        text=f"Your active portfolio is worth {fmtNaira(data.total_value)} as of today.",
        chart=build_sector_chart(data.sector_allocation)
    )
```

---

## Acceptance Checklist

### [DB]
- [ ] No new tables required for Stage 1 (stateless)
- [ ] Intent handlers query existing tables only
- [ ] No chat history persisted to DB (confirmed stateless)

### [API]
- [ ] POST /api/v1/chat/query with "what is my portfolio worth" → 200
      intent = portfolio_value, text contains ₦ amount
- [ ] POST with empty string → 400, code = EMPTY_QUERY
- [ ] POST with 501+ character string → 400, code = QUERY_TOO_LONG
- [ ] POST with "Warren Buffett children" → 200, intent = unsupported_query
- [ ] POST without auth → 401
- [ ] Response chart.type is always one of: line | bar | pie | area | null
- [ ] All chart data values are JSON strings (not floats)
- [ ] meta.intent field present in every response
- [ ] meta.router field present: "rule_based" | "ollama" | "fallback"

### [UI]
- [ ] Sparkle button visible bottom-right on /dashboard (authenticated)
- [ ] Sparkle button NOT visible on /login
- [ ] Click button → input bar expands
- [ ] Type text → click outside → input bar collapses → reopen → text preserved
- [ ] Submit query → loading spinner → response text shown
- [ ] Response with chart → chart renders inline in correct type
- [ ] Response without chart → text only, no empty chart container
- [ ] Query > 500 chars → error message shown, no API call
- [ ] Visible on /admin/* routes (admin users)

---

## Open Questions (Deferred to Implementation Phase)

These are not blockers for the spec — they are decisions for the
implementation agent to make and document in a handover:

1. Which Ollama model version for Stage 2? (llama3.2:3b recommended
   for classification — fast, low memory, sufficient for intent routing)
2. How many messages to show in visual history before truncating?
   (Suggested: last 10 exchanges)
3. Should the chat panel be dismissible with Escape key?
   (Recommended: yes — standard keyboard UX)

---

## Sign-Off Criteria

Status moves to APPROVED_FOR_IMPLEMENTATION when:
- [ ] F-007 through F-016 are complete (intent targets exist)
- [ ] All acceptance checklist items above are reviewable
- [ ] Ollama decision made (use or skip Stage 2)
- [ ] progress-tracker.md updated to IN-PROGRESS

Current status: PLANNED — blocked on prerequisite features.

---
id: F-017
title: AI Chat Bot
status: PLANNED
owner-backend: Owl Alpha
owner-frontend: Nex N2
Review/Architect role: Deepseek
sprint: Phase 4 (future)
---

# F-017 — AI Chat Bot

## Goal
A floating AI assistant on every page that answers portfolio questions in natural language with text explanations and embedded Recharts visualizations. No page navigation required — the user stays on their current page and gets instant answers.

## User Stories

### Core Queries
- "What's my biggest holding?" → top holdings by value
- "Show my sector allocation" → sector breakdown with bar chart
- "Any dividends due this month?" → upcoming dividends
- "How has my portfolio performed this month?" → gain/loss with trend
- "Why did my portfolio drop yesterday?" → top decliner with chart

### Expected Response Format
Every response returns:
1. Text explanation (1–3 sentences)
2. Optional embedded chart (bar chart or sparkline)

### Example Interaction
```
User: How has my portfolio performed this month?
AI: Your portfolio is up 4.2%. Top performer: MTN +8.4%.
     Worst performer: UBA −3.1%. Dividend expected: NGN 15,400.
     [Bar chart: top performers]
```

## Architecture

### Frontend
- Floating launcher button (bottom-right) on all **authenticated** pages via root layout
- **Auth guard:** Hidden on login/register pages (use `authStore` Zustand state)
- 3-stage flow: launcher → input bar → chat panel
- **Dismiss on outside click:** Clicking anywhere outside the panel (at any stage) returns to launcher state. The unsubmitted input text is **preserved** — when the user re-opens the launcher, their typed-but-not-sent prompt is still there. Submitted prompts clear the input field as normal.
- Chat panel: message bubbles + inline SVG charts (bars, sparklines)
- Dark theme using existing EPM CSS variables
- No page navigation — the assistant overlays any page

### Backend
- `POST /api/v1/chat/query` — single endpoint
- Router definition: `router = APIRouter(prefix="/api/v1/chat", tags=["chat"])` (matches dominant style used by prices.py, companies.py, obsidian.py)
- Auth: `Depends(get_current_user)` — same as all other routers
- Receives `{ "query": "..." }`
- Returns standard envelope:
  ```json
  { "data": { "text": "...", "chart": {...} }, "meta": {}, "error": null }
  ```
- Stage 1: Rule-based intent parsing via `IntentRouter` interface (abstract, so Stage 2 LLM can drop in as replacement)
- Stage 2 (future): LLM-powered natural language → structured query
- Chart monetary values as strings per API contract (frontend parses at Recharts boundary)
- Text explanations can be human-readable formatted values

### IntentRouter Interface (for Stage 1 → Stage 2 upgrade)
```python
class IntentRouter:
    def route(self, query: str) -> Intent: ...
```
Stage 1: `RuleBasedRouter(IntentRouter)` — keyword matching
Stage 2: `LLMRouter(IntentRouter)` — drop-in replacement

### Data Flow
```
User Query → FastAPI → IntentRouter → DB Query → Envelope Response
```

### Tech Stack
Same as existing EPM: React 18 + TanStack Router + shadcn/ui + Recharts (frontend), FastAPI + SQLAlchemy async + PostgreSQL (backend).

## Files to Create / Modify

### Frontend (Nex N2)
- Create: `estate-portfolio-manager/src/components/chat/AiAssistant.tsx`
- Create: `estate-portfolio-manager/src/components/chat/MessageBubble.tsx`
- Create: `estate-portfolio-manager/src/components/chat/InlineChart.tsx`
- Create: `estate-portfolio-manager/src/components/chat/LauncherButton.tsx`
- Modify: `estate-portfolio-manager/src/routes/__root.tsx` — add AiAssistant
- Modify: `estate-portfolio-manager/src/api/queries.ts` — add useChatQuery

### Backend (Owl Alpha)
- Create: `backend/app/routers/chat.py`
- Modify: `backend/app/main.py` — register chat router

### Test Files (Owl Alpha + Nex N2)
- Create: `backend/tests/unit/test_chat_intents.py`
- Create: `estate-portfolio-manager/tests/unit/components/chat.test.tsx`

## Acceptance Criteria

### [API]
- [ ] POST /api/v1/chat/query with "biggest holding" → 200 with data.text and data.chart
- [ ] POST /api/v1/chat/query with "sector allocation" → returns sectors + bar chart data in envelope
- [ ] POST /api/v1/chat/query with "dividend" → returns dividend info
- [ ] POST /api/v1/chat/query with "performance" → returns gain/loss
- [ ] POST /api/v1/chat/query with unknown query → returns helpful fallback
- [ ] Response wrapped in envelope: { data: { text, chart? }, meta: {}, error: null }
- [ ] Chart data follows { kind, title, items[] | points[] } shape
- [ ] Chart monetary values are JSON strings (not floats)
- [ ] Post-authenticated — returns 401 without cookie (get_current_user guard)

### [UI]
- [ ] Floating launcher button visible on all **authenticated** pages (bottom-right)
- [ ] Launcher hidden on login/register pages (unauthenticated)
- [ ] Clicking launcher opens input bar
- [ ] Clicking outside the panel (any stage) dismisses back to launcher, **retaining typed-but-not-submitted text**
- [ ] Re-opening launcher after dismiss shows the preserved input text
- [ ] Submitting a query clears the input field
- [ ] Submitting query shows loading state
- [ ] Response text renders in chat bubble
- [ ] Bar chart renders inline when chart.kind === "bars"
- [ ] Sparkline renders inline when chart.kind === "spark"
- [ ] Dark theme compatible (uses CSS variables)
- [ ] Suggestion chips shown before first query
- [ ] Multiple queries create a conversation history in the panel
- [ ] Close button returns to launcher state
- [ ] No console errors on any page

## Dependencies
- None from external packages — reuses existing shadcn/ui, Recharts, Lucide
- Backend reuses existing database models and queries

## Future (Stage 2 — Not in This Spec)
- LLM integration for natural language → query translation
- Multi-turn conversation context
- Watchlist notifications
- Live news/social media consolidation
- Purchase workflow guidance

## Architect Review Resolution

The following questions were reviewed and resolved by DeepSeek (Architect) in the initial review:

| Question | Resolution |
|----------|-----------|
| Endpoint path location | `/api/v1/chat/query` → `router = APIRouter(prefix="/api/v1/chat", tags=["chat"])` matching prices.py style |
| Render on ALL pages or Dashboard only | All **authenticated** pages via `__root.tsx` with auth guard |
| Rule-based vs LLM from start | Rule-based is **accepted** for Stage 1 (deterministic, testable, zero cost). IntentRouter interface abstracts for Stage 2 LLM swap |
| Reuse dashboard API or dedicated endpoint | **Dedicated endpoint** — avoids coupling, fetches only needed data, direct DB queries |
| Response envelope | Must wrap in standard `{ data, meta, error }` envelope (was a CRITICAL finding) |
| Monetary format | Chart values as JSON strings (API contract); text explanations can be human-readable |

All findings from the initial review have been incorporated into this spec.
---
type: HO
id: HO-018-1
title: Corrected HO-018 Amendment for Deepseek Backend, Antigravity Frontend, Grok Spotter
date: 2026-05-23
from: Codex Context Orchestrator
to: Deepseek v4 + Antigravity/Gemini + Grok
status: ACTIVE
amends: docs/handover/HO-018-claude-to-both-agents.md
protocol: EPM docs/context workflow v1.0
---

# [HO] HO-018-1 — Corrected AT-003-2 Recovery Handover

This handover amends, but does not mutate, `HO-018`. The original handover
remains a historical artifact at `docs/handover/HO-018-claude-to-both-agents.md`.
This amendment reflects the owner's requested agent ownership and the codebase
evidence found in EPM v2.

## Part 0: Authority And Scope

Read these first:

1. `docs/context/MASTER_CONTEXT.md`
2. `docs/context/AGENT_STATE.yaml`
3. `docs/context/DELEGATION_REGISTRY.md`
4. `docs/context/WORKFLOW.md`
5. Root `AGENTS.md`

Project root:

```text
egbuna_estate_account_streamlight/estate-portfolio/
```

Do not run Docker locally. Deployments go through GitHub Actions only.

## Part 1: Corrected Agent Ownership

| Agent | Role | Owns | Must Not Edit |
|---|---|---|---|
| Deepseek v4 | Backend Builder + Final Integrator | `backend/`, backend tests, Alembic, API contracts | React UI files unless coordinating an API contract update |
| Antigravity/Gemini | Frontend Builder | `estate-portfolio-manager/src/` | Backend files, migrations, compose/workflows |
| Grok | Spotter | Read-only review | All files |

Two local agents in the same checkout do not need push/pull between each other.
Use file ownership and one final integrator. Deepseek owns the final integration
review and push to `test`.

## Part 2: Corrections To HO-018

### Correction A: POST /api/v1/holdings 500 Is Not Primarily A user_id Issue

Code evidence:

- `backend/app/models.py` defines `Holding` with `average_cost_basis` and
  `total_cost`, but no mapped `status` attribute.
- `backend/app/routers/holdings.py` creates `Holding(..., status="draft")`.
- The same create path does not supply `total_cost`.

Likely backend failure causes:

1. Invalid model constructor keyword: `status`.
2. Missing non-null `total_cost`.
3. Lifecycle drift between `status` (`LIVE`/`DRAFT`) expected by frontend and
   tests, and `holding_type` (`active`/`claim`/possibly `draft`) used by backend.
4. POST route does not explicitly return HTTP 201, while tests expect 201.

Deepseek must resolve this contract at backend level before frontend changes
depend on it.

### Correction B: Dashboard Blank Charts Are Not Guaranteed To Be Recharts Only

Current frontend maps `sector_allocation` and `top_holdings`, but:

- Sector values depend on backend `current_value`; zero/null data creates a
  visually blank chart.
- Top Holdings "By Shares" uses `dataKey="shares"`, but frontend chart data does
  not include a `shares` field.
- `top_holdings` backend response currently does not expose shares either.

Deepseek should expose enough backend data for chart modes. Antigravity should
add zero-data empty states and robust chart mapping.

### Correction C: Notification Bell Contract Is Mismatched

Backend action items currently look like:

```json
{"id":"drafts-h","label":"holdings pending publish","count":1,"severity":"amber","href":"/holdings"}
```

Navbar currently expects:

```ts
item.title
item.description
item.link
```

Antigravity should either adapt the frontend to the backend shape or coordinate
with Deepseek to standardize the API. Prefer minimizing backend churn if the
backend contract is already tested.

### Correction D: Tooltip Component Already Exists

Do not create a duplicate `Tooltip.tsx`. Use the existing Radix wrapper:

```text
estate-portfolio-manager/src/components/ui/tooltip.tsx
```

### Correction E: Theme Toggle May Be A UX Contract Issue

`useTheme()` does use React state. The reported issue may be that the icon shows
the current resolved theme rather than the next action, especially when system
theme is dark. Antigravity must decide and document the UX rule:

- icon represents current state, or
- icon represents the action that will happen on click.

## Part 3: Backend Work For Deepseek v4

Priority order:

1. Normalize holdings lifecycle contract.
   - API should expose frontend-friendly `status: "LIVE" | "DRAFT"` if the UI
     filters by that field.
   - Backend persistence may continue using `holding_type`, but mapping must be
     explicit and tested.
2. Fix POST `/api/v1/holdings`.
   - Remove invalid model constructor fields.
   - Compute and persist `total_cost = num_shares * avg_purchase_price`.
   - Return 201 on successful create.
   - Preserve duplicate handling as 409.
3. Fix publish route contract.
   - Align method and result between frontend and tests.
   - If both `POST` and `PUT` need to be supported temporarily, document it.
4. Fix dashboard data needed for charts.
   - Ensure active/live holdings with value appear in `sector_allocation`.
   - Include shares in `top_holdings` if the UI supports "By Shares".
5. Add/repair backend tests.
   - POST success.
   - POST duplicate.
   - PATCH valid/invalid values.
   - Publish lifecycle.
   - Dashboard chart response fields.

## Part 4: Frontend Work For Antigravity/Gemini

Start only after backend contract choices are known, or work on isolated UI
state fixes first.

Priority order:

1. Fix inline edit cursor jumps.
   - Move edit form state into a row-local component or editable cell component.
   - Ensure Cancel is visible and clears local state without API call.
   - Ensure toggling global edit mode off exits row editing immediately.
2. Fix dashboard charts.
   - Include `shares` in `topHoldingsChartData`.
   - Filter zero-value chart rows or show a professional empty state.
   - Do not leave temporary `console.log` statements.
3. Fix notification bell rendering.
   - Use `label`, `href`, `count`, and `severity`, or coordinate a backend
     contract update.
   - Ensure click-outside close remains working.
4. Add tooltips using existing Radix tooltip components.
   - Theme toggle.
   - Edit mode toggle.
   - Add Holding.
   - Save, Cancel, Publish, Delete.
   - Chart toggles.
5. Clarify and implement theme icon behavior.

## Part 5: Grok Spotter Checklist

Grok should review without editing:

- Does backend expose the fields the frontend actually reads?
- Does frontend stop using fields the backend does not return?
- Does AT-003-2 label checks as `[DB]`, `[API]`, and `[UI]`?
- Are root docs preserved and EPM-local docs referenced from `docs/context/`?
- Are Docker/local deployment rules obeyed?

## Part 6: AT-003-2 Requirements

Create the next acceptance test at:

```text
docs/testing/acceptance-tests/AT-003-2.md
```

Use the 3-layer format:

```markdown
- [ ] [API] SC-UI-024: PATCH /api/v1/holdings/{id} returns 200 with valid payload
- [ ] [DB] SC-UI-024b: holdings table shows updated num_shares after save
- [ ] [UI] SC-UI-024c: row returns to read-only display with new values after save
```

Carry forward only unresolved failures and pending items from
`docs/testing/acceptance-tests/AT-003-1-followup-test.md`, plus any regression
guards required by changed code.

## Part 7: Verification Steps

1. **Test Command**:
   - Backend unit/integration command to be supplied by Deepseek after backend
     scope is finalized.
   - Frontend build/test command to be supplied by Antigravity after frontend
     scope is finalized.
   - Do not use local Docker.
2. **Expected Output**:
   - Holdings POST returns 201 and no 500.
   - Dashboard charts render or show intentional empty states.
   - Inline edit maintains cursor, Save persists, Cancel discards.
   - Notification bell shows count and navigable items when backend returns
     action items.
3. **If It Fails**:
   - Check API/frontend field mismatches first.
   - Check auth/session 401 separately from UI rendering bugs.
   - Check whether seed data has non-null prices/current values.
4. **Rollback**:
   - Revert only the sprint commit on `test`.
   - Do not roll back root infrastructure or shared database manually.

## Part 8: Next Handover

After implementation and AT-003-2, write:

```text
docs/handover/HO-019-deepseek-antigravity-to-claude.md
```

Include:

- Exact files changed.
- Tests run and outputs.
- Remaining AT failures.
- Any contract decisions made.

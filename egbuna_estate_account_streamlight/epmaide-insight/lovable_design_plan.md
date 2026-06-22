## Goal
Align the AI assistant widget with the spec. No visual redesign — same dark theme, lavender accent, rounded shapes; only behavior, dimensions, copy, and position change.

## Changes to `src/components/AiAssistant.tsx`

**1. Position & z-index**
- Container: `fixed bottom-6 right-6 z-[9999]` (was `left-6 z-50`).
- Stage 2 input bar animates from the right: swap `slide-in-from-left-2` → `slide-in-from-right-2`.
- Stage 3 panel anchors right edge (no layout change needed since container is now right-aligned).

**2. Launcher size**
- `h-12 w-12` → `h-[52px] w-[52px]`.

**3. Stage 2 input width**
- `width={340}` → `width={320}`.

**4. Placeholder copy**
- `"Ask EPM a question..."` → `"Ask about your portfolio..."`.

**5. Panel max-height**
- `max-h-[70vh]` → `max-h-[500px]`.

**6. Click-outside to collapse, preserving draft**
- Add a `ref` on the root widget container.
- Add a `mousedown` listener on `document` while `stage !== "launcher"`: if the click target is outside the container, call `setStage("launcher")`.
- Do NOT clear `value` (draft preserved) and do NOT clear `messages` (visual history preserved during the session).
- Keep existing `Escape` (Stage 2) and `X` button (Stage 3) close paths; both already preserve `value`.

**7. Loading state**
- Add `const [pending, setPending] = useState(false)`.
- Refactor `submit`:
  - Push the user message immediately, set `pending=true`, switch to `panel`, clear `value`.
  - After ~600ms (`setTimeout`), compute `answer(q)`, append it, set `pending=false`.
- In the messages list, when `pending` is true, render a small assistant-side loading row: three pulsing lavender dots (`bg-primary/60 animate-pulse` with staggered `animation-delay`) inside the same bubble container style as assistant replies.
- Disable the send button while `pending`.

**8. Recharts for inline charts**
- Replace the hand-rolled bars and SVG sparkline in `InlineChart` with Recharts:
  - `kind: "bars"` → horizontal `BarChart` with `Bar` filled `oklch(0.78 0.10 295)`, `YAxis` showing labels, no grid, minimal axes, `ResponsiveContainer` height ~ `items.length * 22 + 16`.
  - `kind: "spark"` → `AreaChart` with a single `Area` (stroke `oklch(0.78 0.10 295)`, fill `oklch(0.78 0.10 295 / 0.15)`), no axes, no tooltip, `ResponsiveContainer` height 50.
- Keep the existing card frame (`rounded-lg border border-border bg-background/40 p-3`) and the small uppercase title above the chart.
- Install dependency: `bun add recharts` (run once in build mode before edits compile).

## Things explicitly NOT changing
- Colors, fonts, radii, shadows, glow on the launcher, suggestion chips, message bubble styles, header layout, Sparkles icon usage, ArrowUp send icon, dark theme tokens in `src/styles.css`.
- `answer()` canned response content.
- `messages` lifecycle (kept in component state for the session; not persisted).

## Technical notes
- Click-outside uses `mousedown` (not `click`) so it fires before focus shifts and feels instant.
- The `setTimeout` fake-latency is local state only — no network, no backend. This is purely to satisfy the "loading spinner" spec for a read-only demo.
- Recharts is tree-shakeable; only `BarChart`, `Bar`, `YAxis`, `AreaChart`, `Area`, `ResponsiveContainer` are imported.
- `z-[9999]` uses an arbitrary Tailwind value — supported by Tailwind v4 with no config change.


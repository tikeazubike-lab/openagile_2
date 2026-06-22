# Lovable Prompt — EPM AI Assistant Widget

Paste everything below into Lovable as one prompt.

---

I want to add a floating AI assistant widget to my existing dashboard
(EPM — Estate Portfolio Manager, a dark-themed Nigerian stock portfolio
tracker). The dashboard already exists — don't redesign it, just add this
widget on top of it. Match the existing dark theme: near-black background,
soft lavender/purple as the primary accent, muted gray text, small green
"buy" pills, card-based layout with subtle borders.

The widget behaves in three stages, like a chat assistant that grows as
you use it — think of how Midday's AI assistant works, where it starts as
a tiny button and unfolds into a full conversation panel only once you
actually start typing.

**Stage 1 — Collapsed launcher**
A small round (or pill-shaped) button fixed to the bottom-left corner of
the screen, floating just above the sidebar's user profile footer. It
should NOT blend into the dark sidebar — give it a noticeably brighter
accent color (a glowing lavender or violet works well against the near-black
background) so it visually reads as "tap me" at a glance, the way a
notification dot or floating action button would. A simple sparkle, chat
bubble, or assistant-style icon sits centered inside it.

**Stage 2 — Input bar (on launcher click)**
Clicking the launcher rolls it out horizontally/vertically into a single-line
text input — small and unassuming, not a full chat window yet. It has a
light, soft-glowing border that contrasts gently against the dark
background (don't make it loud — a thin 1px light-gray or lavender-tinted
border is enough). Placeholder text reads "Ask EPM a question...". There's
a small submit affordance on the right side of the bar (an icon button, like
a paper plane or arrow). No chat history is visible yet at this stage —
it's just an inviting, minimal input.

**Stage 3 — Full panel (on first message sent)**
Once the user types a question and submits, the input bar expands upward
into a full assistant panel — roughly 380px wide, tall enough to show
several messages (cap around 70% of viewport height), with rounded corners
and a soft shadow so it floats above the dashboard content beneath it.
Structure top to bottom:
  - A small header strip at the top reading "Assistant" with a subtle
    sparkle/icon, and a close (X) button on the right to collapse back
    down to the launcher
  - A scrollable message area below that, showing the conversation —
    user messages and assistant replies in distinct bubble or block
    styles (assistant replies can include things like a short paragraph
    of text, and optionally a small inline chart if the answer involves
    portfolio numbers — e.g. a tiny sector allocation bar or trend line
    embedded directly in the reply, similar to how a financial assistant
    might show a small chart alongside its written answer)
  - The same input bar from Stage 2, now pinned to the bottom of this
    panel (not the bottom of the screen) so it stays attached as the
    conversation scrolls
  - A few faded, clickable suggestion chips above the input bar the
    first time the panel opens (e.g. "What's my biggest holding?",
    "Show my sector allocation", "Any dividends due this month?") to
    hint at what can be asked — these fade away once a real conversation
    starts

**Tone and feel**
Calm, minimal, financial-data-aware — not playful or cartoonish. This is
a serious portfolio tool, so the assistant should feel like a quiet,
competent feature tucked in the corner, not a flashy chatbot popup. No
bright primary colors beyond the one accent used for the launcher and
borders. Typography should match the rest of the dashboard — clean
sans-serif, generous spacing, numbers in a slightly monospace or tabular
style where relevant (matching how currency values already look elsewhere
in the dashboard).

**Important constraints**
- This is a read-only assistant for now — it only answers questions about
  existing portfolio data (holdings, dividends, sector allocation,
  transactions). Do not design any UI for attaching files or images, and
  do not design any buttons implying the assistant can edit, add, or
  change data. Text-in, text-out (plus the occasional inline chart in a
  reply) is the full scope.
- The widget should feel like it belongs to this dashboard, not like an
  embedded third-party chat plugin — same border radius, same shadow
  language, same spacing rhythm as the existing cards.
- Make sure the collapsed launcher (Stage 1) is the default/idle state
  shown when the page loads — the panel should never auto-open.

Please design all three stages so I can see the full interaction flow.

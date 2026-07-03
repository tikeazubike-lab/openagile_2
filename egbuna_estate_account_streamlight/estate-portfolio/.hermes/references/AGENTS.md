# EPM v2 — Agent Instructions

## Source of truth
Architecture, infra, CI/CD, branching, agent routing, and handoff rules are
defined in `Master_context_Claude_web.txt` at the project root. That file
is authoritative — if anything below conflicts with it, the file wins.

CRITICAL: Read `Master_context_Claude_web.txt` in full before any
architecture, infrastructure, or deployment task. Read `.context/` files
on a need-to-know basis per the references below.

## Detailed context (load lazily, only when relevant to the current task)
@.context/database-schema.md
@.context/api-contracts.md
@.context/deployment-notes.md

## Cross-agent handoff log
`.context/AGENT_LOG.md` is a shared, append-only log read by both OpenCode
and Hermes. Before starting non-trivial work:
  1. Read the last 5 entries in `.context/AGENT_LOG.md` for recent context
     from the other tool.
After completing non-trivial work (new spec, schema change, API change,
significant refactor):
  2. Append a dated entry to `.context/AGENT_LOG.md`: what changed, why,
     and what the next session (yours or the other tool's) needs to know.
Keep entries under 150 words. Do not duplicate what's already in
Master_context_Claude_web.txt — reference it instead.

## Execution constraints
Zero-execution rule applies on this workstation for Python/Node/Docker.
All builds, tests, and deploys run via GitHub Actions or the VPS. Never
suggest local execution unless explicitly requested.

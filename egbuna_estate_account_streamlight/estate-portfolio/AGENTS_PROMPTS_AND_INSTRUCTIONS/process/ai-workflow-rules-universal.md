# ai-workflow-rules.md
# UNIVERSAL FILE — copy unchanged between projects
# This file does not contain project-specific information

---

## The Execution Sequence (No Exceptions)

For every feature, in this exact order:

  1. Read all .context/ files (AGENTS.md first, then the rest)
  2. Read the assigned feature spec (.context/feature-specs/F-XXX.md)
  3. Write tests for the feature
  4. Run tests — confirm they FAIL (RED)
  5. Write minimum production code to make tests pass
  6. Run tests — confirm they PASS (GREEN)
  7. Run the 3-layer acceptance checklist [DB] [API] [UI]
  8. Update .context/progress-tracker.md
  9. Write handover brief → docs/handovers/HO-XXX.md

Skipping any step is not "maintaining velocity."
It is accumulating debt that requires a fix sprint later.

---

## Zone System

Zone 1 — Low Friction (automate directly):
  Triggers: "format", "generate", "draft", "boilerplate", "just give me"
  Action: implement directly, Architect reviews after

Zone 2 — Add Friction (design first, implement second):
  Triggers: "architect", "design", "why", "understand", new feature, unknown territory
  Action: stop, write analysis, send to Architect, wait for spec

DEFAULT IS ZONE 2.
When in doubt, treat the task as Zone 2.

---

## One Feature Unit at a Time

Never combine unrelated system boundaries in one session.

Wrong: "build the dividends API and also fix the dashboard chart bug"
Right: "build the dividends API" — full stop — handover — separate session for the bug

Each session produces one commit covering one feature or one bug.

---

## The Debug Protocol (Prevents the Fix Spiral)

When something is broken, strictly in this order:

  1. Capture the exact error — do not paraphrase it:
     Backend:  docker compose logs [service] --tail=50
     Frontend: DevTools Console → exact error message and stack trace
     API:      DevTools Network → exact request payload + exact response body
     Database: SQL query → exact row state

  2. Identify which layer failed: [DB] [API] [UI]

  3. Trace to the exact file and line responsible

  4. Write root cause analysis:
     - What is the error exactly?
     - Which file and line is responsible?
     - Why did this happen?

  5. Propose ONE fix plan:
     - What file changes are needed?
     - What is the expected outcome?

  6. Send to Architect. Wait for approval.

  7. Implement only after approval.

Never fix by trial and error.
Never change multiple things at once to see which one works.
The diagnosis step takes 5 minutes and prevents 2 hours of chasing symptoms.

---

## When a Decision Is Needed

If implementing a feature requires a design choice not covered by the spec:

STOP. Do not invent the answer.

Write a handover brief to the Architect:
  - What decision is needed
  - What the options are
  - What you recommend and why
  - What you will implement if no response comes

Architect responds with the locked decision. Then implement.

---

## Handover Brief Format (Every Session Ends With One)

---
type: HO
id: HO-XXX
title: [Agent] → [Agent]: [Topic]
date: YYYY-MM-DD
from: [Agent name + role]
to: [Agent name + role]
protocol: OpenAgile Hybrid Framework v1.0
---

## 1. What Was Done
[Specific files changed, commands run, tests executed]

## 2. What Is Verified Working
[Exact verification: command run + output seen — not "it works"]

## 3. What Is Broken / Uncertain
[Root cause if known — not "it's broken"]

## 4. Next Agent Action List
1. [numbered step]
2. [numbered step]

## 5. Blockers
[What cannot proceed until resolved]

---

## 3-Layer Acceptance Test Format

Every acceptance test item is prefixed with its verification layer:

  [DB]  — verify directly in the database
          How: connect to DB, run SQL query, check row state

  [API] — verify via curl or DevTools Network tab
          How: curl with auth token, or DevTools → Network → XHR

  [UI]  — verify in the browser
          How: open staging URL, interact, check Console + Network

Test in this order: [DB] → [API] → [UI]
DB confirms persistence.
API confirms contract.
UI confirms rendering.

---

## Acceptance Test Naming (Immutable Records)

AT-001        — first run of feature 1
AT-001-1      — follow-up run after fixes
AT-001-2      — second follow-up if more fixes needed
AT-002        — first run of feature 2

NEVER modify an existing AT file after it is written.
It is a historical record of the system state at that moment.
Create a new follow-up file instead.

---

## Agent File Domain Rules

Every project must define file domains in AGENTS.md.
Agents never touch files outside their domain.

When a feature requires both backend and frontend changes:
  Backend agent finishes and pushes first.
  Frontend agent pulls latest, then starts.
  Never both sides simultaneously in the same session.

---

## Hard Rules (Apply to Every Agent on Every Project)

  NO production code before RED tests
  NO implementation without a feature spec
  NO guessing at bug fixes — diagnose first, propose, wait for approval
  NO datetime.utcnow() — always use timezone-aware timestamps
  NO hardcoded secrets in source code
  NO force-push to main or production branches
  NO deployment without confirming staging works first

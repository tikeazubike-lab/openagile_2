# Phase 3 — Agent Setup

## What This Phase Produces
- Updated AGENTS.md with full agent registry
- Hermes personality blocks (paste into ~/.hermes/config.yaml)
- Cursor .cursor/rules/*.mdc files
- Session starter prompts per agent
- Handover protocol documented

---

## Questions to Ask (Group 1 — Agent Registry)

> "For each AI agent working on this project, define their domain.
>
> For each agent, I need:
> 1. Name (Antigravity, Deepseek v4, Cursor, Hermes, Claude Code, etc.)
> 2. Role (backend builder / frontend builder / tester / executor / architect)
> 3. Files they OWN (directories, specific files)
> 4. Files they must NEVER touch
> 5. How they report back (handover brief format? direct commit?)
>
> Start with your primary implementing agent:"

After each agent, confirm:
> "So [Agent] owns [files], never touches [files], and reports via
> [method]. Is that right?"

---

## Questions to Ask (Group 2 — Conflict Prevention)

> "When a feature needs both backend AND frontend changes,
> what is the push sequence?
>
>   a) Backend agent finishes and pushes → frontend agent pulls then starts
>      (recommended — frontend knows the exact API shape before building)
>   b) Both work simultaneously on separate branches → merge
>      (faster but risks API contract drift)
>   c) One agent does both (no conflict risk, but slower)
>
> And: if two agents accidentally edit the same file, what is
> the resolution process?"

---

## Questions to Ask (Group 3 — Communication Protocol)

> "The handover brief is how agents communicate state between sessions.
> Every session ends with one. Confirm the format:
>
> Standard HO format (5 sections):
>   1. What Was Done (specific files, commands, tests)
>   2. What Is Verified Working (exact evidence)
>   3. What Is Broken / Uncertain (root cause if known)
>   4. Next Agent Action List (numbered steps)
>   5. Blockers
>
> Filing location: docs/handovers/HO-XXX.md
> Naming: sequential HO-001, HO-002... (never reuse, never modify)
>
> Does this work for your project, or do you need extra sections?"

---

## Questions to Ask (Group 4 — Hermes Configuration)

Only ask if Hermes is in the agent list.

> "For Hermes, I'll generate personality blocks for your project.
> How many personalities do you need?
>
>   a) Builder — implements features, follows specs
>   b) Debugger — systematic root cause analysis only
>   c) Tester — writes and runs acceptance tests
>   d) Architect — designs but never implements
>   e) All of the above (recommended)
>
> What is the working directory on your server?
> (e.g. /home/zubbyik/openagile_2/project-name/)"

---

## Questions to Ask (Group 5 — Cursor Rules)

Only ask if Cursor is in the agent list.

> "For Cursor, I'll generate .cursor/rules/*.mdc files.
> Which domains need rules?
>
>   a) general.mdc — always active (project-wide rules)
>   b) backend.mdc — activates for backend/** files
>   c) frontend.mdc — activates for src/** files
>   d) infrastructure.mdc — activates for docker-compose, GitHub Actions
>
> All four is recommended. Any domain you want to skip?"

---

## Documents to Produce

1. Updated `.context/AGENTS.md` with full registry table
2. Hermes personality blocks — tell user to paste into `~/.hermes/config.yaml`
3. `.cursor/rules/general.mdc` — always-active rules
4. `.cursor/rules/backend.mdc` — backend domain rules
5. `.cursor/rules/frontend.mdc` — frontend domain rules (if applicable)
6. `.cursor/rules/infrastructure.mdc` — infra rules (if applicable)
7. Session starter prompt per agent:

```markdown
## [Agent Name] Session Starter Prompt

Read these files before doing anything:
1. .context/AGENTS.md
2. .context/project-overview.md
3. .context/architecture.md
4. .context/code-standards.md
5. .context/ai-workflow-rules.md
6. .context/ui-context.md  [frontend only]
7. .context/progress-tracker.md
8. .context/current-issues.md  [if exists]
9. .context/feature-specs/[assigned feature].md

Your assigned task: [fill in per session]
```

---

## Phase 3 Checklist

```
Agent Registry:
[ ] Every agent has a defined file domain
[ ] Every agent has a defined anti-domain
[ ] Push sequence defined for multi-agent features
[ ] Conflict resolution process documented

Communication:
[ ] HO-XXX format in ai-workflow-rules.md
[ ] Naming convention established (HO-001 sequential)
[ ] Filing location confirmed (docs/handovers/)

Hermes (if applicable):
[ ] Personality blocks written for all required roles
[ ] Working directory set in config.yaml cwd
[ ] show_cost: true set (track model costs)

Cursor (if applicable):
[ ] .cursor/rules/ directory created
[ ] general.mdc written (alwaysApply: true)
[ ] Domain-specific .mdc files written

Session Starters:
[ ] Session starter prompt written for each agent
[ ] User can paste prompt and agent knows what to do immediately
```

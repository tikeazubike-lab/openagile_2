# AGENT_ROLES.md

## Role Registry

### Claude — The Brain (Architect)
- Sole architectural authority
- Produces: design documents, handover briefs (HO-*), API contracts,
  Gherkin feature files, STLC specs, Lovable prompts, this registry
- Reviews: all agent handovers before action is taken
- Never writes production code
- Never runs commands locally or on server
- Zone classification: always Zone 2 (add friction) unless told otherwise
- Handover format: structured HO-* document with 5 mandatory sections

### Antigravity — The Builder (Backend + Infrastructure)
- Implements: FastAPI, SQLAlchemy, Alembic, GitHub Actions, Docker
- Owns files: backend/**, docker-compose.yml, .github/workflows/**
- Never executes locally: no pip, npm, docker, pytest on Fedora workstation
- Verifies via: SSH to VPS (read/diagnose only) or GitHub Actions logs
- Deploys via: git push → GitHub Actions only
- Must: use quoted heredoc << 'ENDSSH' in all SSH scripts
- Must: write failing test first (RED) before production code (GREEN)

### Deepseek v4 — The Builder (Frontend)
- Implements: React 18, TypeScript, TanStack Router, Tailwind v4
- Owns files: estate-portfolio-manager/src/**
- Same local execution constraints as Antigravity
- Conflict rule: Antigravity pushes backend first → Deepseek v4 pulls → fixes frontend
- Must follow: oklch colour tokens, null-safe rendering, credentials: 'include' on all fetch calls

### Codex — The Tester
- Executes tests via SSH to VPS on test branch only
- Never merges to main or develop
- Never writes production app code
- Produces: handover reports with test execution results + drift analysis

### Lovable — The UI Generator
- Generates React 18 + TypeScript + Tailwind v4 from Claude's prompt spec
- Outputs to GitHub PR → Antigravity reviews
- Known limitation: defaults to Supabase — must be overridden in every prompt
- Antigravity review checklist: no supabase imports, relative /api/v1/ paths,
  no localStorage JWT, Vite outputs to dist/

### Grok — The Spotter
- Verifies Claude's designs against real-world tool capabilities
- Checks: library versions, known gotchas, capability audits
- Never overrides Claude's architectural decisions
- Never produces implementation code

### Owner (Zubby) — Product Owner
- Direction, decisions, UAT sign-off
- Provides: NGX PDF files, Obsidian vault updates, acceptance test results
- Controls: GitHub secrets, VPS access, branch merges to main

## Handover Protocol (All Agents)
Every handover document must include:
1. What was done (specific files, commands, tests)
2. What is verified working (exact results with numbers)
3. What is broken / uncertain (root cause if known)
4. What receiving agent must do next (numbered list)
5. Blockers

## Handover Naming Convention
```
HO-001, HO-002, ... — sequential, never reused
AT-003, AT-003-1, AT-003-2 — follow-up runs of same test suite
AT-004 — new feature, new test suite
```

## Agent Conflict Resolution
- File domain separation: Antigravity owns backend/, Deepseek v4 owns src/
- Antigravity pushes backend first; Deepseek v4 pulls before starting frontend
- Both push to test branch
- Claude arbitrates if design conflict arises
- Past assistance is not authorization — every session re-reads context

## NEVER Rules (All Agents)
1. Context-blind generics (always read MASTER_CONTEXT first)
2. "Just spin up another X" (check existing services first)
3. Incomplete code ("# rest here")
4. Tutorial preamble
5. Placeholder hell (YOUR_API_KEY)
6. Orphaned code without handover brief
7. Skip RED phase (tests must fail before code is written)
8. Edit files directly on VPS server
9. Deploy via SSH (GitHub Actions only)
10. Upgrade bcrypt above 4.0.1


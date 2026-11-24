# Phase 2 — Architecture Decisions

**Goal**: produce `.context/architecture.md`, `.context/code-standards.md`, and the first ADRs
in `docs/decisions/`. This is the phase most likely to need a Mermaid diagram — always include
one in `architecture.md`.

## Questions to ask (2–3 at a time)

Round 1:
1. Monolith, modular monolith, or services? (explain trade-offs briefly if user is unsure)
2. Primary language/framework?

Round 2:
3. Data store(s) — relational, document, both, none yet?
4. Auth approach — none needed, session-based, token-based, third-party (OAuth)?

Round 3:
5. Any component you already know you want isolated (e.g. "payments must be its own service")?
6. Local dev environment: Docker Compose, bare metal, other?

## Output

Write `.context/architecture.md` with a Mermaid component diagram, e.g.:

```markdown
# Architecture

## Components

​```mermaid
flowchart LR
    Client --> API[API Layer]
    API --> DB[(Database)]
    API --> Auth[Auth Service]
​```

## Decisions
- <language/framework, with the "why">
- <data store, with the "why">
- <auth approach, with the "why">

## Local Development
<Docker Compose / bare metal answer>
```

For each non-trivial decision, also write an ADR to `docs/decisions/ADR-XXX.md` using
`assets/adr-template.md`. Number sequentially starting at ADR-001.

Write `.context/code-standards.md` — keep it short: linting/formatting tool, commit message
convention, branch naming. Ask the user only if they have strong preferences; otherwise propose
sensible stack-appropriate defaults and let them confirm or override.

## Checklist before moving to Phase 3

- [ ] `.context/architecture.md` written with a Mermaid diagram
- [ ] At least one ADR written for the biggest architectural decision
- [ ] `.context/code-standards.md` written and confirmed

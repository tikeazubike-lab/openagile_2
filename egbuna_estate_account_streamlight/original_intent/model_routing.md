# MODEL_ROUTING.md

## Model-to-Role Assignments

| Model | Role | Strengths Used |
|-------|------|----------------|
| Claude (Sonnet) | The Brain — Architect | Deep reasoning, architecture, documentation, Gherkin specs, handover design |
| Antigravity (Gemini Pro) | Builder — Backend + Infra | File system access, multi-file edits, FastAPI, Docker, GitHub Actions |
| Deepseek v4 | Builder — Frontend | React 18, TypeScript, Tailwind v4, TanStack ecosystem |
| Codex (OpenAI) | Tester | Codebase investigation, test migration, execution via SSH |
| Lovable.dev | UI Generator | React component generation from natural language prompts |
| Grok | Spotter | Current trends, library version verification, real-world tool audits |

## Routing Logic

### Zone 1 Tasks (Automate — mechanical, precedent exists)
- Triggers: "format", "generate", "draft", "boilerplate", "just give me"
- Route: Antigravity or Deepseek v4 (implement directly)
- Claude role: review + document after

### Zone 2 Tasks (Add friction — architecture or learning required)
- Triggers: "architect", "design", "why", "understand", "critique", "learn"
- Route: Claude (design) → Grok (verify) → Antigravity/Deepseek v4 (implement)
- Default: Zone 2 unless explicitly told otherwise

### UI Generation Pipeline
- Claude writes Lovable prompt (self-contained, single document)
- Lovable generates React code → GitHub PR
- Antigravity reviews PR (strip Supabase, verify API paths)
- Antigravity merges to test branch

### Debugging Pipeline
- Antigravity diagnoses via SSH to VPS (never locally)
- Claude performs root cause analysis
- Grok verifies if known library issue
- Antigravity implements fix and pushes

### Testing Pipeline
- Claude writes STLC spec + Gherkin feature files
- Codex migrates + executes tests on test branch via SSH
- Codex handover → Claude reviews drift
- Antigravity fixes backend gaps

## Cost / Resource Constraints
- Local Fedora workstation: kernel OOM on Python/Node execution
  → All execution routed to GitHub Actions (cloud) or VPS
- VPS: 16GB RAM, 8 vCPU — adequate for all execution tasks
- No GPU on VPS:
  → faster-whisper rejected (OOM)
  → whisper.cpp with small model as alternative
- GitHub Actions: free tier with test schema isolation (no new containers)

## Model Handoff Rules
- Claude never starts implementing before design is locked
- Antigravity never starts backend before Gherkin RED phase confirmed
- Deepseek v4 never starts frontend before backend endpoints are stable
- Lovable never touches backend or Supabase
- Codex never merges to main
- Past Claude output is not authorization to skip current review

## Information Routing
- Claude → agents: HO-* handover documents (structured, numbered)
- Agents → Claude: HO-* handover documents (same format)
- User → Claude: acceptance test results (AT-*.md), product decisions
- Claude → user: architectural decisions, clarifying questions (max 3 at a time)


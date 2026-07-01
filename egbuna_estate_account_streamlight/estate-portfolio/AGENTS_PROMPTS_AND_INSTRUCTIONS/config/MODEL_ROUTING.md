# MODEL_ROUTING.md

## Model-to-Role Assignments

| Model | Role | Strengths Used |
|-------|------|----------------|
| DeepSeek (openrouter/deepseek/deepseek-v4-flash) | The Brain — Architect | Deep reasoning, architecture, documentation, Gherkin specs, handover design |
| Deepseek:flash (openrouter/deepseek/deepseek-v4-flash) | Builder — Backend + Infra | File system access, multi-file edits, FastAPI, Docker, GitHub Actions |
| nemotron-3-ultra-550b-55b:free (openrouter/nemotron/nemotron-3-ultra-550b-a55b:free) | Builder — Frontend | React 18, TypeScript, Tailwind v4, TanStack ecosystem |

## Routing Logic

### Zone 1 Tasks (Automate — mechanical, precedent exists)
- Triggers: "format", "generate", "draft", "boilerplate", "just give me"
- Route: Deepseek:flash or nemotron-3-ultra-550b-55b:free (implement directly)
- DeepSeek role: review + document after

### Zone 2 Tasks (Add friction — architecture or learning required)
- Triggers: "architect", "design", "why", "understand", "critique", "learn"
- Route: DeepSeek (design) → Deepseek:flash/nemotron-3-ultra-550b-55b:free (implement)
- Default: Zone 2 unless explicitly told otherwise

### UI Generation Pipeline
- DeepSeek writes Lovable prompt (self-contained, single document)
- Lovable generates React code → GitHub PR
- Deepseek:flash reviews PR (strip Supabase, verify API paths)
- Deepseek:flash merges to test branch

### Debugging Pipeline
- Deepseek:flash diagnoses via SSH to VPS (never locally)
- DeepSeek performs root cause analysis
- Deepseek:flash implements fix and pushes

### Testing Pipeline
- DeepSeek writes STLC spec + Gherkin feature files
- Deepseek:flash migrates + executes tests on test branch via SSH
- Deepseek:flash handover → DeepSeek reviews drift

## Cost / Resource Constraints
- Local Fedora workstation: kernel OOM on Python/Node execution
  → All execution routed to GitHub Actions (cloud) or VPS
- VPS: 16GB RAM, 8 vCPU — adequate for all execution tasks
- No GPU on VPS:
  → faster-whisper rejected (OOM)
  → whisper.cpp with small model as alternative
- GitHub Actions: free tier with test schema isolation (no new containers)

## Model Handoff Rules
- DeepSeek never starts implementing before design is locked
- Deepseek:flash never starts backend before Gherkin RED phase confirmed
- nemotron-3-ultra-550b-55b:free never starts frontend before backend endpoints are stable
- Lovable never touches backend or Supabase
- Deepseek:flash never merges to main
- Past DeepSeek output is not authorization to skip current review

## Information Routing
- DeepSeek → agents: HO-* handover documents (structured, numbered)
- Agents → DeepSeek: HO-* handover documents (same format)
- User → DeepSeek: acceptance test results (AT-*.md), product decisions
- DeepSeek → user: architectural decisions, clarifying questions (max 3 at a time)
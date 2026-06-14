# ORCHESTRATOR MISSION CONTEXT

## Agent Registry

| Agent | Prompt File | State Key | Scope |
|-------|-------------|-----------|-------|
| **Orchestrator** | [ORCHESTRATOR_AGENT.md](./agents/ORCHESTRATOR_AGENT.md) | `agents.orchestrator` | Coordinates all agents |
| **Investigator** | [INVESTIGATOR_AGENT.md](./agents/INVESTIGATOR_AGENT.md) | `agents.investigator` | Reads reference projects, `<TARGET_PROJECT>`, and `MASTER_CONTEXT.md` |
| **Builder** | [BUILDER_AGENT.md](./agents/BUILDER_AGENT.md) | `agents.builder` | Implements changes inside `<TARGET_PROJECT>` ecosystem |

## State File
**Location:** [AGENT_STATE.yaml](./AGENT_STATE.yaml)

All agents must read and update this file to maintain workflow coordination.

## Workflow Sequence & Zone Delegation
The pipeline operates strictly under the Master Prompt Framework v4.0 (Zone 1/Zone 2 delegation).
```
1. INVESTIGATOR (Zone 2) → Investigates references and outputs INFRASTRUCTURE_CONTRACT.md
2. ORCHESTRATOR (Zone 2) → Cross-checks against MASTER_CONTEXT.md and produces BR/IMPLEMENTATION_PLAN.md
3. BUILDER (Zone 1) → Auto-executes approved plans directly inside <TARGET_PROJECT>
4. ORCHESTRATOR (Zone 2) → Validates completion and triggers Handover documentation
```

---

## ⚡ Platform Migration: Antigravity (Feb 2026)

> [!IMPORTANT]
> The agent system has been **migrated to Antigravity** — a full-capability agentic AI with **no license limitations**. All previous constraints around model compatibility, rate limits, and feature restrictions no longer apply.

### Previous State (Pre-Feb 2026)
- Agents were designed for **Claude free version** and **Gemini CLI without pro license**
- License limitations were treated as **architectural forces** that shaped prompt design
- Prompts were intentionally model-agnostic to support handoff between constrained models
- Rate limits, token limits, and missing features influenced workflow sequencing

### Current State
- **Platform:** Antigravity (unrestricted)
- **License:** No limitations — full capability access
- **Tools:** File system, terminal, browser, code search, web search, image generation
- **Memory:** Persistent Knowledge Items (KIs) and conversation history across sessions
- **Execution:** Autonomous planning, implementation, and verification
- **Context:** Unlimited — no token window constraints

### What This Means for the Agent System
1. **No model-switching overhead** — Antigravity handles all agent roles (Investigator, Builder, Orchestrator)
2. **No prompt compatibility constraints** — structured format is retained for clarity, not necessity
3. **Full tool access** — agents can directly execute commands, edit files, and validate deployments
4. **Persistent state** — Knowledge Items replace manual state management between sessions
5. **No rate-limiting workarounds** — all operations execute without artificial delays or batching

---

## Original Mission Context (ChatGPT Transcript)

> [!NOTE]
> The following transcript is preserved as **historical context** documenting how the multi-agent architecture was conceived. The constraints discussed (license limits, model-switching, capability gaps) have been **superseded** by the Antigravity migration above.


Skip to content
Chat history
You said:
You are an agent[Gemini Cli without pro license and Gemini-3 pro(high) ] that worked on a project that would have generated so many documents, including agent files, contextual files and many other artifacts that would have been useful for any other agent that might want to work on it using a different model, for example[Antigravity without pro license and Gemini-3 pro(high), Claude opus and Claude sonnet] . Your role is a go between to the next agent that would work on it, investigate, if possible reverse engineer(and i mean using the existing artifact to generate a detailed instruction of how the project was set up so far, the difficult situations and how they were resolved. Write a better prompt that would enable the initial agent to be able to act as an Architect and tell a professional story or describe the project in detail, pointing out the steps, the nuances, difficulties and how they were resolved. 
ChatGPT said:

You’re asking for something subtle and powerful: a handover narrative prompt that lets one agent reconstruct a complex project from artifacts alone, then retell it as an architect’s story—decisions, dead ends, trade-offs, and resolutions—so another agent (with a different model, constraints, or strengths) can continue the work without amnesia.

Think of this as writing the field notes + blueprint legend for a ruined but still intelligible city.

I’ll do three things:

    Frame the handover philosophy (what the next agent must infer, not assume).

    Describe the reverse-engineering method using existing artifacts.

    Give you a production-grade prompt you can hand to the initial agent, rewritten so it behaves like a true architect and historian of the project.

1. What the next agent actually needs (and usually doesn’t get)

Most agent handovers fail because they pass outputs, not intent.

A useful handover must preserve:

    Why the project exists (original constraints, goals, non-goals).

    What models/tools were available and which were not (license limits matter).

    How the system evolved over time (initial plan vs reality).

    Where friction occurred (rate limits, hallucinations, missing APIs, cost ceilings).

    Which decisions were reversible and which were hard commitments.

    What artifacts are canonical vs experimental or abandoned.

Artifacts without narrative are just fossils. Narrative without artifacts is fiction. You want both braided together.
2. Reverse-engineering method for the go-between agent (your role)

As the intermediary agent, you are not “continuing” the project. You are archaeology + translation.

Here’s the working theory the go-between agent should follow:

    Inventory first, interpret later

        Enumerate all artifacts: agent files, context files, prompts, configs, logs, partial outputs.

        Classify them by role: planning, execution, evaluation, discarded.

    Reconstruct the execution graph

        Infer order of operations: what had to exist before something else made sense.

        Identify feedback loops (prompt → output → correction → revised prompt).

    Identify constraint pressure points

        Where did lack of Pro features force design changes?

        Where did model behavior shape architecture (token limits, reasoning depth, style)?

    Extract decision rationales

        Look for language like “we chose X because…”, even if implicit.

        If absent, infer from trade-offs visible in the artifacts.

    Surface unresolved tensions

        Open questions.

        Known limitations.

        “This works, but feels wrong” areas.

    Translate into an architect’s narrative

        Not a changelog.

        Not a tutorial.

        A professional story: intent → attempt → resistance → adaptation → outcome.

That’s the mindset your rewritten prompt must enforce.
3. The improved Architect-level prompt (core deliverable)

Below is a clean, model-agnostic prompt you can reuse.
It is written to make the initial agent behave like an architect, historian, and systems thinker—not a chatty assistant.
Architectural Handover & Project Reconstruction Prompt

    You are acting as the original system architect and lead agent of this project.

    Your task is to reconstruct and formally describe the project using only the existing artifacts provided (agent files, contextual documents, prompts, logs, partial outputs, and related materials).

    Treat these artifacts as authoritative evidence. Do not invent components that are not supported by them. Where uncertainty exists, explicitly label it as inferred.

Your objectives:

    Reconstruct the Project Intent

        Explain the original problem the project set out to solve.

        State explicit constraints (technical, licensing, cost, model access, tooling).

        Clarify non-goals and rejected directions if they can be inferred.

    Describe the System Architecture

        Identify the major components (agents, prompts, workflows, tools).

        Explain how information flowed between them.

        Note which components were stable vs experimental.

    Narrate the Project Evolution

        Describe how the initial design changed over time.

        Highlight moments where reality (model behavior, limits, errors) forced adaptation.

        Explain why certain architectural decisions were made instead of plausible alternatives.

    Document Difficulties and Resolutions

        Clearly identify technical, conceptual, or coordination challenges.

        Explain how each was addressed or mitigated.

        If a problem was only partially solved, say so.

    Clarify Model-Specific Considerations

        Explain how available models (e.g., non-Pro Gemini CLI, Gemini-3 Pro, Claude variants) influenced design.

        Note behaviors, strengths, or weaknesses that shaped prompts or workflows.

    Assess the Current State

        What works reliably.

        What is fragile or incomplete.

        What assumptions the system currently depends on.

    Prepare a Forward-Looking Handover

        Explicitly state what a new agent should understand before continuing.

        Highlight areas safe for refactoring versus areas that require caution.

        Suggest logical next steps without prescribing a single path.

Style and Standards:

    Write as a professional architect’s report, not a tutorial or marketing summary.

    Be precise, calm, and explicit about uncertainty.

    Prefer explanation over instruction.

    Avoid hype, anthropomorphism, or narrative fluff.

    Use structure and clear sectioning so another agent can quickly orient itself.

    Your output should make it possible for a different agent, using a different model and constraints, to continue this project without needing to rediscover its history through trial and error.

Why this works (the meta-reasoning)

This prompt does three critical things most prompts don’t:

    It forces evidence-based reconstruction, not creative filling-in.

    It separates intent, architecture, evolution, and state, which prevents confusion.

    It acknowledges model limitations as first-class design forces, which is essential when switching agents.

In other words, it turns “here’s a pile of files” into “here’s the story of a system under pressure.”

If you want, the next step could be crafting a companion checklist the receiving agent uses to validate whether the reconstruction is sufficient—or a diff-style handover comparing “what was intended” vs “what actually shipped.”
You said:
now based on the written upgraded prompt, write another prompt that would help the same Agent infer and use the present project as reference for knowing how to use the infrastructure discovered from the result of the above prompt to build a new project. For example in the existing project a frappe-erpnext was built using Docker, Docker compose, Traefik, postgres, redis that is also presently running. A new project will use the existing infrastructure to build a Ghost blog site and some of the required infrastructures are listed as follows:

**Architecture**: Headless Ghost CMS + React (Vite) Frontend.
**Infrastructure**: Dockerized, integrated with OpenAgile ecosystem (Traefik, Shared Postgres).
ChatGPT said:

Excellent. Now we’re moving from archaeology to reuse without cargo-culting.

What you want here is a second-order prompt: one that assumes the agent has already produced the Architectural Handover & Project Reconstruction and can now treat that output as living infrastructure knowledge, not just documentation.

This prompt must force the agent to:

    Reuse patterns, not blindly copy services

    Respect running systems (Frappe/ERPNext is live)

    Infer integration contracts (Traefik labels, networks, Postgres roles, Redis usage)

    Design a new project that is compatible, isolated, and reversible

Below is a production-grade prompt that does exactly that.
Prompt: Infrastructure Reuse & New Project Design (Architect Mode)

    You are the same system architect who produced the Architectural Handover & Project Reconstruction for the existing infrastructure.

    You now have a second task: design and plan a new project that reuses the existing infrastructure safely and intentionally, using the reconstructed project as your primary reference.

Context You Must Assume

    The existing system (e.g., Frappe/ERPNext) is running in production.

    Core shared infrastructure already exists and must not be broken:

        Docker & Docker Compose

        Traefik as reverse proxy / ingress

        Shared Postgres instance

        Redis (possibly multi-purpose)

    The infrastructure is part of a broader OpenAgile ecosystem and may host multiple services over time.

The new project to be introduced is:

    Application: Headless Ghost CMS + React frontend (Vite)

    Deployment model: Fully Dockerized

    Integration requirements:

        Uses Traefik for routing and TLS

        Reuses shared Postgres (with proper isolation)

        Coexists with existing services without disruption

Your Objectives
1. Infer the Existing Infrastructure Contract

Using the reconstructed project documentation:

    Identify:

        Docker networks in use

        Traefik routing conventions (labels, entrypoints, middleware)

        Database access patterns (users, schemas, ports)

        Naming conventions and compose structure

    Explicitly state implicit rules (things that would break the system if violated).

Do not restate everything—extract what is relevant for reuse.
2. Define Reuse vs Isolation Boundaries

For each shared component (Traefik, Postgres, Redis, Docker network):

    Decide:

        What can be safely shared

        What must be isolated (users, schemas, volumes, containers)

    Justify each decision briefly in architectural terms (blast radius, security, maintainability).

3. Design the New Project Architecture

Describe the Ghost + React system as it should exist within this ecosystem, including:

    Service decomposition (Ghost, frontend, optional build container)

    Data flow between components

    External exposure (domains, routes, TLS)

    Internal-only services

This should read like an architect explaining a system to another engineer—not a tutorial.
4. Map the Architecture to the Existing Infrastructure

Explain how the new project plugs into what already exists:

    Traefik:

        Routing strategy

        Hostnames / subdomains

        Label patterns aligned with the existing system

    Postgres:

        Database and role strategy

        Migration/initialization approach

    Docker:

        Network attachment

        Compose file structure (new file vs extension vs stack)

Call out anything that must be coordinated carefully to avoid downtime.
5. Identify Risks and Mitigations

Explicitly list:

    Potential conflicts with the existing ERPNext system

    Resource contention risks

    Upgrade or rollback concerns

Provide mitigation strategies, not generic warnings.
6. Produce a Forward Plan (Not a How-To)

End with a clear, ordered plan for introducing the new project safely:

    Preparation steps

    Deployment phases

    Validation checkpoints

Do not include copy-paste commands unless they clarify architecture.
Focus on decisions, sequencing, and dependencies.
Style and Constraints

    Write as a senior infrastructure architect documenting a system evolution.

    Assume the reader is technically competent.

    Be explicit about assumptions and uncertainties.

    Prefer reasoning over verbosity.

    Do not invent infrastructure that was not present in the reconstructed project.

    Your output should enable a future agent—or human engineer—to build the new Ghost + React project using the existing infrastructure as a stable foundation, without reverse-engineering it again or risking the running system.

Why this prompt works

This prompt deliberately:

    Treats infrastructure as a shared organism, not a blank slate

    Forces the agent to extract rules from the old system

    Prevents “just spin up another stack” thinking

    Produces a design narrative, not YAML soup

If you want, the next logical refinement would be:

    A compose-file skeleton generator prompt that follows the inferred rules

    Or a Traefik contract spec prompt that formalizes routing once and for all

Both would slot neatly into this chain.
You said:
The next prompt is a modification of the second upgraded prompt, but this time, it is working on an existing project that wasn't planned properly. It will use the second prompt to compare and as a guide for what should be vs what is existing, and how to get it back on the right track. This existing project has the intention of building a production grade project, but did not plan accurately enough. So it will investigate the present project to know why it is not working by comparing it to what it should be based on the reference to the knowledge of the first prompt
ChatGPT said:

Good. This is the moment where the agent stops being an architect of new cities and becomes a forensic engineer called in after the bridge is already bending.

What you want is a diagnostic + realignment prompt.
Not a teardown, not a rebuild fantasy—an honest comparison between:

    What this project should look like (derived from the reconstructed reference system)

    What it actually looks like

    How to move from here to there without detonating production

Below is a carefully modified prompt that sits on top of the second upgraded prompt and explicitly uses it as a normative baseline.
Prompt: Project Forensics, Architectural Drift Analysis & Realignment

    You are the same system architect who:

        Reconstructed the original infrastructure and project history, and

        Designed a clean, infrastructure-aligned reference architecture for introducing new projects into that ecosystem.

    You are now tasked with analyzing an existing but poorly planned project that was intended to be production-grade but is currently unstable, inconsistent, or failing.

This project already exists. It was not designed with sufficient architectural foresight.

Your role is not to start over, but to:

    Diagnose why it is not working,

    Compare it against what it should be, and

    Propose a realistic path back to architectural sanity.

Inputs You Must Use

    The reconstructed reference infrastructure from the first prompt.

    The ideal reuse-based architecture from the second prompt.

    The current project artifacts (Docker files, compose files, configs, logs, routing rules, partial documentation, etc.).

Treat the second prompt’s output as the architectural baseline for how this project ought to integrate with the ecosystem.
Your Objectives
1. Establish the Intended vs Actual Architecture

Briefly state:

    What the project intended to be (as inferred from artifacts).

    What it actually is in practice.

Avoid judgment. This is factual framing.
2. Perform Architectural Drift Analysis

Compare the current project against the reference architecture and identify:

    Missing components

    Misused shared infrastructure

    Incorrect assumptions about Traefik, Postgres, Docker networks, or service boundaries

    Violations of implicit infrastructure contracts

Group findings into:

    Structural issues (architecture-level)

    Configuration issues (fixable without redesign)

    Process issues (how it was built or evolved)

3. Identify Root Causes (Not Just Symptoms)

For each major problem:

    Explain why it likely occurred
    (e.g. premature optimization, misunderstanding shared infra, copy-paste Compose files, lack of sequencing).

    Distinguish between:

        Design debt

        Implementation errors

        Missing knowledge at the time of construction

This section should read like a postmortem without blame.
4. Assess Production Risk

Evaluate:

    What can break if changes are applied incorrectly

    Which parts of the system are safe to modify now

    Which parts require careful sequencing or temporary duplication

Explicitly identify any red lines: changes that should not be attempted in-place.
5. Define the Target “Corrected” Architecture

Using the reference design as a guide:

    Describe what the project should look like after correction

    Be explicit about:

        Service boundaries

        Integration points with shared infrastructure

        What remains shared vs isolated

This is a north star, not yet a step-by-step plan.
6. Propose a Realignment Strategy

Lay out a pragmatic recovery path:

    Phase 1: Stabilization (stop the bleeding)

    Phase 2: Alignment (bring components into compliance)

    Phase 3: Hardening (make it truly production-grade)

Each phase should:

    Minimize downtime

    Avoid unnecessary rewrites

    Respect the running ecosystem

7. Highlight Lessons for Future Projects

Conclude by extracting:

    The key architectural mistakes that led to drift

    The signals that were missed early

    The rules that should be made explicit next time

This section ensures the ecosystem matures, not just this project.
Style and Tone Requirements

    Write as a senior architect conducting a recovery assessment.

    Be precise, calm, and technical.

    Avoid moralizing language (“wrong”, “bad”); prefer causal explanations.

    State uncertainty explicitly where evidence is incomplete.

    Do not provide copy-paste fixes unless they clarify architecture.

    Your output should make it possible for another engineer or agent to understand why this project drifted, what “correct” looks like, and how to bring it back on course without burning everything down.

Why this is the right modification

This prompt does something rare and valuable:

    It treats bad architecture as a historical process, not incompetence.

    It uses the ideal design as a measuring instrument, not a cudgel.

    It forces the agent to separate fixable misconfigurations from structural debt.

    It creates a path forward that respects reality, not greenfield fantasies.

At this point, you’ve built a full agent ladder:

    Reconstruction (what exists, how it came to be)

    Reuse design (how new work should be done)

    Forensic correction (how to rescue work that went off-script)

That’s not just prompting—that’s institutional memory encoded in language.
You said:
The last prompt is the orchestrator, the link between all the prompts[agents], and it will coordinate, inform and guide each of the prompts[Agents] so that the whole workflow will be able to communicate with each other
ChatGPT said:

Now we crown the system with its nervous system.

What you’re asking for is not “another prompt” in the casual sense. This is the Orchestrator Charter: the meta-agent that enforces coherence, sequencing, and shared truth across all other agents. If the previous prompts are specialists, this one is the chief architect, program manager, and historian rolled into one—without doing their jobs for them.

It must:

    Maintain a single source of truth

    Control information flow between agents

    Prevent drift, contradiction, and amnesia

    Decide when an agent runs, why, and with what inputs

    Ensure outputs are consumable by the next agent

Below is the orchestrator prompt, designed to sit above all others.
Prompt: Multi-Agent Orchestrator for Architectural Reconstruction, Reuse & Recovery

    You are the Orchestrator Agent for a multi-stage architectural analysis and recovery workflow.

    Your responsibility is not to perform deep technical analysis yourself, but to coordinate, constrain, and align a set of specialized agents so they function as a single, coherent system.

You oversee the following agents:

    Reconstruction Agent
    Reconstructs project intent, architecture, evolution, and current state from artifacts.

    Reuse Architecture Agent
    Designs how new projects should be built using the reconstructed infrastructure as a stable foundation.

    Forensic Recovery Agent
    Analyzes an existing, poorly planned project by comparing it against the reference architecture and proposes a path back to alignment.

Each agent has its own prompt and role. You must ensure they operate in the correct order, with the correct inputs, and with compatible assumptions.
Your Core Responsibilities
1. Enforce a Single Source of Truth

    Treat the Reconstruction Agent’s output as the canonical description of:

        Existing infrastructure

        Constraints

        Implicit contracts

    Prevent later agents from contradicting it.

    If contradictions arise, flag them explicitly as unresolved uncertainties.

2. Control Information Flow Between Agents

You must:

    Pass only relevant, distilled outputs to downstream agents.

    Remove narrative excess while preserving:

        Architectural decisions

        Constraints

        Known risks

    Explicitly label:

        Assumptions

        Inferences

        Unknowns

Each agent should receive:

    What it needs

    Why it needs it

    What it must not assume

3. Sequence the Workflow

You must run agents in this order:

    Reconstruction

    Reuse Architecture

    Forensic Recovery (only if an existing project is being analyzed)

Do not allow:

    Reuse design without reconstruction

    Recovery analysis without a reference architecture

4. Maintain Architectural Consistency

Actively watch for:

    Naming inconsistencies

    Conflicting interpretations of shared infrastructure

    Drift in assumptions about Traefik, Docker, Postgres, Redis, or network boundaries

When detected:

    Pause progression

    Summarize the conflict

    Propose clarification before proceeding

5. Translate Outputs into Agent-Consumable Briefs

For each agent transition, produce a handover brief that includes:

    Key findings

    Constraints to respect

    Open questions

    Non-negotiables

These briefs must be concise, factual, and structured.
6. Decide When the Workflow Is “Complete”

You are responsible for declaring when:

    The system is sufficiently understood

    The target architecture is clearly defined

    A safe recovery or extension path exists

Completion does not require perfection—only:

    Coherent understanding

    Explicit risks

    Actionable next steps

Operating Rules

    You do not redesign systems yourself.

    You do not override specialist agents.

    You do challenge unclear reasoning.

    You do surface ambiguity instead of hiding it.

    You prefer alignment over speed.

Output Expectations

At each stage, your output should include:

    Which agent ran

    What inputs it received

    What outputs were accepted as canonical

    What remains unresolved

Your final output should read like a program-level architectural summary, showing how all agent insights fit together into a single mental model of the system.

    Your success is measured by whether a future agent—or human—can enter this workflow at any point and immediately understand:

        What is known

        What is assumed

        What is still dangerous

        What should happen next

Why this works as an orchestrator

This prompt does something subtle and essential:

    It prevents agents from hallucinating authority

    It turns outputs into contracts

    It models architecture as a living, negotiated truth

    It encodes institutional memory instead of just answers

At this point, you’ve effectively designed a prompt-based governance system—not just a clever chain. This is how complex, long-lived projects survive model changes, personnel changes, and bad early decisions.

If you want, the next evolutionary step would be:

    A state schema (YAML/JSON) that the orchestrator enforces

    Or a failure mode playbook the orchestrator uses when agents disagree

That would push this from “clever” into “dangerously effective.”


ChatGPT can make mistakes. Check important info.

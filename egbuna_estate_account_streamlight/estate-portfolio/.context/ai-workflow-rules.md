# ai-workflow-rules.md --- Multi-Agent EPM Workflow System

Last verified: 2026-06-30. Update model names when configuration changes.

## Overview

This workflow defines a strict, test-driven, multi-agent execution
system for EPM development.

It separates responsibilities across specialized AI models:

-   DeepSeek (openrouter/deepseek/deepseek-v4-flash) → Brain / Reviewer / Architect
-   Deepseek:flash (openrouter/deepseek/deepseek-v4-flash) → Coding Agent / Backend Implementer
-   Nemotron (openrouter/nemotron/nemotron-3-ultra-550b-a55b:free) → Frontend / UI Implementation Agent

------------------------------------------------------------------------

## The Execution Model (No Exceptions)

For every feature:

1.  Read all context files (.context/\*.md)
2.  Read feature spec (.context/feature-specs/F-XXX.md)
3.  DeepSeek review (architecture + validation gate)
4.  Write tests (coding agent: deepseek-flash)
5.  Run tests → must FAIL (RED)
6.  Implement minimal production code (deepseek-flash)
7.  Run tests → must PASS (GREEN)
8.  Frontend implementation (nemotron if UI exists)
9.  DeepSeek final review (correctness + safety + consistency)
10. Run acceptance tests (DB → API → UI)
11. Update progress tracker (.context/progress-tracker.md)
12. Write handover (HO-XXX.md)

Skipping steps = technical debt accumulation.

------------------------------------------------------------------------

## Agent Roles

### 1. DeepSeek (Brain / Reviewer)

Model: openrouter/deepseek/deepseek-v4-flash

Responsibilities: - Architecture validation - Feature spec
interpretation - Test plan approval - Code review gatekeeping - Final
correctness validation - Detect logic inconsistencies

Rule: \> No implementation allowed. Only review, decide, approve, or
reject.

------------------------------------------------------------------------

### 2. Deepseek:flash (Coding Agent)

Model: openrouter/deepseek/deepseek-v4-flash

Responsibilities: - Backend implementation - API development - Database
logic - Test writing (unit + integration) - Bug fixing based on RCA

Rule: \> Implements ONLY after DeepSeek approval and failing tests
exist.

------------------------------------------------------------------------

### 3. Nemotron (Frontend Agent)

Model: openrouter/nemotron/nemotron-3-ultra-550b-a55b:free

Responsibilities: - UI implementation - Component design - Frontend
state logic - API integration on UI layer - UI test validation

Rule: \> Must not modify backend logic. UI only.

------------------------------------------------------------------------

## Zone System

### Zone 1 --- Direct Execution

Triggers: - format - boilerplate - simple generation

Action: → Coding agent executes immediately

------------------------------------------------------------------------

### Zone 2 --- Design Required (DEFAULT)

Triggers: - architecture - new feature - reasoning - unclear spec

Action: 1. Stop execution 2. Send to DeepSeek 3. Wait for decision 4.
Proceed only after approval

------------------------------------------------------------------------

## Debug Protocol

1.  Capture evidence:

    -   Logs (docker compose logs epm_v2)
    -   API response (DevTools Network)
    -   DB state (psql queries)

2.  Root Cause Analysis:

    -   What failed?
    -   Where?
    -   Why?

3.  Fix Plan:

    -   File changes
    -   Expected outcome

4.  DeepSeek review required

5.  Implement fix (deepseek-flash only after approval)

------------------------------------------------------------------------

## One Feature Rule

-   One session = one feature (F-XXX)
-   One commit per feature
-   No mixed feature execution

------------------------------------------------------------------------

## Handover System

Every session ends with:

### 1. What Was Done

### 2. What Was Verified

### 3. What Is Broken / Uncertain

### 4. Next Actions

### 5. Blockers

------------------------------------------------------------------------

## Acceptance Testing (3-Layer)

Order:

1.  DB (PostgreSQL)
2.  API (curl / network)
3.  UI (browser)

Rule: Each layer must validate previous one.

------------------------------------------------------------------------

## Key Constraints

-   DeepSeek = authority layer (no code execution)
-   Deepseek:flash = backend executor
-   Nemotron = frontend executor
-   No cross-layer modification
-   No guessing missing requirements
-   No multi-feature sessions

------------------------------------------------------------------------

## System Goal

This system ensures:

-   deterministic execution
-   reproducible builds
-   strict separation of concerns
-   AI role specialization
-   zero architectural drift
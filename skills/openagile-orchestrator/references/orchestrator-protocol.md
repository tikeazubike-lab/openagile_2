# Orchestrator Protocol

## Purpose

Use this reference when coordinating investigation, planning, execution, and handoff for OpenAgile work.

## Primary References

Read these first:

- `MASTER_CONTEXT.md`
- `ORCHESTRATOR_MISSION.md`
- `AGENT_STATE.yaml`
- `INFRASTRUCTURE_CONTRACT.md`
- relevant agent or skill instructions

## Required Sequence

Follow this order:

1. Investigator completes the infrastructure contract
2. Orchestrator produces the implementation or recovery plan
3. Builder executes approved Zone 1 work
4. Orchestrator validates and hands off

Do not skip ahead.

## Clarifying Questions Gate

Before finalizing a plan, resolve the items that change architecture or workflow:

- whether Woodpecker CI is required
- the target subdomain
- whether the request is a new build, a repair, or a recovery/realignment

Record the answers in `AGENT_STATE.yaml`.

## Deployment Law Enforcement

Reject plans that include any of the following:

- local Docker deployment commands
- direct SSH deployment instructions
- `scp` or manual server-side file transfer

Require GitHub Actions based deployment through repository changes and pushes.

## Zone Classification

Use Zone 1 when work is mechanical, precedent-backed, and low-risk.

Use Zone 2 when work introduces:

- new services
- new databases
- new networks
- new subdomains
- cross-service risk
- architectural ambiguity

When in doubt, classify as Zone 2 and wait for human confirmation.

## Plan Structure

Produce `RECOVERY_PLAN.md` or an equivalent plan with:

- context and gating status
- zone classification summary
- phased tasks
- validation steps
- acceptance criteria

Each task should identify its zone explicitly.

## Shared State

Keep `AGENT_STATE.yaml` current with:

- current phase
- deployment-law verification status
- Woodpecker requirement
- per-agent status
- artifact completion

## Conflict Handling

When sources disagree:

1. pause the workflow
2. summarize both positions
3. explain trade-offs
4. wait for human confirmation

## Handoffs

Prepare concise handoffs:

- Investigator to Orchestrator: key findings, deviations, open questions
- Orchestrator to Builder: approved tasks, constraints, pending Zone 2 confirmations

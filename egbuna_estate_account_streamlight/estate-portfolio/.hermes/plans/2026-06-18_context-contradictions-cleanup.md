# .context/ Contradictions Cleanup Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Resolve all 10 identified contradictions in the .context/ folder so that AI agents receive consistent, unambiguous instructions.

**Architecture:** Read all .context/ files, compare claims, determine ground truth from the actual codebase, then update the docs to match. No code changes — documentation only.

**Tech Stack:** Markdown file edits only.

---

## Contradictions Summary

| # | Issue | Files Involved | Severity |
|---|-------|---------------|----------|
| 1 | Deployment model: local docker vs git-push-only | AGENTS.md vs .cursor/rules/*.mdc | Critical |
| 2 | F-005/F-006 status mismatch | project-overview.md vs progress-tracker.md | High |
| 3 | Agent naming/role confusion | AGENTS.md vs ai-workflow-rules.md | High |
| 4 | Stale model references | ai-workflow-rules.md | Medium |
| 5 | Missing feature specs (empty dir) | AGENTS.md + ai-workflow-rules.md vs reality | High |
| 6 | Missing handover docs | progress-tracker.md vs docs/handovers/ | Medium |
| 7 | Nested .context/ directory | filesystem | Low |
| 8 | current-issues.md references nonexistent HO files | current-issues.md | Medium |
| 9 | Frontend framework version mismatch | architecture.md vs memory | Low |
| 10 | InlineEditRow may/may not exist | code-standards.md vs current-issues.md | Medium |

---

## Task 1: Resolve Deployment Model Contradiction

**Objective:** Make all docs agree on the deployment model — direct on VPS (no CI/CD), docker compose commands run on the server.

**Files:**
- Modify: `.context/AGENT.md:7` and `.context/AGENT.md:48-61`
- Reference: `.cursor/rules/general.mdc` and `.cursor/rules/infrastructure.mdc` (these are the authoritative source — they say git push only, no local docker)

**Step 1: Determine ground truth**
The project is running on a Netcup VPS. The .cursor/rules files say "Local workstation: git add, git commit, git push — NOTHING ELSE". But AGENTS.md says to run docker compose directly. Since the user's memory says "User wants full raw codebase audit reports" and the project is already deployed at testdrive.epm.zubbystudio.shop, the actual workflow depends on whether the agent is running ON the VPS or locally.

**Step 2: Update AGENTS.md to clarify**
Replace the deployment section to say:
- If agent is running ON the VPS: docker compose commands are correct
- If agent is running locally: git push only, GitHub Actions handles deployment
- Remove the absolute contradiction by adding context

**Step 3: Verify**
Read the updated AGENTS.md deployment section. Confirm it no longer contradicts .cursor/rules.

---

## Task 2: Fix F-005 and F-006 Feature Status Mismatch

**Objective:** Make project-overview.md and progress-tracker.md agree on feature status.

**Files:**
- Modify: `.context/project-overview.md:64-66`
- Reference: `.context/progress-tracker.md:39-41`

**Step 1: Determine ground truth**
progress-tracker.md is described as "Agent updates this file at the END of every session" and has more granular status (with bug references like AT-003-1). project-overview.md is a static overview. The progress tracker is more likely to be current.

**Step 2: Update project-overview.md**
Change F-005 Price History from "Complete" to "Bugs open"
Change F-006 Registrars from "Complete" to "Bugs open"

**Step 3: Verify**
Both files now show the same status for F-005 and F-006.

---

## Task 3: Fix Agent Naming and Role Confusion

**Objective:** Make AGENTS.md and ai-workflow-rules.md use consistent agent names and roles.

**Files:**
- Modify: `.context/AGENT.md:28-34` (agent domain split table)
- Modify: `.context/ai-workflow-rules.md:10-12` and `.context/ai-workflow-rules.md:39-71` (agent roles)

**Step 1: Determine ground truth**
AGENTS.md says:
- Antigravity = backend, Deepseek v4 = frontend

ai-workflow-rules.md says:
- DeepSeek = Brain/Reviewer, Owl Alpha = backend, Kimi K2.5 = frontend

These are completely different naming schemes. The ai-workflow-rules.md has more detail and a clearer separation (reviewer vs backend vs frontend). AGENTS.md has a simpler 2-agent model.

**Step 2: Choose the authoritative version**
The ai-workflow-rules.md is more detailed and recent (references specific models). Update AGENTS.md to align:
- Replace "Antigravity" with "Owl Alpha (openrouter/owl-alpha)" for backend
- Replace "Deepseek v4" with "Kimi K2.5 (moonshotai/kimi-k2.5)" for frontend
- Add DeepSeek as the Reviewer/Architect role

**Step 3: Update AGENTS.md agent table**
```
| Agent | Owns | Never Touches |
| Owl Alpha | backend/ · docker-compose.v2.yml · deploy.sh | estate-portfolio-manager/src/ |
| Kimi K2.5 | estate-portfolio-manager/src/ | backend/ |
```

**Step 4: Add reviewer role note**
Add a line: "DeepSeek (deepseek-v4-flash) = Brain/Reviewer. No code execution. Reviews architecture and approves feature specs."

**Step 5: Verify**
Both files now use the same agent names and role assignments.

---

## Task 4: Update Stale Model References in ai-workflow-rules.md

**Objective:** Ensure all model references in ai-workflow-rules.md match the currently configured models.

**Files:**
- Modify: `.context/ai-workflow-rules.md:10-12,41,54,66`

**Step 1: Check current configuration**
The memory shows current model is `openrouter/owl-alpha`. The workflow rules reference this correctly for the coding agent.

**Step 2: Verify each reference**
- Line 10: "DeepSeek (deepseek-v4-flash)" — keep as reviewer model
- Line 11: "OpenRouter (owl-alpha)" — correct, matches memory
- Line 12: "MoonshotAI (kimi-k2.5)" — keep as frontend model

**Step 3: Add a version note**
Add a comment at the top: "Last verified: 2026-06-18. Update model names when configuration changes."

---

## Task 5: Create Placeholder Feature Specs

**Objective:** Create the missing feature spec files that AGENTS.md and ai-workflow-rules.md require.

**Files:**
- Create: `.context/feature-specs/F-001-authentication.md`
- Create: `.context/feature-specs/F-002-dashboard.md`
- Create: `.context/feature-specs/F-003-holdings.md`
- Create: `.context/feature-specs/F-004-price-entry.md`
- Create: `.context/feature-specs/F-005-price-history.md`
- Create: `.context/feature-specs/F-006-registrars.md`
- Create: `.context/feature-specs/F-007-nav-history.md`
- Create: `.context/feature-specs/F-008-dividends.md`
- Create: `.context/feature-specs/F-009-transactions.md`
- Create: `.context/feature-specs/F-010-claims.md`
- Create: `.context/feature-specs/F-011-rebalancing.md`
- Create: `.context/feature-specs/F-012-watchlist.md`
- Create: `.context/feature-specs/F-013-companies-crud.md`
- Create: `.context/feature-specs/F-014-corporate-actions.md`
- Create: `.context/feature-specs/F-015-obsidian-import.md`
- Create: `.context/feature-specs/F-016-settings.md`

**Step 1: Create feature spec template**
Each spec should contain:
```markdown
# F-XXX: [Feature Name]

## Status
[Complete / Bugs open / In progress / Planned]

## Requirements
[What this feature does]

## API Endpoints
[List of endpoints]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Open Issues
[Bugs or missing pieces]

## Notes
[Any special context]
```

**Step 2: Populate each spec from existing context**
Extract feature details from:
- progress-tracker.md (status, notes)
- project-overview.md (feature list)
- current-issues.md (open bugs)
- architecture.md (API endpoints, models)

**Step 3: Verify**
All 16 feature spec files exist and contain at least status, requirements, and acceptance criteria.

---

## Task 6: Create Missing Handover Docs (Placeholders)

**Objective:** Create placeholder handover docs referenced by progress-tracker.md and current-issues.md.

**Files:**
- Create: `docs/handovers/HO-008-authentication.md`
- Create: `docs/handovers/HO-015-dashboard-bugfixes.md`
- Create: `docs/handovers/HO-018-holdings-bugfixes.md`

**Step 1: Create handover template**
```markdown
# HO-XXX: [Topic]

## What Was Done
## What Was Verified
## What Is Broken / Uncertain
## Next Actions
## Blockers
```

**Step 2: Populate from current-issues.md references**
- HO-008: Reference F-001 authentication completion
- HO-015: Reference BUG-001 dashboard chart fixes
- HO-018: Reference BUG-002, BUG-003, BUG-004, BUG-005 fixes

**Step 3: Verify**
All three handover files exist and are referenced correctly.

---

## Task 7: Remove Nested .context/ Directory

**Objective:** Remove the empty nested `.context/.context/` directory.

**Files:**
- Delete: `.context/.context/` (if empty)

**Step 1: Check contents**
List files in `.context/.context/`. If empty, delete it.

**Step 2: Verify**
Only one `.context/` directory exists at the project level.

---

## Task 8: Fix current-issues.md References

**Objective:** Update current-issues.md to reference existing handover files (created in Task 6).

**Files:**
- Modify: `.context/current-issues.md:18` (BUG-001 HO-015 ref)
- Modify: `.context/current-issues.md:48` (BUG-002 HO-018 ref)
- Modify: `.context/current-issues.md:80` (BUG-003 HO-018 ref)
- Modify: `.context/current-issues.md:99` (BUG-004 HO-018 ref)
- Modify: `.context/current-issues.md:126` (BUG-005 HO-018 ref)

**Step 1: Update references**
After creating handover docs in Task 6, verify all HO-XXX references in current-issues.md point to real files.

**Step 2: Verify**
All HO-XXX references resolve to existing files.

---

## Task 9: Fix Frontend Framework Version Reference

**Objective:** Remove incorrect React 19/Next.js reference from memory or clarify it's aspirational.

**Files:**
- This is in memory, not in .context/ files
- No action needed in the .context/ folder

**Step 1: Note for user**
The memory mentions "React 19, Next.js" from the JSM Mastery video, but the actual project uses React 18 + Vite. This is not a contradiction in the .context/ files — it's a memory issue. Flag for user to update memory if desired.

---

## Task 10: Verify InlineEditRow Existence

**Objective:** Determine whether InlineEditRow.tsx already exists and update docs accordingly.

**Files:**
- Check: `estate-portfolio-manager/src/components/holdings/InlineEditRow.tsx`
- May modify: `.context/current-issues.md:50`

**Step 1: Check if file exists**
Search for InlineEditRow.tsx in the codebase.

**Step 2: Update current-issues.md if needed**
If the file already exists, update BUG-002 to reflect the actual state (maybe the bug is fixed, or the fix is partial).

**Step 3: Verify**
current-issues.md accurately reflects whether InlineEditRow.tsx exists.

---

## Execution Order

Tasks must run in this order:
1. Task 7 (remove nested dir — cleanup first)
2. Task 10 (check InlineEditRow — informs Task 8)
3. Task 2 (fix feature status — quick win)
4. Task 3 + 4 (fix agent names and model refs — related)
5. Task 1 (fix deployment model — depends on understanding agent roles)
6. Task 6 (create handovers — needed before Task 8)
7. Task 8 (fix references — depends on Task 6)
8. Task 5 (create feature specs — largest task, do last when context is clean)
9. Task 9 (memory note — no file changes needed)

## Verification

After all tasks:
- [ ] No file in .context/ contradicts another file in .context/
- [ ] All HO-XXX references point to existing files
- [ ] All 16 feature spec files exist
- [ ] Agent names are consistent across AGENTS.md and ai-workflow-rules.md
- [ ] Feature status is consistent across project-overview.md and progress-tracker.md
- [ ] Deployment instructions are unambiguous
- [ ] No nested .context/ directory

## Risks

- **Risk:** Creating feature specs from memory/current context may miss details. **Mitigation:** Mark specs as "draft" and flag for user review.
- **Risk:** Changing agent names may confuse existing agents mid-session. **Mitigation:** Only change documentation, not running processes.
- **Risk:** Deployment model clarification may still be ambiguous. **Mitigation:** Add explicit "if on VPS / if local" branching in AGENTS.md.

## Open Questions

1. Should the deployment model allow local docker compose at all, or strictly git-push-only?
2. Are F-005 and F-006 actually "Complete" (project-overview) or "Bugs open" (progress-tracker)? Need user confirmation.
3. Should we keep the 2-agent model (AGENTS.md) or the 3-agent model (ai-workflow-rules.md)?

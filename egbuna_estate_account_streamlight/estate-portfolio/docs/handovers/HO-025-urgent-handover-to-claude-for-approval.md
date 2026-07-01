---
id: HO-025
title: Urgent Handover — Agent Configuration DRY Refactoring for Claude Review
status: SUBMITTED_FOR_REVIEW
author: Hermes Agent (Controller)
reviewer: Claude (Architect)
created: 2026-07-01
sprint: Phase 3C (New Core Features)
blocking: F-016 User Management (depends on stable agent config)
---

# HO-025 — Urgent Handover: Agent Configuration DRY Refactoring

## Summary

**Problem:** Agent/model strings are duplicated across 14+ documentation files (~50 occurrences). Every time we change a model (e.g., Owl Alpha → Deepseek:flash), we must manually update AGENT.md, ai-workflow-rules.md, 8 feature specs, MASTER_CONTEXT_v4.md, CONSTRAINTS.md, current-issues.md. This is error-prone and violates DRY.

**Proposed Solution:** Establish `.context/agents.yaml` as the single source of truth with a Python config loader (`backend/app/config/agents.py`) for runtime consumption. Markdown files reference agent keys (`deepseek-flash`, `nemotron`, `deepseek-v4`) instead of hardcoding model URLs.

**Request:** Claude to review the plan (saved at `.hermes/plans/2026-07-01_183000-agent-config-dry-refactor.md`) and approve/amend before implementation.

---

## Current State

### Files with Duplicated Strings

| File | Agent References | Model URL Occurrences |
|------|------------------|----------------------|
| `.context/AGENT.md` | 3 agents in table | 6 |
| `.context/ai-workflow-rules.md` | 12+ inline | 12+ |
| `.context/feature-specs/F-001` through `F-022` (8 files) | 3 each in frontmatter | 24 |
| `.context/current-issues.md` | 1 fix attribution | 0 |
| `specs/MASTER_CONTEXT_v4.md` | 11+ references | 11+ |
| `specs/CONSTRAINTS.md` | 1 editor reference | 0 |
| `.context/agents.yaml` | **Source of truth** | 3 (definitive) |

**Total: ~50+ duplicated strings**

### Authoritative Config (`.context/agents.yaml`)

```yaml
agents:
  deepseek-flash:
    role: backend-executor
    model: openrouter/deepseek/deepseek-v4-flash
    provider: openrouter
    owns: [backend/, docker-compose.v3.yml, deploy.sh]
    never_touches: [estate-portfolio-manager/src/]
  nemotron:
    role: frontend-executor
    model: openrouter/nemotron/nemotron-3-ultra-550b-a55b:free
    provider: openrouter
    owns: [estate-portfolio-manager/src/]
    never_touches: [backend/]
  deepseek-v4:
    role: reviewer-architect
    model: openrouter/deepseek/deepseek-v4-flash
    provider: openrouter
    owns: []
routing:
  backend_task: {primary: deepseek-flash, reviewer: deepseek-v4}
  frontend_task: {primary: nemotron, reviewer: deepseek-v4}
  complex_analytical: {primary: deepseek-v4}
```

---

## Proposed Plan (5 Tasks)

### Task 1: Config Loader Module (Foundation)
- **Create:** `backend/app/config/agents.py` — loads YAML, exposes typed API
- **Functions:** `get_agent_model(key)`, `get_routing()`, `get_agent_role(key)`
- **Tests:** `backend/tests/unit/config/test_agents_config.py` (TDD)
- **No markdown changes** — purely code infrastructure

### Task 2: Environment Variable Bridge (Optional)
- **Modify:** `.env.example` — add `AGENT_MODEL_BACKEND`, `AGENT_MODEL_FRONTEND`, `AGENT_MODEL_ARCHITECT`
- **Modify:** `agents.py` — respect env overrides with YAML fallback
- **Rationale:** 12-factor compliance for deployed services

### Task 3: Markdown Refactoring (Bulk Work)
- **14 files** updated to reference agent keys instead of model URLs
- **Pattern:** Add header comment `<!-- Agent models defined in .context/agents.yaml -->`
- **Feature specs:** Frontmatter uses keys (`deepseek-flash`, `nemotron`, `deepseek-v4`)
- **AGENT.md:** Simplified table showing keys + reference comment
- **ai-workflow-rules.md:** Replace model URLs in agent role sections

### Task 4: Doc Generation Script (Future-Proofing, Optional)
- **Create:** `scripts/generate_agent_docs.py` + Jinja2 templates
- **Add:** `make docs` target to regenerate from `agents.yaml`
- **Deferred** unless drift occurs

### Task 5: Runtime Validation
- **Verify:** FastAPI app can import and use config module
- **Verify:** Any scripts hardcoding models migrate to loader

---

## Key Design Decisions for Review

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Config location** | `backend/app/config/` vs `backend/scripts/` | `backend/app/config/` (follows existing pattern) |
| **Frontmatter format** | Keys (`deepseek-flash`) vs Full names (`Deepseek:flash`) | Keys (stable, machine-readable) |
| **Env overrides** | Required vs Optional | Optional (YAML defaults, env = override) |
| **Doc generation** | Jinja2 templates vs Manual updates | Start manual, add templates if drift detected |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Config path breaks in Docker | Medium | High | Use `__file__` relative path, test in container |
| Markdown drifts from YAML | Medium | Medium | Add CI check: `grep -r "openrouter/" .context/ --include="*.md" | grep -v agents.yaml` |
| Circular imports | Low | High | Config module is leaf (no app imports) |
| Env vars missing in prod | Low | Medium | Defaults in YAML, env is override only |

---

## Verification Criteria

Claude to confirm:
- [ ] Plan structure follows EPM conventions (bite-sized tasks, exact paths, TDD)
- [ ] Config loader approach is sound for FastAPI + scripts runtime
- [ ] Frontmatter key convention is correct for feature specs
- [ ] Env bridge pattern aligns with 12-factor and existing `.env.example`
- [ ] No missing dependencies (PyYAML already in requirements.txt)
- [ ] Task ordering is logical (foundation → runtime → docs → validation)

---

## Files to Review

1. **Plan:** `.hermes/plans/2026-07-01_183000-agent-config-dry-refactor.md`
2. **Source of truth:** `.context/agents.yaml`
3. **Example consumer:** `.context/AGENT.md` (current state)
4. **Feature spec example:** `.context/feature-specs/F-001-authentication.md`

---

## Next Steps After Approval

1. Controller dispatches Task 1 implementer (Deepseek:flash) with full context
2. Spec compliance review → Code quality review → Commit
3. Tasks 2-5 follow same pattern
4. Final integration review after all tasks complete

---

## Blocker Note

**F-016 User Management** (next sprint priority) depends on stable agent configuration for delegation discipline. This refactor should complete before F-016 implementation begins.

---

**Submitted by:** Hermes Agent (Controller)
**For review by:** Claude (Architect)
**Urgency:** HIGH — blocking sprint planning
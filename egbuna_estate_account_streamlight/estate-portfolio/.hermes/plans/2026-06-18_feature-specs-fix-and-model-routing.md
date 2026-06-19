# Feature Specs Review + Model Automation Config Plan

> **For Hermes:** This plan is written in plan mode — no execution yet. Review the open questions below before proceeding.

**Goal:** (1) Fix frontmatter inconsistencies in F-001–F-006 feature specs, and (2) answer the question: "what file automates the use of the models in AGENTS.md?"

**Architecture:** Feature specs use YAML frontmatter that must stay consistent with `.context/progress-tracker.md`. The model automation question requires understanding Hermes's `delegate_task` model override mechanism.

**Tech Stack:** YAML frontmatter; Hermes config.yaml `delegation` section.

---

## User Directives (from this session)

1. `.context/` folder = single source of truth
2. F-005 and F-006 correct status = "Bugs Open"
3. ai-workflow-rules has correct models → AGENTS.md updated accordingly
4. Feature specs and handovers are ONLY created after full RED→GREEN→RED→GREEN + acceptance tests
5. Handover files are generated only after code passes (not pre-created)

---

## Part A: Feature Spec Frontmatter Fixes

### Issue Summary

| File | Field | Current | Should Be | Why |
|------|-------|---------|-----------|-----|
| F-005 | `title` | `Bugs Open` | `Price History` | Wrong value |
| F-005 | `status` | `COMPLETE` | `BUGS-OPEN` | progress-tracker.md says "Bugs open" |
| F-006 | `status` | `COMPLETE` | `BUGS-OPEN` | progress-tracker.md says "Bugs open" |
| F-001 | `status` | `Complete` | `COMPLETE` | Inconsistent case (F-002/F-003 use BUGS-OPEN, F-004 uses COMPLETE) |

### A1: Fix F-005 title

**File:** `.context/feature-specs/F-005-price-history.md:5`
```yaml
# Before
title: Bugs Open

# After
title: Price History
```

### A2: Fix F-005 status

**File:** `.context/feature-specs/F-005-price-history.md:6`
```yaml
# Before
status: COMPLETE

# After
status: BUGS-OPEN
```

### A3: Fix F-006 status

**File:** `.context/feature-specs/F-006-registrars.md:5`
```yaml
# Before
status: COMPLETE

# After
status: BUGS-OPEN
```

### A4: Fix F-001 status case

**File:** `.context/feature-specs/F-001-authentication.md:7`
```yaml
# Before
status: Complete

# After
status: COMPLETE
```

### Verification

```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/.context/feature-specs
for f in F-001 F-002 F-003 F-004 F-005 F-006; do
  echo "=== $f ==="
  grep -E "^(title|status):" "$f"*.md
done
```

Expected: All titles correct, all status values are either `COMPLETE` or `BUGS-OPEN`.

---

## Part B: Model Automation — What File Routes Work to Models?

### Investigation Results

**Current Hermes config** (`~/.hermes/config.yaml`):
- Default model: `openrouter/owl-alpha`
- No `delegation.model` or `delegation.provider` set
- No `custom_providers` file exists
- No `.env` file with API keys for KIMI or DEEPSEEK

**How `delegate_task` routes models today:**

Hermes's `delegate_task` tool accepts a `model` parameter (object with `provider` and `model`). This is defined in the tool schema:

```json
{
  "name": "model",
  "type": "object",
  "properties": {
    "provider": { "type": "string" },
    "model": { "type": "string" }
  }
}
```

This means **no config file is needed** to automate model usage. The orchestrator (the main agent) simply passes `model: { provider: "moonshotai", model: "kimi-k2.5" }` when calling `delegate_task` for frontend work.

**The question is:** should we create a convenience layer so the orchestrator doesn't have to hardcode model names every time?

### Option 1: No file needed (simplest)

The orchestrator reads AGENTS.md, sees the model assignments, and passes them inline:
```python
delegate_task(
  goal="Fix dashboard chart",
  model={"provider": "openrouter", "model": "owl-alpha"},
  ...
)
```

**Zero files to create.** Just use the `model` parameter.

### Option 2: `.context/agents.yaml` (convenience mapping)

Create a YAML file that the orchestrator can read as reference:
```yaml
agents:
  owl-alpha:
    model: openrouter/owl-alpha
  kimi-k25:
    model: moonshotai/kimi-k2.5
  deepseek:
    model: deepseek/deepseek-v4-flash
```

The orchestrator reads this to construct the `model` parameter without memorizing strings.

### Option 3: Hermes `delegation` config section

Set `delegation.model` and `delegation.provider` in `~/.hermes/config.yaml` so ALL delegate_task calls default to a specific model:
```yaml
delegation:
  model: moonshotai/kimi-k2.5
  provider: moonshotai
```

**Problem:** This forces ALL delegation to one model. You'd need to override per-call for different agents.

---

## Open Questions (need your answers before finalizing)

### Q1: Model API Keys

`OPENROUTER_API_KEY` is the only key currently in environment. Do you have:
- `KIMI_API_KEY` (for moonshotai/kimi-k2.5)?
- `DEEPSEEK_API_KEY` (for deepseek/deepseek-v4-flash)?

If not, `delegate_task` with those models will fail with 401. The agent names in AGENTS.md are configured but the credentials aren't present.

**Options:**
- A) Add keys to `~/.hermes/.env` now
- B) Create the routing file but note "keys needed"
- C) Use OpenRouter as the provider for all three (since it proxies to any model) — set model to `moonshotai/kimi-k2.5` and `deepseek/deepseek-v4-flash` under `provider: openrouter`

### Q2: Model Automation Approach

Which option do you prefer?
- **Option 1:** No file. Orchestrator passes model inline in `delegate_task` calls.
- **Option 2:** `.context/agents.yaml` as a reference doc (not loaded by Hermes, just for the orchestrator to read).
- **Option 3:** Hermes config `delegation` section (forces default model).

### Q3: F-001 and F-004 Acceptance Status

F-001 and F-004 specs say "All checklist items verified" / "No open bugs" in their sign-off. But per your directive, handovers only exist after full RED→GREEN + acceptance. Since no handover files exist for these:
- **Should we update the sign-off to say "Code exists, formal acceptance not yet run under RED-GREEN cycle"?**
- Or do you consider them truly complete and just haven't written the handover yet?

### Q4: Status Enum Convention

F-002 and F-003 use `BUGS-OPEN` (hyphenated, uppercase). F-004 uses `COMPLETE` (uppercase, no hyphen). Should the enum be:
- `COMPLETE` / `BUGS-OPEN` / `IN-PROGRESS` / `PLANNED`?
- Or match the progress-tracker.md format: `✅ Complete` / `⚠️ Bugs open`?

(Note: YAML values with emojis and special chars need quoting.)

---

## Execution Order (after your answers)

1. Part A: Fix frontmatter (4 one-line edits, ~2 min total)
2. Part B: Implement your chosen model automation approach (0–5 min depending on option)

## Verification

- [ ] All F-001–F-006 frontmatter `status` values are consistent
- [ ] F-005 title is "Price History"
- [ ] Model automation question answered per your preference
- [ ] If Option 2 chosen: `.context/agents.yaml` is valid YAML
- [ ] If Option 3 chosen: `~/.hermes/config.yaml` delegation section added

## Risks

- **Risk:** Setting `delegation.model` in config (Option 3) forces all subagents to that model unless explicitly overridden. **Mitigation:** Use Option 1 or 2 instead.
- **Risk:** If API keys for Kimi/DeepSeek are missing, those agents will fail at runtime. **Mitigation:** Use OpenRouter as proxy (Q1 Option C) or add keys.

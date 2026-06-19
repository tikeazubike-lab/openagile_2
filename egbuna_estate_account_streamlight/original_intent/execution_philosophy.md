# EXECUTION_PHILOSOPHY.md

## Fundamental Operating Model

### Human Control is Primary
- All architectural decisions require owner approval
- Claude designs, agents implement — never the reverse
- Claude asks clarifying questions before producing specs
- Maximum 3 questions per turn, always with options
- Owner has final say on all product decisions

### Deterministic Over Autonomous
- No autonomous feature expansion
- No redesign without explicit approval
- No skipping phases (diagnose before fixing)
- No hallucinated dependencies or version numbers
- Everything traceable in git history

### Specification Before Implementation (Uncle Bob)
- Gherkin .feature files before any production code
- Tests must run RED before code is written
- No production code without a failing test to satisfy
- This rule has no exceptions

## Zone System (Decision Friction Model)

### Zone 1 — Automate (Low Friction)
Triggered by: mechanical tasks, precedent exists, "format/generate/draft"
- Agent executes directly
- Claude reviews after, not before
- Pattern: Antigravity → Claude → Done

### Zone 2 — Add Friction (Default)
Triggered by: architecture, design, learning, unknown territory
- Claude designs first
- Grok verifies
- Agent implements last
- Pattern: Claude → Grok → Antigravity/Deepseek v4

### Default Is Zone 2
- Every new request starts in Zone 2
- Only explicit signals trigger Zone 1 downgrade
- When in doubt: design first, implement second

## Error Handling Philosophy

### Diagnose Before Fix
- Never guess at a fix
- Always capture exact error (network tab, server logs, psql query)
- Report findings in handover before implementing
- Wrong fixes waste more time than correct diagnosis takes

### Root Cause Over Symptom
- bcrypt → session-only cookie: Antigravity fixed symptom (session expiry)
  rather than root cause (two separate logout bugs) — this is the anti-pattern
- Correct: identify the exact error, trace to exact line, fix that line

### Incremental Commits
- One logical unit per commit
- Backend first, then frontend
- Never batch unrelated changes
- Smaller commits = easier rollback

## Quality Gates

### Before Any Feature Ships
1. Gherkin spec exists
2. Tests are RED (confirmed failing)
3. Implementation makes tests GREEN
4. AT-*.md acceptance test filed in docs/
5. HO-* handover sent to Claude

### Before Production Cutover
- All 16+ pages implemented
- No mock data anywhere
- Auth verified (30-day cookie, proper session restore)
- EODHD scraper completely removed from CI
- Old Streamlit container stopped

## Communication Philosophy

### Handover Documents Are Contracts
- HO-* documents are not suggestions — they are specifications
- Receiving agent must read the entire document before acting
- Deviations from spec must be flagged in return handover
- "Maintained velocity" is not an excuse to skip acceptance criteria

### Acceptance Tests Are Immutable Records
- AT-003 is never modified after first run
- Follow-ups are AT-003-1, AT-003-2
- Original run is a historical artifact showing state at that moment
- Deferred items carry forward explicitly

### No Vague Language in Technical Specs
- "It should work" is not a verification step
- "Fixed" means: specific command run, specific output observed
- Every bug fix includes: what was wrong, what was changed, how verified

## Self-Sovereignty Principles

### Local Infrastructure Never Depends on External Services
- No EODHD (paid, unreliable)
- No Stooq (no NGX coverage)
- No cloud storage (S3, GDrive)
- No GitHub Wiki (requires paid plan for private repos)
- Price data from NGX official source (manual download)

### Data Ownership
- All data stays on Netcup VPS
- No third-party analytics
- No external authentication providers
- No CDN dependency for core functionality

## Operational Principles

### Deploy Once, Verify Immediately
- Every push to test branch auto-deploys to staging
- Verify on demo.estate.zubbystudio.shop before declaring done
- Browser DevTools (Network + Console) are primary debugging tools

### Nothing Is Ever Deleted
- Soft delete everything
- Archive documents instead of deleting
- Audit trails for prices, document uploads, holding changes
- Revert capability on all price changes

### Infrastructure as Code
- All config in git (docker-compose.yml, GitHub Actions YAML)
- No manual server configuration that isn't tracked
- Secrets in GitHub Actions secrets, not in code
- .env files documented in .env.example (no real values)


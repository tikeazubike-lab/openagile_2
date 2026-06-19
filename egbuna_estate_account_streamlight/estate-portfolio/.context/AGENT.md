# AGENTS.md — EPM Agent Entry Point

Project: Estate Portfolio Manager (EPM) v3 — Test Drive
Server: 185.216.177.250 (Netcup VPS) — working directly on server
Project root: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/
Staging URL: https://testdrive.epm.zubbystudio.shop
Deployment: Direct — restart container after backend changes, rebuild after frontend changes

---

## Before Every Session — Read These Files in Order

1. .context/project-overview.md
2. .context/architecture.md
3. .context/code-standards.md
4. .context/ai-workflow-rules.md
5. .context/ui-context.md          (frontend work only)
6. .context/progress-tracker.md
7. .context/current-issues.md      (if it exists)
8. .context/agents.yaml            (agent-to-model routing)

Then read your assigned feature spec:
  .context/feature-specs/F-XXX-feature-name.md

---

## Agent Domain Split — No Exceptions

| Agent | Model | Owns | Never Touches |
|-------|-------|------|---------------|
| Owl Alpha | openrouter/owl-alpha | backend/ · docker-compose.v3.yml · deploy.sh | estate-portfolio-manager/src/ |
| Nex N2 | openrouter/nex-agi/nex-n2-pro:free | estate-portfolio-manager/src/ | backend/ |
| DeepSeek | openrouter/deepseek/deepseek-v4-flash | Review/Architect role. No code execution. | — |

Sequence: Owl Alpha finishes backend first. Nex N2 reads it then fixes frontend. DeepSeek reviews architecture and approves feature specs. Never both sides in the same session simultaneously.

---

## The One Rule That Cannot Be Broken

No agent writes production code for a feature until:
  (a) the feature spec F-XXX.md exists, AND
  (b) tests for that feature are confirmed FAILING (RED)

Write the test. Run it. See it fail. Only then write code.

---

## Deployment on This Server (No CI/CD)

Backend change:
  cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
  docker compose -f docker-compose.v3.yml up -d --build epm_v3

Frontend change:
  cd estate-portfolio-manager
  npm run build
  cp -r dist/* ../backend/app/static/
  docker compose -f docker-compose.v3.yml restart epm_v3

View logs:
  docker compose -f docker-compose.v3.yml logs epm_v3 --tail=50

---

## After Completing Work

1. Run acceptance checklist from the feature spec
2. Update .context/progress-tracker.md
3. Write handover brief → docs/handovers/HO-XXX.md

---

## Hard Rules

NO production code before RED tests
NO implementation without a feature spec
NO guessing at bug fixes — diagnose first, write analysis, wait for approval
NO datetime.utcnow() — always datetime.now(timezone.utc)
NO get_db — always get_session
NO localStorage for JWT — httpOnly cookie only
NO hardcoded hex colours — always var(--token-name)
NO monetary floats from API — always strings ("12345.50" not 12345.50)
NO bcrypt upgrade above 4.0.1

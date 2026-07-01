# Phase 1 — Project Foundation

## What This Phase Produces
1. Repository folder structure (created on disk)
2. All 7 `.context/` files populated
3. Agent configuration (Hermes personality, Cursor rules)
4. Infrastructure baseline (Docker/server running, hello-world endpoint)
5. `.gitignore` with correct exclusions

---

## Questions to Ask (Group 1 — Tech Stack)

> "What is your tech stack? Pick or describe each layer:
>
> Backend language/framework:
>   a) Python/FastAPI  b) Python/Django  c) Node/Express
>   d) Go  e) Other (describe)
>
> Frontend (if applicable):
>   a) React + TypeScript  b) Vue 3  c) Plain HTML/JS
>   d) No frontend — API only  e) Other
>
> Database:
>   a) PostgreSQL  b) MySQL/MariaDB  c) SQLite  d) MongoDB  e) Other
>
> Hosting:
>   a) Self-hosted VPS (Linux)  b) Docker Compose  c) Cloud (which?)
>   d) Local only"

---

## Questions to Ask (Group 2 — Agents)

> "Which AI agents will work on this project?
> Select all that apply:
>
>   a) Antigravity (Gemini Pro — backend/infra)
>   b) Deepseek v4 (frontend)
>   c) Cursor (coding assistant in IDE)
>   d) Hermes (local terminal executor)
>   e) Claude Code (full codebase access)
>   f) Other (describe)
>
> For each selected agent, what files will they own?
> (e.g. Antigravity → backend/**, Deepseek → src/**)"

---

## Questions to Ask (Group 3 — Deployment)

> "How will code get deployed?
>
>   a) GitHub Actions CI/CD (automatic on push)
>   b) Manual script (you run deploy.sh on the server)
>   c) Direct editing on server (no git workflow yet)
>   d) Other
>
> And for the staging environment — do you have a URL already?
> (e.g. testdrive.myproject.example.com)"

---

## Documents to Produce

After all groups answered, produce in this order:

1. Create folder structure:
```bash
mkdir -p .context/feature-specs
mkdir -p docs/decisions docs/requirements
mkdir -p docs/testing/features docs/testing/acceptance
mkdir -p docs/handovers
```

2. Produce `.context/AGENTS.md` — entry point with hard rules
3. Produce `.context/project-overview.md` — from Phase 0 answers
4. Produce `.context/architecture.md` — stack + invariants placeholder
5. Produce `.context/code-standards.md` — language conventions
6. Copy `assets/ai-workflow-rules-universal.md` → `.context/ai-workflow-rules.md`
7. Produce `.context/ui-context.md` (if frontend project)
8. Produce `.context/progress-tracker.md` — all features = PLANNED
9. Create `.context/current-issues.md` — empty (gitignored)

10. Produce `.gitignore`:
```
.context/current-issues.md
uploads/
.env
.env.local
*.log
__pycache__/
node_modules/
dist/
.DS_Store
```

11. If Cursor agent selected: produce `.cursor/rules/` files
12. If Hermes agent selected: produce personality block to paste into config.yaml

---

## Phase 1 Checklist

Present this checklist and ask the user to confirm each item:

```
Repository:
[ ] .context/ folder exists with all 7 files
[ ] docs/ folder structure exists
[ ] .gitignore created with correct exclusions

Infrastructure:
[ ] Version control initialised (git init + remote, or direct-on-server noted)
[ ] Deployment method confirmed and documented in AGENTS.md
[ ] Staging URL accessible (or noted as pending)

Context Files:
[ ] AGENTS.md — hard rules present, file domains assigned
[ ] project-overview.md — problem, vision, users, out-of-scope
[ ] architecture.md — stack listed (invariants added in Phase 2)
[ ] code-standards.md — language conventions present
[ ] ai-workflow-rules.md — copied from universal template unchanged
[ ] progress-tracker.md — feature list with all statuses = PLANNED
[ ] current-issues.md — exists but empty (will be gitignored)
```

After all confirmed:
> "Phase 1 complete. The foundation is in place. Ready for Phase 2 —
> Architecture Decisions? This is where we lock the choices that are
> hard to reverse."

# Agent Handoff Log

Format: `## YYYY-MM-DD HH:MM UTC — <tool> — <one-line summary>` followed by
2-4 lines of what changed / why / what's next. Newest entries at the top.

---

## 2026-07-05 12:00 WAT — hermes — Created MASTER_CONTEXT_server.md + MASTER_CONTEXT_workstation.md overlay files

Three-tier Master Context architecture live:
- MAIN: `.context/MASTER_CONTEXT.md` — all standard rules
- SERVER OVERLAY: `.context/MASTER_CONTEXT_server.md` — allows direct VPS deploy
- WORKSTATION OVERLAY: `.context/MASTER_CONTEXT_workstation.md` — enforces CI/CD-only

Agent start rule: ask "Server (VPS direct) or Workstation (CI/CD)?" to pick the overlay.

## 2026-07-05 11:50 WAT — hermes — MASTER_CONTEXT v4 deployed to .context/; old Master_context_Claude_web_2.txt removed

v4 covers: full infra contract, CI/CD fast/full path, vault sync architecture, historical decision log, failed approaches, Master Prompt Framework, zone classification, tool strengths, EPM backend layout.

## 2026-07-05 10:30 WAT — hermes — F-013 + F-TD-001 implementation via OpenCode, deployed to testdrive

Companies Page and Checklist Teardown feature implemented by DeepSeek Flash (OpenCode), deployed to testdrive.epm.zubbystudio.shop. Alembic migration run. All endpoints verified 200.

## 2026-07-05 08:30 WAT — hermes — F-013 + F-TD-001 specs written, architect-reviewed, HO-029 created

Feature specs reviewed by DeepSeek Pro, patched with corrections. Handover to Claude Web committed.

## 2026-07-03 20:30 UTC — opencode — Added Claude Web back as co-Architect

## 2026-07-03 20:15 UTC — opencode — Provider migration: OpenRouter → OpenCode Go + OpenCode Zen

## 2026-07-03 19:50 UTC — opencode — Endpoint acceptance verification (companies + cost-basis + admin)

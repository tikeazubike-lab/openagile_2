# Agent Handoff Log

Format: `## YYYY-MM-DD HH:MM UTC — <tool> — <one-line summary>` followed by
2-4 lines of what changed / why / what's next. Newest entries at the top.

---

## 2026-07-05 11:50 WAT — hermes — MASTER_CONTEXT v4 deployed to .context/; old Master_context_Claude_web_2.txt removed

v4 covers: full infra contract, CI/CD fast/full path, vault sync architecture, historical decision log, failed approaches, Master Prompt Framework, zone classification, tool strengths, EPM backend layout.

Conflicts between this document and actual Hermes session workflow identified on promotion (HO-029).

## 2026-07-05 10:30 WAT — hermes — F-013 + F-TD-001 implementation via OpenCode, deployed to testdrive

Companies Page and Checklist Teardown feature implemented by DeepSeek Flash (OpenCode), deployed to testdrive.epm.zubbystudio.shop. Alembic migration run. All endpoints verified 200.

## 2026-07-05 08:30 WAT — hermes — F-013 + F-TD-001 specs written, architect-reviewed, HQ-029 created

Feature specs reviewed by DeepSeek Pro, patched with corrections. Handover to Claude Web committed.

## 2026-07-03 20:30 UTC — opencode — Added Claude Web back as co-Architect
Claude Web restored as co-Architect with DeepSeek Pro. Both are architects — differentiators: DeepSeek Pro delegates to subagents, Claude Web provides domain expertise. All 14 files updated.

## 2026-07-03 20:15 UTC — opencode — Provider migration: OpenRouter → OpenCode Go + OpenCode Zen
Updated all routing files. OpenCode agents run on OpenCode Go. Hermes runs on OpenCode Zen (deepseek:flash). Nemotron removed. All 12 config files synced.

## 2026-07-03 19:50 UTC — opencode — Endpoint acceptance verification (companies + cost-basis + admin)

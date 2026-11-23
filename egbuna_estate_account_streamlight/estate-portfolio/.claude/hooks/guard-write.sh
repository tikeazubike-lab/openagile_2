#!/usr/bin/env bash
# PreToolUse guard for Write|Edit|NotebookEdit. Input: hook JSON on stdin. exit 2 = block.
# Phase 1 (permissive): spec-reference check only warns on stderr. Tighten after one cycle.
set -uo pipefail
block() { echo "BLOCKED by guard-write: $1 (${path:-?})" >&2; exit 2; }
warn()  { echo "WARN guard-write: $1 ($path)" >&2; }
input=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null) || block "unparseable hook input (fail-closed)"
path=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' <<<"$input" 2>/dev/null) || block "unparseable hook input (fail-closed)"
[[ -z "$path" ]] && block "no file path in hook input (fail-closed)"
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
[[ "$path" = /* ]] || path="$root/$path"
base=$(basename "$path")
case "$path" in
  */.git|*/.git/*) block "writes inside .git" ;;
  */.claude/settings*.json|*/.claude/hooks/*) block "guardrail files are changed by Zubbyik via PR, not by the agent" ;;
esac
case "$base" in
  .env.example|.env.sample|.env.template) ;;
  .env|.env.*|*.env|.envrc) block "writes to .env files (secrets)" ;;
esac
case "$path" in
  "$root"/*|/tmp/*) ;;
  *) block "outside EPM project scope ($root)" ;;
esac
case "$path" in
  */alembic/versions/*)
    [[ -e "$path" ]] && block "modifying an existing Alembic migration (additive-only: add a new revision)" ;;
  */backend/app/*|*/estate-portfolio-manager/src/*)
    if [[ "$tool" == "Write" && ! -e "$path" ]]; then
      stem="${base%.*}"
      case "$stem" in __init__|index|main|types|utils) warn "generic filename; confirm a spec covers it" ;; esac
      if ! grep -rqsF -- "$stem" "$root/.context/feature-specs" 2>/dev/null; then
        warn "new app file not referenced by any spec in .context/feature-specs/ (spec-first rule)"
      fi
    fi ;;
esac
exit 0

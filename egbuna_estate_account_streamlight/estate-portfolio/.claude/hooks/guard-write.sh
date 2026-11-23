#!/usr/bin/env bash
# PreToolUse guard for Write|Edit. Input: hook JSON on stdin. exit 2 = block.
# Phase 1 (permissive): spec-reference check only warns on stderr. Tighten after one cycle.
set -euo pipefail
input=$(cat)
tool=$(jq -r '.tool_name // ""' <<<"$input")
path=$(jq -r '.tool_input.file_path // ""' <<<"$input")
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
block() { echo "BLOCKED by guard-write: $1 ($path)" >&2; exit 2; }
warn()  { echo "WARN guard-write: $1 ($path)" >&2; }
base=$(basename "$path")
case "$path" in
  */.git/*|.git/*) block "writes inside .git/" ;;
esac
case "$base" in
  .env|.env.*|*.env) block "writes to .env files (secrets)" ;;
esac
case "$path" in
  */alembic/versions/*)
    [[ -e "$path" ]] && block "modifying an existing Alembic migration (additive-only: add a new revision)" ;;
  */backend/app/*|backend/app/*|*/estate-portfolio-manager/src/*|estate-portfolio-manager/src/*)
    if [[ "$tool" == "Write" && ! -e "$path" ]]; then
      stem="${base%.*}"
      if ! grep -rqsF -- "$stem" "$root/.context/feature-specs" 2>/dev/null; then
        warn "new app file not referenced by any spec in .context/feature-specs/ (spec-first rule)"
      fi
    fi ;;
esac
exit 0

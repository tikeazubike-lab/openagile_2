#!/usr/bin/env bash
# PreToolUse guard for Bash. Input: hook JSON on stdin. exit 2 = block (stderr goes to the model).
# Source: docs/handover/ARCHITECT-TAKEOVER-001.md §3c (patterns tightened, see PR notes).
set -euo pipefail
cmd=$(jq -r '.tool_input.command // ""')
block() { echo "BLOCKED by guard-bash: $1" >&2; exit 2; }
grep -Eq 'git +push.*(--force|-f( |$)|[ :]\+[^ ]+)' <<<"$cmd"              && block "force push"
grep -Eq 'git +push[^|;&]*( |:)main( |$)' <<<"$cmd"                        && block "push to main (Gate 2: PR only)"
grep -Eq 'git +(reset +--hard|filter-branch|filter-repo|rebase +-i)' <<<"$cmd" && block "history rewrite/destructive reset"
grep -Eiq 'psql.*\b(insert|update|delete|alter|drop|create|truncate|grant|revoke)\b' <<<"$cmd" && block "write SQL via psql (use a committed Alembic migration)"
grep -Eq 'docker(-| +)compose\b.*\b(up|down|build|restart|stop|rm|kill)\b' <<<"$cmd" && block "container change needs Zubbyik's explicit go"
grep -Eq 'docker +(container +)?(restart|rm|stop|kill)\b' <<<"$cmd"         && block "container change needs Zubbyik's explicit go"
grep -Eq '(rm|git +rm)\b[^|;&]*alembic/versions' <<<"$cmd"                 && block "deleting Alembic migrations (additive-only)"
grep -Eq '\b(cat|less|more|head|tail|bat|strings)\b[^|;&]*\.env' <<<"$cmd" && block "would print secrets"
grep -Eq '(^|[;&|(] *)(printenv|env)( *$| *[;&|)])' <<<"$cmd"               && block "would print secrets"
exit 0

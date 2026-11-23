#!/usr/bin/env bash
# PreToolUse guard for Bash. Input: hook JSON on stdin. exit 2 = block (stderr goes to the model).
# Source: docs/handover/ARCHITECT-TAKEOVER-001.md §3c (patterns tightened after auditor pass).
set -uo pipefail
block() { echo "BLOCKED by guard-bash: $1" >&2; exit 2; }
raw=$(jq -r '.tool_input.command // empty' 2>/dev/null) || block "unparseable hook input (fail-closed)"
# Flatten heredocs/newlines and strip quotes so 'main', "main", multi-line SQL are matched.
cmd=$(tr '\n' ' ' <<<"$raw" | tr -d "\"'")
m() { grep -Eiq -- "$1" <<<"$cmd"; }
m 'git\b[^;&|]*\bpush.*(--force|--mirror|--delete| -f( |$)| [^ ]*:?\+[^ ]+| :[^ ]+)'                     && block "force push / mirror / remote branch delete"
m 'git\b[^;&|]*\bpush.*([ :]|refs/heads/)main( |;|&|\||$)'          && block "push to main (Gate 2: PR only)"
m 'git( +-C +[^ ]+)? +push( +[^ -][^ ]*)? *($|;|&|\|)' && m 'git +(checkout|switch) +main'  && block "push while switching to main"
m 'git +(reset +--hard|filter-branch|filter-repo|rebase +-i|clean +-[a-z]*f|update-ref +-d|branch +-D)' && block "history rewrite / destructive git"
m 'psql.*\b(insert|update|delete|alter|drop|create|truncate|grant|revoke)\b'               && block "write SQL via psql (use a committed Alembic migration)"
m 'psql.*( -f | -f$|<|--file)' || m '\| *(docker +exec[^|]*)?psql'                         && block "psql from file/stdin (cannot inspect; use a committed migration)"
m '(^|[;&|( ])(rm|git +rm|mv|git +mv)\b[^|;&]*alembic/versions'                    && block "deleting/moving Alembic migrations (additive-only)"
m '\balembic +(upgrade|downgrade|stamp)\b'                                                  && block "migration run needs Zubbyik's explicit go"
m 'docker(-| +)compose\b.* (up|down|build|restart|stop|rm|kill|run|start|create)( |$)'     && block "container change needs Zubbyik's explicit go"
m 'docker +(container +|image +|volume +|network +|system +)?(restart|rm|stop|kill|start|run|build|prune|rmi|create)( |$)' && block "container change needs Zubbyik's explicit go"
m '\b(cat|less|more|head|tail|bat|strings|grep|sed|awk|source|xxd|od)\b[^|;&]*\.env(\.v[0-9]+)?( |$|;|&|\|)' && block "would print secrets"
m '(^|[;&|( ])(printenv|env)( |$|;|&|\|)' && ! m '(^|[;&|( ])env +[A-Z_]+=.* [a-z]'          && block "would print secrets"
m 'os\.environ|process\.env' && m '\b(print|echo|console\.log)'                             && block "would print secrets"
exit 0

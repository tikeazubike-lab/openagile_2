#!/usr/bin/env bash
# Spawn an OpenCode agent for one role, non-interactively, inside a git worktree.
# Usage: dispatch.sh <builder|frontend|reviewer> <epm-dir-in-worktree> <brief-file> [log-dir]
#
# Orchestrator = Claude Code. This script is the only way builder/reviewer agents are started.
# Guardrails: a role-specific opencode.json is placed in the worktree's EPM dir for the run
# (OpenCode enforces project-file permissions; OPENCODE_CONFIG was tested and is NOT enforced),
# then removed. The builder never pushes; the orchestrator pushes after the auditor pass.
set -euo pipefail
role=${1:?role}; wt=${2:?epm dir in worktree}; brief=${3:?brief file}
logdir=${4:-${TMPDIR:-/tmp}/epm-agent-runs}
here=$(cd "$(dirname "$0")" && pwd)
case "$role" in
  builder)  model=opencode-go/mimo-v2.6-flash; profile=builder ;;
  frontend) model=opencode-go/mimo-v2.6-pro;       profile=builder ;;
  reviewer) model=opencode-go/deepseek-v4-pro;     profile=reviewer ;;
  *) echo "unknown role: $role" >&2; exit 64 ;;
esac
[[ -d "$wt" && -f "$brief" ]] || { echo "missing worktree dir or brief" >&2; exit 64; }
main_tree=$(git -C "$here" rev-parse --show-toplevel)
[[ "$(git -C "$wt" rev-parse --show-toplevel)" != "$main_tree" ]] || { echo "refusing: run in a separate worktree, not the main tree (cron runs there)" >&2; exit 65; }
branch=$(git -C "$wt" branch --show-current)
[[ "$branch" != main && "$branch" != test ]] || { echo "refusing: builder may not work on $branch" >&2; exit 65; }

# Handover rule (Zubbyik, 2026-11-24): every artefact passed to an agent lives in docs/handovers/,
# HO-prefixed, committed before dispatch. The agent's report is saved next to it (see the end).
wt_root=$(git -C "$wt" rev-parse --show-toplevel)
ho_dir=$(realpath "$wt/docs/handovers"); brief_abs=$(realpath "$brief")
[[ "$brief_abs" == "$ho_dir"/HO-* ]] || { echo "refusing: brief must be $ho_dir/HO-<nnn>-....md (handover rule)" >&2; exit 66; }
rel=${brief_abs#"$wt_root"/}
{ git -C "$wt_root" ls-files --error-unmatch -- "$rel" && git -C "$wt_root" diff --quiet HEAD -- "$rel"; } >/dev/null 2>&1 \
  || { echo "refusing: commit the brief before dispatch ($rel)" >&2; exit 66; }

mkdir -p "$logdir"; ts=$(date +%Y%m%d-%H%M%S); log="$logdir/$ts-$role.jsonl"
cp "$here/opencode.$profile.json" "$wt/opencode.json"
trap 'rm -f "$wt/opencode.json"' EXIT
start=$(git -C "$wt" rev-parse HEAD)

rules=$'You are the EPM '"$role"$' agent, started by the orchestrator (Claude Code). Rules:\n- Follow the brief exactly; files outside its scope are off-limits.\n- Never push, never touch containers or databases, never print secrets. Denied commands are denied on purpose: do not look for workarounds.\n- Commit each step with a clear message (builder roles). The reviewer role writes nothing.\n- Finish with a report: what changed, raw test output, commit SHAs (40 chars), what was NOT done.\n\nBRIEF:\n'
( cd "$wt" && timeout "${DISPATCH_TIMEOUT:-3600}" opencode run --auto --archived --format json \
    --title "epm-$role-$ts" -m "$model" "$rules$(cat "$brief")" ) > "$log" 2>&1 || echo "opencode exit=$?" >&2

echo "== role=$role model=$model branch=$branch log=$log"
echo "== denied tool calls:"; jq -r 'select(.part.type=="tool" and (.part.state.error // "" | test("Permission denied"))) | "  " + (.part.state.input.command // .part.state.input.filePath // "?")' "$log" 2>/dev/null || true
echo "== errors:"; grep -o '"type":"error".\{0,200\}' "$log" | head -3 || true
echo "== new commits:"; git -C "$wt" log --format='  %H %s' "$start"..HEAD
echo "== uncommitted:"; git -C "$wt" status --short | sed 's/^/  /'
echo "== final report:"; jq -r 'select(.part.type=="text") | .part.text' "$log" 2>/dev/null | tail -60

# Save the full report beside the brief: HO-159-brief-partG.md -> HO-159-report-partG[-<ts>].md
name=$(basename "$brief_abs" .md); rname=${name/-brief-/-report-}
[[ "$rname" != "$name" ]] || rname="$name-report"
report="$ho_dir/$rname.md"; [[ ! -e "$report" ]] || report="$ho_dir/$rname-$ts.md"
{
  echo "# Agent report: $role ($model), run $ts"
  echo "Brief: $rel  |  Branch: $branch  |  Start: $start  |  End: $(git -C "$wt" rev-parse HEAD)"
  echo; echo "## Denied tool calls"
  jq -r 'select(.part.type=="tool" and (.part.state.error // "" | test("Permission denied"))) | "- " + (.part.state.input.command // .part.state.input.filePath // "?")' "$log" 2>/dev/null || true
  echo; echo "## New commits"; git -C "$wt" log --format='- %H %s' "$start"..HEAD
  echo; echo "## Final report"; jq -r 'select(.part.type=="text") | .part.text' "$log" 2>/dev/null
} > "$report"
echo "== report saved: ${report#"$wt_root"/} (orchestrator: commit it with the HO)"

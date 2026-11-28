#!/usr/bin/env bash
# Run the NGX reconciliation research batches through N parallel researcher lanes (HO-160).
# Usage: run_research.sh <lanes> [batch-name ...]   (no batch names = every brief in research/briefs)
# Resumable: a batch whose research/out/<batch>.json already validates is skipped.
# Each lane is its own git worktree (dispatch.sh places opencode.json in the worktree, so lanes can't share one).
set -uo pipefail
lanes=${1:?lanes}; shift
epm=$(cd "$(dirname "$0")/.." && pwd)              # coordinator EPM dir
top=$(git -C "$epm" rev-parse --show-toplevel)
rel=${epm#"$top"/}
base=${RESEARCH_LANE_DIR:-$(dirname "$top")/research-lanes}
out="$epm/research/out"; logs="$epm/research/logs"; progress="$epm/research/progress.log"
mkdir -p "$out" "$logs" "$base"
if (( $# )); then batches=("$@"); else mapfile -t batches < <(ls "$epm/research/briefs" | sed 's/\.md$//' | sort); fi

valid() {  # <file> <expected count>
  jq -e --argjson n "$2" 'type=="array" and length==$n and all(.[]; has("ticker") and has("ticker_status") and has("evidence"))' "$1" >/dev/null 2>&1
}
expected() { jq 'length' <(sed -n '/^```json$/,/^```$/p' "$epm/research/briefs/$1.md" | sed '1d;$d' | tail -n +1 | awk 'BEGIN{p=0} /^\[/{p=1} p' ); }
log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$progress"; }

lane_setup() {  # <n>
  local wt="$base/lane-$1"
  if [[ ! -d "$wt" ]]; then
    git -C "$top" worktree add -q -B "research/ngx-lane-$1" "$wt" HEAD >/dev/null 2>&1 || { log "lane-$1 setup FAILED"; return 1; }
  fi
  mkdir -p "$wt/$rel/research/out"
  rsync -a --delete "$epm/research/briefs/" "$wt/$rel/research/briefs/"
}

run_lane() {  # <n> <batch...>
  local n=$1; shift; local wt="$base/lane-$n/$rel"
  for b in "$@"; do
    local want; want=$(expected "$b")
    if valid "$out/$b.json" "$want"; then log "$b skip (already valid)"; continue; fi
    for attempt in 1 2; do
      rm -f "$wt/research/out/$b.json"
      log "$b start lane-$n attempt $attempt ($want companies)"
      DISPATCH_TIMEOUT=${RESEARCH_TIMEOUT:-2700} "$epm/.claude/orchestration/dispatch.sh" researcher "$wt" \
        "$wt/research/briefs/$b.md" "$logs" > "$logs/$b-attempt$attempt.txt" 2>&1
      if valid "$wt/research/out/$b.json" "$want"; then
        cp "$wt/research/out/$b.json" "$out/$b.json"
        log "$b DONE lane-$n ($(jq '[.[]|select(.ticker_status=="UNVERIFIED")]|length' "$out/$b.json") ticker-unverified)"
        break
      fi
      log "$b INVALID lane-$n attempt $attempt"
    done
    valid "$out/$b.json" "$want" || log "$b FAILED after 2 attempts"
  done
}

log "run start: ${#batches[@]} batches, $lanes lanes"
for ((i = 1; i <= lanes; i++)); do lane_setup "$i" || exit 1; done
pids=()
for ((i = 1; i <= lanes; i++)); do
  mine=(); for ((j = i - 1; j < ${#batches[@]}; j += lanes)); do mine+=("${batches[j]}"); done
  (( ${#mine[@]} )) && { run_lane "$i" "${mine[@]}" & pids+=($!); }
done
wait "${pids[@]}"
done_n=$(for b in "${batches[@]}"; do valid "$out/$b.json" "$(expected "$b")" && echo ok; done | wc -l)
log "run end: $done_n/${#batches[@]} batches valid"

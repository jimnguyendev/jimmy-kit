#!/usr/bin/env bash
# land.sh <worktree> <title> — the only way a packet reaches the default branch. Root only.
#
#   1. refuse a dirty worktree or a detached HEAD
#   2. fetch and merge origin/<main> into the packet branch (a conflict stops here)
#   3. run the gate runner on the merged result: a clean git merge can still fail to build
#   4. push the branch, open a PR/MR (or reuse the open one), wait until the forge says mergeable
#   5. merge with the head SHA, so nothing pushed after the gates can land
#   6. fast-forward the main checkout, then remove the worktree and the local branch
#
# Any failure exits non-zero and keeps the worktree. Never pipe this script into tail or grep
# before `&&`: the pipe hides its exit code.
#
# Environment:
#   ORCH_MAIN          default branch (default: origin/HEAD, else the main checkout's branch, else main)
#   ORCH_GATES         gate runner, called as `<runner> <worktree>` (default: gates.sh beside this file)
#   ORCH_FORGE         github | gitlab (default: github when origin is on github.com, else gitlab)
#   ORCH_MERGE_WAIT    seconds to wait for mergeability (default 180)
#   ORCH_MERGE_METHOD  github only: merge | squash | rebase (default merge)
#   GITLAB_TOKEN       gitlab: token with api scope (sent from a file descriptor, not argv)
#   GITLAB_API         gitlab: API base (default https://<origin host>/api/v4)
#   GITLAB_PROJECT     gitlab: numeric id or group/name path (default: path of the origin URL)
set -euo pipefail

say() { echo "land: $*"; }
die() { echo "land: $*" >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
wt="${1:-}"; title="${2:-}"
if [ -z "$wt" ] || [ ! -d "$wt" ] || [ -z "$title" ]; then
  echo "usage: land.sh <worktree> <title>" >&2; exit 2
fi
wt="$(cd "$wt" && pwd)"
repo="$(dirname "$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir)")"
[ "$wt" != "$repo" ] || die "$wt is the main checkout; land a packet worktree"
branch="$(git -C "$wt" symbolic-ref --short -q HEAD)" || die "$wt has a detached HEAD"
main="${ORCH_MAIN:-$(git -C "$repo" symbolic-ref --short -q refs/remotes/origin/HEAD 2>/dev/null || true)}"
main="${main#origin/}"
[ -n "$main" ] || main="$(git -C "$repo" symbolic-ref --short -q HEAD 2>/dev/null || true)"
main="${main:-main}"
[ "$branch" != "$main" ] || die "refusing to land $main onto itself"
[ -z "$(git -C "$wt" status --porcelain)" ] || die "$wt has uncommitted or untracked files; commit or clean them first"

say "merging origin/$main into $branch"
git -C "$wt" fetch -q origin "$main"
if ! git -C "$wt" merge -q --no-edit "origin/$main"; then
  git -C "$wt" merge --abort 2>/dev/null || true
  die "origin/$main conflicts with $branch; resolve in $wt and rerun"
fi

say "running gates on the merged result"
"${ORCH_GATES:-$here/gates.sh}" "$wt" || die "gates failed; nothing was pushed"
[ -z "$(git -C "$wt" status --porcelain --untracked-files=no)" ] ||
  die "a gate changed tracked files (generated code or formatting drift); commit the result and rerun"
sha="$(git -C "$wt" rev-parse HEAD)"

origin_url="$(git -C "$repo" remote get-url origin)"
forge="${ORCH_FORGE:-}"
if [ -z "$forge" ]; then
  case "$origin_url" in *github.com[:/]*) forge=github ;; *) forge=gitlab ;; esac
fi
wait_s="${ORCH_MERGE_WAIT:-180}"

say "pushing $branch ($sha)"
git -C "$wt" push -q -u origin "$branch"

jget() { # jget <key> — read one key from a JSON object (or the first element of an array) on stdin
  python3 -c 'import json,sys
d=json.load(sys.stdin)
d=d[0] if isinstance(d,list) and d else d
v=d.get(sys.argv[1],"") if isinstance(d,dict) else ""
print("" if v is None else v)' "$1"
}

land_github() {
  ghw() { (cd "$wt" && gh "$@"); }
  local num url st i
  num="$(ghw pr list --head "$branch" --base "$main" --state open --json number -q '.[0].number')"
  if [ -z "$num" ]; then
    url="$(ghw pr create --base "$main" --head "$branch" --title "$title" \
      --body "Landed by orchestrate land.sh after every gate passed on $sha.")"
    num="${url##*/}"
  fi
  say "PR #$num open; waiting for mergeability (up to ${wait_s}s)"
  st=UNKNOWN
  for ((i = 0; i < wait_s; i += 3)); do
    st="$(ghw pr view "$num" --json mergeable -q .mergeable)"
    case "$st" in MERGEABLE) break ;; CONFLICTING) die "PR #$num conflicts with $main" ;; esac
    sleep 3
  done
  [ "$st" = MERGEABLE ] || die "PR #$num not mergeable after ${wait_s}s (mergeable=$st)"
  ghw pr merge "$num" "--${ORCH_MERGE_METHOD:-merge}" --match-head-commit "$sha" ||
    die "merge of PR #$num refused; worktree kept"
  [ "$(ghw pr view "$num" --json state -q .state)" = MERGED ] || die "PR #$num is not MERGED; worktree kept"
  git -C "$repo" push -q origin --delete "$branch" 2>/dev/null || say "remote branch $branch left in place"
  say "merged PR #$num at $sha"
}

land_gitlab() {
  : "${GITLAB_TOKEN:?land: GITLAB_TOKEN with api scope is required for gitlab}"
  local parsed host path api pid iid st i out
  parsed="$(python3 -c 'import re,sys
m=re.match(r"^(?:[a-z+]+://)?(?:[^@/]+@)?([^/:]+)(?::[0-9]+)?[:/](.+?)(?:\.git)?/?$", sys.argv[1])
print(m.group(1)+" "+m.group(2) if m else "")' "$origin_url")"
  [ -n "$parsed" ] || die "cannot parse origin URL $origin_url; set GITLAB_API and GITLAB_PROJECT"
  host="${parsed%% *}"; path="${parsed#* }"
  api="${GITLAB_API:-https://$host/api/v4}"
  pid="$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1],safe=""))' "${GITLAB_PROJECT:-$path}")"
  gl() { curl -sS --fail-with-body -H @<(printf 'PRIVATE-TOKEN: %s\n' "$GITLAB_TOKEN") "$@"; }

  iid="$(gl "$api/projects/$pid/merge_requests?source_branch=$branch&target_branch=$main&state=opened" | jget iid)" ||
    die "cannot list merge requests at $api (check GITLAB_TOKEN and GITLAB_PROJECT)"
  if [ -z "$iid" ]; then
    iid="$(gl -X POST "$api/projects/$pid/merge_requests" \
      --data-urlencode "source_branch=$branch" --data-urlencode "target_branch=$main" \
      --data-urlencode "title=$title" -d remove_source_branch=true | jget iid)" ||
      die "cannot open a merge request for $branch"
  fi
  [ -n "$iid" ] || die "could not open or find the merge request for $branch"
  say "MR !$iid open; waiting for mergeability (up to ${wait_s}s)"
  st=unknown
  for ((i = 0; i < wait_s; i += 3)); do
    out="$(gl "$api/projects/$pid/merge_requests/$iid")"
    st="$(printf '%s' "$out" | jget detailed_merge_status)"
    [ -n "$st" ] || st="$(printf '%s' "$out" | jget merge_status)"
    case "$st" in mergeable|can_be_merged) break ;; conflict|cannot_be_merged|broken_status) die "MR !$iid cannot be merged ($st)" ;; esac
    sleep 3
  done
  case "$st" in mergeable|can_be_merged) ;; *) die "MR !$iid not mergeable after ${wait_s}s (status=$st)" ;; esac
  out="$(gl -X PUT "$api/projects/$pid/merge_requests/$iid/merge?sha=$sha&should_remove_source_branch=true")" ||
    die "merge of MR !$iid refused: $out"
  [ "$(printf '%s' "$out" | jget state)" = merged ] || die "MR !$iid is not merged: $out"
  say "merged MR !$iid at $sha"
}

case "$forge" in
  github) land_github ;;
  gitlab) land_gitlab ;;
  *) die "unknown ORCH_FORGE=$forge (github | gitlab)" ;;
esac

git -C "$repo" fetch -q origin "$main"
if [ "$(git -C "$repo" symbolic-ref --short -q HEAD || true)" = "$main" ] &&
   [ -z "$(git -C "$repo" status --porcelain --untracked-files=no)" ]; then
  git -C "$repo" merge -q --ff-only "origin/$main" || say "main checkout could not fast-forward; fetched only"
else
  say "main checkout is not a clean $main; fetched only"
fi

# Only now, after a confirmed merge, is the worktree disposable. Gate artifacts may be untracked.
git -C "$repo" worktree remove --force "$wt"
git -C "$repo" branch -D -q "$branch" 2>/dev/null || true
say "removed worktree $wt"

#!/usr/bin/env bash
# reset.sh — archive the current visitor's work and clear the workspace.
#
# Moves every generated file out of tasks/ into archive/<timestamp>/ so nothing
# is ever lost, then leaves tasks/ empty and ready for the next visitor.
# NON-DESTRUCTIVE: it only MOVES files. It never deletes and never touches git.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TS="$(date +%Y%m%d-%H%M%S)"

shopt -s nullglob dotglob
candidates=(tasks/*)
real=()
for f in "${candidates[@]}"; do
  base="$(basename "$f")"
  [ "$base" = ".gitkeep" ] && continue
  real+=("$f")
done

if [ "${#real[@]}" -eq 0 ]; then
  echo "✓ tasks/ already clean — nothing to archive. Ready for the next visitor."
  exit 0
fi

mkdir -p "archive/$TS"
mv "${real[@]}" "archive/$TS"/
echo "✓ Archived ${#real[@]} item(s) to archive/$TS/ — tasks/ is clean. Ready for the next visitor."

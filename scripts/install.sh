#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
SKILL_NAMES=(sudis-rebuttal-with-me sudis-arr-rebuttal-with-me)
UNIFIED_DIR="${SUDIS_SKILLS_DIR:-$HOME/.agents/skills}"
DRY_RUN=0

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ "${1:-}" == "--uninstall" ]]; then
  for skill_name in "${SKILL_NAMES[@]}"; do
    target="$UNIFIED_DIR/$skill_name"
    if [[ -L "$target" ]]; then
      rm "$target"
      echo "removed $target"
    elif [[ -e "$target" ]]; then
      echo "refusing to remove non-symlink: $target" >&2
      exit 1
    fi
  done
  exit 0
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--dry-run|--uninstall]" >&2
  exit 2
fi

link_one() {
  local destination=$1
  local source=$2
  if (( DRY_RUN )); then
    echo "would link $destination -> $source"
    return
  fi
  mkdir -p "$(dirname "$destination")"
  if [[ -e "$destination" && ! -L "$destination" ]]; then
    echo "refusing to replace non-symlink: $destination" >&2
    exit 1
  fi
  ln -sfn "$source" "$destination"
  echo "linked $destination -> $source"
}

for skill_name in "${SKILL_NAMES[@]}"; do
  source_dir="$ROOT_DIR/skills/$skill_name"
  if [[ ! -f "$source_dir/SKILL.md" ]]; then
    echo "missing skill source: $source_dir/SKILL.md" >&2
    exit 1
  fi
  link_one "$UNIFIED_DIR/$skill_name" "$source_dir"
  # Compatibility discovery paths. The unified directory remains the source of truth.
  for base in "$HOME/.codex/skills" "$HOME/.Codex/skills" "$HOME/.claude/skills"; do
    if [[ "$base" != "$UNIFIED_DIR" ]]; then
      link_one "$base/$skill_name" "$source_dir"
    fi
  done
done

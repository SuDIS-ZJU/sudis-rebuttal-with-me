#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
SKILL_NAME=sudis-rebuttal-with-me
SOURCE_DIR="$ROOT_DIR/skills/$SKILL_NAME"
UNIFIED_DIR="${SUDIS_SKILLS_DIR:-$HOME/.agents/skills}"
TARGET="$UNIFIED_DIR/$SKILL_NAME"
DRY_RUN=0

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ "${1:-}" == "--uninstall" ]]; then
  if [[ -L "$TARGET" ]]; then
    rm "$TARGET"
    echo "removed $TARGET"
  else
    echo "refusing to remove non-symlink: $TARGET" >&2
    exit 1
  fi
  exit 0
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--dry-run|--uninstall]" >&2
  exit 2
fi

if [[ ! -f "$SOURCE_DIR/SKILL.md" ]]; then
  echo "missing skill source: $SOURCE_DIR/SKILL.md" >&2
  exit 1
fi

link_one() {
  local destination=$1
  if (( DRY_RUN )); then
    echo "would link $destination -> $SOURCE_DIR"
    return
  fi
  mkdir -p "$(dirname "$destination")"
  if [[ -e "$destination" && ! -L "$destination" ]]; then
    echo "refusing to replace non-symlink: $destination" >&2
    exit 1
  fi
  ln -sfn "$SOURCE_DIR" "$destination"
  echo "linked $destination -> $SOURCE_DIR"
}

link_one "$TARGET"

# Compatibility discovery paths. The unified directory remains the source of truth.
for base in "$HOME/.codex/skills" "$HOME/.Codex/skills" "$HOME/.claude/skills"; do
  if [[ "$base" != "$UNIFIED_DIR/skills" && "$base/$SKILL_NAME" != "$TARGET" ]]; then
    link_one "$base/$SKILL_NAME"
  fi
done

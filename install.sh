#!/usr/bin/env bash

set -euo pipefail

PLUGIN_NAME="mathmodeling-skills"
MARKETPLACE_NAME="mathmodeling-skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
TARGET="both"
MODE="plugin"
CLAUDE_SCOPE="user"
PROJECT_DIR="$PWD"
PROJECT_DIR_SET=0
DRY_RUN=0
FORCE=0
BACKUP_STAMP="$(date +%Y%m%d-%H%M%S)"

usage() {
  cat <<'EOF'
Install MathModeling Skills for Claude Code, Codex, or both.

Usage:
  ./install.sh [options]

Options:
  --target claude|codex|both   Host to install for (default: both)
  --mode plugin|project        Native plugin or project files (default: plugin)
  --scope user|project|local   Claude plugin scope (default: user)
  --project-dir PATH           Project used by project mode or Claude project/local scope
  --force                      Back up and replace conflicting project files
  --dry-run                    Print mutating commands without running them
  -h, --help                   Show this help

Examples:
  ./install.sh
  ./install.sh --target claude
  ./install.sh --target both --mode project --project-dir /path/to/contest
  ./install.sh --mode project --project-dir . --force
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '%s\n' "$*"
}

print_command() {
  printf '  +'
  printf ' %q' "$@"
  printf '\n'
}

run() {
  print_command "$@"
  if [ "$DRY_RUN" -eq 0 ]; then
    "$@"
  fi
}

run_in_project() {
  local directory="$1"
  shift
  printf '  + cd %q &&' "$directory"
  printf ' %q' "$@"
  printf '\n'
  if [ "$DRY_RUN" -eq 0 ]; then
    (
      cd "$directory"
      "$@"
    )
  fi
}

require_command() {
  if [ "$DRY_RUN" -eq 0 ] && ! command -v "$1" >/dev/null 2>&1; then
    die "required command not found: $1"
  fi
}

json_has() {
  local json="$1"
  local needle="$2"
  printf '%s' "$json" | grep -Fq "$needle"
}

backup_path() {
  local destination="$1"
  printf '%s.backup-%s-%s' "$destination" "$BACKUP_STAMP" "$$"
}

prepare_destination() {
  local source="$1"
  local destination="$2"
  local kind="$3"

  if [ ! -e "$destination" ]; then
    return 0
  fi

  if [ "$kind" = "file" ] && cmp -s "$source" "$destination"; then
    log "  = unchanged: $destination"
    return 1
  fi

  if [ "$kind" = "tree" ] && diff -qr --exclude='.DS_Store' "$source" "$destination" >/dev/null 2>&1; then
    log "  = unchanged: $destination"
    return 1
  fi

  if [ "$FORCE" -ne 1 ]; then
    die "destination exists and differs: $destination (rerun with --force to back it up and replace it)"
  fi

  local backup
  backup="$(backup_path "$destination")"
  log "  ! backing up: $destination -> $backup"
  if [ "$DRY_RUN" -eq 0 ]; then
    mv "$destination" "$backup"
  fi
  return 0
}

copy_file() {
  local source="$1"
  local destination="$2"
  if prepare_destination "$source" "$destination" file; then
    run mkdir -p "$(dirname "$destination")"
    run cp "$source" "$destination"
  fi
}

copy_tree() {
  local source="$1"
  local destination="$2"
  if prepare_destination "$source" "$destination" tree; then
    run mkdir -p "$(dirname "$destination")"
    run cp -R "$source" "$destination"
  fi
}

install_claude_plugin() {
  require_command claude
  log "Installing native Claude Code plugin..."

  local marketplaces=""
  local plugins=""
  if [ "$DRY_RUN" -eq 0 ]; then
    marketplaces="$(claude plugin marketplace list --json 2>/dev/null || true)"
  fi

  if json_has "$marketplaces" "\"name\": \"$MARKETPLACE_NAME\""; then
    run_in_project "$PROJECT_DIR" claude plugin marketplace update "$MARKETPLACE_NAME"
  else
    run_in_project "$PROJECT_DIR" claude plugin marketplace add "$SCRIPT_DIR" --scope "$CLAUDE_SCOPE"
  fi

  if [ "$DRY_RUN" -eq 0 ]; then
    plugins="$(claude plugin list --json 2>/dev/null || true)"
  fi

  if json_has "$plugins" "\"id\": \"$PLUGIN_NAME@$MARKETPLACE_NAME\""; then
    run_in_project "$PROJECT_DIR" claude plugin update "$PLUGIN_NAME@$MARKETPLACE_NAME" --scope "$CLAUDE_SCOPE"
  else
    run_in_project "$PROJECT_DIR" claude plugin install "$PLUGIN_NAME@$MARKETPLACE_NAME" --scope "$CLAUDE_SCOPE"
  fi
}

install_codex_plugin() {
  require_command codex
  log "Installing native Codex plugin..."

  local marketplaces=""
  if [ "$DRY_RUN" -eq 0 ]; then
    marketplaces="$(codex plugin marketplace list --json 2>/dev/null || true)"
  fi

  if ! json_has "$marketplaces" "\"name\": \"$MARKETPLACE_NAME\""; then
    run codex plugin marketplace add "$SCRIPT_DIR"
  else
    log "  = marketplace already configured: $MARKETPLACE_NAME"
  fi

  run codex plugin add "$PLUGIN_NAME@$MARKETPLACE_NAME"
}

install_claude_project() {
  log "Deploying Claude Code project files..."
  copy_tree "$SCRIPT_DIR/.claude/skills" "$PROJECT_DIR/.claude/skills"
  copy_file "$SCRIPT_DIR/.claude/settings.json" "$PROJECT_DIR/.claude/settings.json"
  copy_file "$SCRIPT_DIR/CLAUDE.md" "$PROJECT_DIR/CLAUDE.md"
  copy_file "$SCRIPT_DIR/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
}

install_codex_project() {
  log "Deploying Codex project files..."
  copy_tree "$SCRIPT_DIR/.codex/skills" "$PROJECT_DIR/.codex/skills"
  copy_file "$SCRIPT_DIR/AGENTS.md" "$PROJECT_DIR/AGENTS.md"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || die "--target requires a value"
      TARGET="$2"
      shift 2
      ;;
    --mode)
      [ "$#" -ge 2 ] || die "--mode requires a value"
      MODE="$2"
      shift 2
      ;;
    --scope)
      [ "$#" -ge 2 ] || die "--scope requires a value"
      CLAUDE_SCOPE="$2"
      shift 2
      ;;
    --project-dir)
      [ "$#" -ge 2 ] || die "--project-dir requires a value"
      PROJECT_DIR="$2"
      PROJECT_DIR_SET=1
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

case "$TARGET" in
  claude|codex|both) ;;
  *) die "invalid --target: $TARGET" ;;
esac

case "$MODE" in
  plugin|project) ;;
  *) die "invalid --mode: $MODE" ;;
esac

case "$CLAUDE_SCOPE" in
  user|project|local) ;;
  *) die "invalid --scope: $CLAUDE_SCOPE" ;;
esac

if [ "$MODE" = "plugin" ] && [ "$CLAUDE_SCOPE" != "user" ] && [ "$PROJECT_DIR_SET" -ne 1 ] && { [ "$TARGET" = "claude" ] || [ "$TARGET" = "both" ]; }; then
  die "--scope $CLAUDE_SCOPE requires an explicit --project-dir"
fi

[ -d "$SCRIPT_DIR/plugins/$PLUGIN_NAME/skills" ] || die "plugin package is incomplete; run scripts/sync-plugin.sh"
[ -f "$SCRIPT_DIR/.claude-plugin/marketplace.json" ] || die "Claude marketplace manifest is missing"
[ -f "$SCRIPT_DIR/.agents/plugins/marketplace.json" ] || die "Codex marketplace manifest is missing"

if [ ! -d "$PROJECT_DIR" ]; then
  die "project directory does not exist: $PROJECT_DIR"
fi
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd -P)"

log "MathModeling Skills installer"
log "  target: $TARGET"
log "  mode: $MODE"

if [ "$MODE" = "plugin" ]; then
  if [ "$TARGET" = "claude" ] || [ "$TARGET" = "both" ]; then
    install_claude_plugin
  fi
  if [ "$TARGET" = "codex" ] || [ "$TARGET" = "both" ]; then
    install_codex_plugin
  fi
else
  log "  project: $PROJECT_DIR"
  if [ "$TARGET" = "claude" ] || [ "$TARGET" = "both" ]; then
    install_claude_project
  fi
  if [ "$TARGET" = "codex" ] || [ "$TARGET" = "both" ]; then
    install_codex_project
  fi
fi

if [ "$DRY_RUN" -eq 1 ]; then
  log "Dry run complete; no mutating command was executed."
else
  log "Installation complete. Start a new Claude Code or Codex session to load the plugin."
fi

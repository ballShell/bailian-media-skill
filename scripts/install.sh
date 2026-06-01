#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CC_SWITCH_HOME="${CC_SWITCH_HOME:-$HOME/.cc-switch}"

mkdir -p "$CC_SWITCH_HOME/skills" "$CC_SWITCH_HOME/tools"
rm -rf "$CC_SWITCH_HOME/skills/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media"
cp -R "$ROOT_DIR/skill/bailian-media" "$CC_SWITCH_HOME/skills/bailian-media"
cp -R "$ROOT_DIR/tools/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media"
chmod +x "$CC_SWITCH_HOME/tools/bailian-media/bailian-media" \
  "$CC_SWITCH_HOME/tools/bailian-media/bailian_media.py" \
  "$CC_SWITCH_HOME/skills/bailian-media/scripts/bailian-media"

install_link() {
  local link_path="$1"
  local target_path="$2"
  mkdir -p "$(dirname "$link_path")"
  rm -rf "$link_path"
  ln -s "$target_path" "$link_path"
}

install_link "$HOME/.codex/skills/bailian-media" "$CC_SWITCH_HOME/skills/bailian-media"
install_link "$HOME/.codex/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media"
install_link "$HOME/.claude/skills/bailian-media" "$CC_SWITCH_HOME/skills/bailian-media"
install_link "$HOME/.claude/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media"
install_link "$HOME/.config/opencode/skills/bailian-media" "$CC_SWITCH_HOME/skills/bailian-media"
install_link "$HOME/.config/opencode/tools/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media"

mkdir -p "$HOME/.local/bin"
install_link "$HOME/.local/bin/bailian-media" "$CC_SWITCH_HOME/tools/bailian-media/bailian-media"

echo "Installed bailian-media skill and CLI under $CC_SWITCH_HOME"

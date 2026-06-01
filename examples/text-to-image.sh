#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/tools/bailian-media/bailian-media" text-to-image \
  --prompt "一张中文科技发布会海报，标题为「灵感发生器」，玻璃质感产品装置，现代排版" \
  --models auto

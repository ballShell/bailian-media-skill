#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/tools/bailian-media/bailian-media" image-to-video \
  --prompt "让画面中的人物缓慢转头看向镜头，电影感光影" \
  --media '[{"type":"first_frame","url":"https://example.com/first.png"}]' \
  --models auto

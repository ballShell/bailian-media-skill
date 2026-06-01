---
name: bailian-media
description: Generate and edit images/videos with Alibaba Cloud Bailian DashScope models from agent workflows.
tags:
  - image-generation
  - video-generation
  - dashscope
  - bailian
  - agent-tools
allowed-tools:
  - read
  - write
  - exec
---

# Bailian Media

## Overview

Use this skill when the user asks to generate images, edit images, generate videos, create image-to-video/reference-to-video results, or edit videos with Alibaba Cloud Bailian/DashScope media models.

The bundled CLI groups same-capability models behind one command. With `--models auto`, each selected model returns one result set, allowing the agent to present multiple creative candidates to the user for selection.

Supported model families include Wan, Qwen-Image, Z-Image, HappyHorse, and Kling/可灵.

## Instructions

1. Confirm `DASHSCOPE_API_KEY` is available in the environment. Do not print the key.

2. Pick exactly one capability for the request:
   - `text-to-image` for prompt-only image generation.
   - `image-edit` for editing or transforming one or more images.
   - `text-to-video` for prompt-only video generation.
   - `image-to-video` for first-frame, last-frame, or image-driven video generation.
   - `reference-to-video` for video generation from character/object/style reference images.
   - `video-edit` for editing an existing video with an instruction.

3. Use `--models auto` unless the user names a model family or model ID. If the user asks for Wan, Qwen-Image, Z-Image, HappyHorse, Kling, or 可灵, pass explicit model IDs that match the request.

4. Run the CLI:

```bash
bailian-media text-to-image --prompt "..." --models auto
```

If `bailian-media` is not on `PATH`, run the installed wrapper:

```bash
scripts/bailian-media text-to-image --prompt "..." --models auto
```

5. For commands that need media input, pass only reachable URLs through `--media`. The CLI currently rejects local image/video paths.

6. Inspect the CLI JSON output, especially `summary.json`. Present successful outputs grouped by model name. If multiple models succeed, ask the user which result to keep, refine, or use as the next input.

7. If some models fail and at least one succeeds, do not treat the whole task as failed. Report the successful results first, then briefly mention failed models and their errors.

8. Save and reuse output paths from the CLI for follow-up edits. Generated assets are saved under:

```text
~/.cc-switch/outputs/bailian-media/{capability}/{timestamp}/
```

9. Read `references/api.md` only when you need detailed model-family notes, media examples, or command examples.

## Examples

Prompt-only image generation:

```bash
bailian-media text-to-image \
  --prompt "一张中文科技发布会海报，标题为「灵感发生器」，玻璃质感产品装置" \
  --models auto
```

Explicit text-to-image models:

```bash
bailian-media text-to-image \
  --prompt "极简产品摄影，一只透明玻璃香水瓶，高清细节" \
  --models wan2.7-image-pro qwen-image-2.0-pro z-image-turbo
```

Image edit:

```bash
bailian-media image-edit \
  --prompt "把汽车车身改成哑光黑，保留构图和背景" \
  --media '[{"type":"image","url":"https://example.com/car.png"}]' \
  --models auto
```

Image-to-video with a first frame:

```bash
bailian-media image-to-video \
  --prompt "让画面中的人物缓慢转头看向镜头，电影感光影" \
  --media '[{"type":"first_frame","url":"https://example.com/first.png"}]' \
  --models auto
```

Typical successful output shape:

```json
{
  "ok": true,
  "run_dir": "~/.cc-switch/outputs/bailian-media/text-to-image/20260601-210000",
  "results": [
    {
      "ok": true,
      "model": "wan2.7-image-pro",
      "outputs": [
        {
          "type": "image",
          "local_path": "~/.cc-switch/outputs/.../result-1.png"
        }
      ]
    }
  ]
}
```

## Constraints

- Do NOT print, log, or commit `DASHSCOPE_API_KEY`.
- Do NOT commit generated outputs, signed DashScope URLs, response JSON files, or private media assets.
- Do NOT pass local media paths to `--media`; upload media first and pass a reachable URL.
- Always use one capability command rather than calling model-specific endpoints manually.
- Always group multiple successful outputs by model name when presenting choices.
- Always read the top-level `summary.json` before claiming completion.
- Prefer `--models auto` for exploratory creative requests unless the user specifies a model or family.

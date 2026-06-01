---
name: bailian-media
description: Generate or edit images/videos through Alibaba Cloud Bailian DashScope media models. Use when a user asks to create images, edit images, generate videos, create image-to-video/reference-to-video results, or edit videos with Wan, Qwen-Image, Z-Image, HappyHorse, or Kling/可灵 models.
---

# Bailian Media

Use this skill for Alibaba Cloud Bailian/DashScope image and video creation. The bundled CLI groups same-capability models behind one command and can run multiple candidate models in one request, returning one result set per model so the agent can show options to the user.

## Tool

Run:

```bash
bailian-media --help
```

If `bailian-media` is not on `PATH`, use the installed script wrapper in this skill:

```bash
scripts/bailian-media --help
```

Requires:

```bash
DASHSCOPE_API_KEY
```

Optional:

```bash
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1
BAILIAN_MEDIA_OUTPUT_ROOT=$HOME/.cc-switch/outputs/bailian-media
```

## Commands

- `text-to-image`: prompt to image candidates.
- `image-edit`: edit one or more images with a prompt.
- `text-to-video`: prompt to video candidates.
- `image-to-video`: first-frame/last-frame/video-continuation generation.
- `reference-to-video`: generate video from reference images.
- `video-edit`: edit a video with an instruction.
- `list-models`: inspect supported models.

Each creative command accepts:

```bash
--prompt "..."
--models auto
--models model-a model-b
--media '[{"type":"first_frame","url":"https://..."}]'
--parameters '{"duration":5,"resolution":"720P"}'
--wait
--download
```

`--models auto` selects a curated default set for that capability. Explicit model IDs override the default set.

## Selection Workflow

1. Classify the request into one capability: `text-to-image`, `image-edit`, `text-to-video`, `image-to-video`, `reference-to-video`, or `video-edit`.
2. Use `--models auto` unless the user names a family/model such as Wan, Qwen-Image, HappyHorse, Z-Image, Kling, or 可灵.
3. For broad creative requests, let several models run and present the generated options by model name.
4. When multiple successful outputs exist, ask the user to choose which result to keep or iterate on.
5. For follow-up edits, use the selected output path/URL as the next command's media input.

## Default Model Groups

- `text-to-image`: `wan2.7-image-pro`, `qwen-image-2.0-pro`, `z-image-turbo`.
- `image-edit`: `wan2.7-image-pro`, `qwen-image-2.0-pro`.
- `text-to-video`: `wan2.7-t2v`, `happyhorse-1.0-t2v`, `kling/kling-v3-video-generation`.
- `image-to-video`: `wan2.7-i2v`, `happyhorse-1.0-i2v`, `kling/kling-v3-video-generation`.
- `reference-to-video`: `wan2.7-r2v`, `happyhorse-1.0-r2v`, `kling/kling-v3-omni-video-generation`.
- `video-edit`: `wan2.7-videoedit`, `happyhorse-1.0-video-edit`, `kling/kling-v3-omni-video-generation`.

## Media Inputs

DashScope media APIs generally require reachable URLs. The CLI currently rejects local media paths with a clear error. Upload local files to OSS or another accessible URL first, then pass that URL in `--media`.

Examples:

```json
[{"type":"image","url":"https://example.com/input.png"}]
```

```json
[{"type":"first_frame","url":"https://example.com/first.png"},{"type":"last_frame","url":"https://example.com/last.png"}]
```

```json
[{"type":"reference_image","url":"https://example.com/person.png"}]
```

```json
[{"type":"base","url":"https://example.com/input.mp4"}]
```

## Output Contract

The CLI prints JSON and saves all run artifacts under:

```text
~/.cc-switch/outputs/bailian-media/{capability}/{timestamp}/
```

Each model gets its own directory with:

- `request.json`
- `create-response.json`
- `final-response.json` when waited
- downloaded `result-*` files when URLs are available
- `error.json` on model-specific failure

Always inspect the top-level `summary.json`. If at least one model succeeds, present successful outputs and note failed models briefly.

## References

For model families, parameter notes, and command examples, read `references/api.md` only when more detail is needed.

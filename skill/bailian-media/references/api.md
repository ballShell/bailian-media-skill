# Bailian Media Reference

## Capability Commands

List models:

```bash
bailian-media list-models
```

Text to image with default model set:

```bash
bailian-media text-to-image \
  --prompt "生成一张中文科技发布会海报，清晰标题，产品主视觉" \
  --models auto \
  --parameters '{"n":1}'
```

Text to image with explicit models:

```bash
bailian-media text-to-image \
  --prompt "写实产品摄影，一只透明玻璃香水瓶，冷暖对比布光" \
  --models wan2.7-image-pro qwen-image-2.0-pro
```

Note: Wan image models use the async image-generation endpoint. Qwen-Image 2.0 and Z-Image use the sync multimodal-generation endpoint and return image URLs immediately.

Image edit:

```bash
bailian-media image-edit \
  --prompt "把汽车车身改成哑光黑，保留构图和背景" \
  --media '[{"type":"image","url":"https://example.com/car.png"}]' \
  --models auto
```

Text to video:

```bash
bailian-media text-to-video \
  --prompt "雨夜赛博朋克街头，镜头缓慢推进，霓虹倒影，电影感" \
  --models auto \
  --parameters '{"duration":5,"resolution":"720P"}'
```

Image to video:

```bash
bailian-media image-to-video \
  --prompt "让画面中的人物转头看向镜头，头发被微风吹动" \
  --media '[{"type":"first_frame","url":"https://example.com/first.png"}]' \
  --models auto
```

Reference to video:

```bash
bailian-media reference-to-video \
  --prompt "保持参考人物一致，在咖啡馆中自然走动，电影感光影" \
  --media '[{"type":"reference_image","url":"https://example.com/person.png"}]' \
  --models auto
```

Video edit:

```bash
bailian-media video-edit \
  --prompt "把视频改成日落海边风格，保留人物动作" \
  --media '[{"type":"base","url":"https://example.com/input.mp4"}]' \
  --models auto
```

## Model Families

Wan:

- Good default for high-quality image generation, image editing, text-to-video, image-to-video, reference-to-video, and video edit.
- Common models: `wan2.7-image-pro`, `wan2.7-image`, `wan2.7-t2v`, `wan2.7-i2v`, `wan2.7-r2v`, `wan2.7-videoedit`.

Qwen-Image:

- Good for Chinese text rendering, posters, product layouts, and instruction-heavy image editing.
- Common models: `qwen-image-2.0-pro`, `qwen-image-2.0`.

Z-Image:

- Fast text-to-image candidate for quick alternatives.
- Common model: `z-image-turbo`.

HappyHorse:

- Good for creative sound-capable video alternatives.
- Common models: `happyhorse-1.0-t2v`, `happyhorse-1.0-i2v`, `happyhorse-1.0-r2v`, `happyhorse-1.0-video-edit`.

Kling / 可灵:

- Good for Kling-specific image/video generation and omni workflows.
- Common models: `kling/kling-v3-image-generation`, `kling/kling-v3-omni-image-generation`, `kling/kling-v3-video-generation`, `kling/kling-v3-omni-video-generation`.
- Usually requires China mainland Beijing region and prior Kling AI enablement in Bailian.

## JSON Output Shape

The CLI writes one top-level summary:

```json
{
  "ok": true,
  "run_dir": "$HOME/.cc-switch/outputs/bailian-media/text-to-image/20260601-210000",
  "capability": "text_to_image",
  "results": [
    {
      "ok": true,
      "model": "wan2.7-image-pro",
      "task_id": "...",
      "outputs": [
        {
          "type": "image",
          "url": "https://...",
          "local_path": "$HOME/.cc-switch/outputs/.../result-1.png"
        }
      ]
    }
  ]
}
```

When presenting results, group by model name. If multiple model results are acceptable, ask the user to choose before editing or producing a final chosen asset.

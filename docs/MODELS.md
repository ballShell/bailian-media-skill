# Model Registry

The canonical model registry is `skill/bailian-media/tools/models.json`.

## Capability Defaults

- `text_to_image`: Wan, Qwen-Image, Z-Image candidates.
- `image_edit`: Wan and Qwen-Image candidates.
- `text_to_video`: Wan, HappyHorse, Kling candidates.
- `image_to_video`: Wan, HappyHorse, Kling candidates.
- `reference_to_video`: Wan, HappyHorse, Kling omni candidates.
- `video_edit`: Wan, HappyHorse, Kling omni candidates.

## Notes

Kling/可灵 models may require China mainland Beijing region and prior enablement in Alibaba Cloud Bailian.

Qwen-Image 2.0 and Z-Image use the synchronous multimodal generation endpoint. Wan image models use the asynchronous image generation endpoint.

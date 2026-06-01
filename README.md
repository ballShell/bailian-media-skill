# Bailian Media Skill

中文优先的阿里云百炼/DashScope 图像与视频生成 Skill + CLI。它可以让 Codex、Claude Code、opencode 或普通 Shell 调用百炼的 Wan、Qwen-Image、Z-Image、HappyHorse、可灵/Kling 等多媒体模型。

English overview is available below: [English](#english).

## 这个项目解决什么问题

百炼针对同一个创作需求通常提供多个可选模型。例如“文生图”可以选择 Wan、Qwen-Image、Z-Image 或可灵；“文生视频”也可能有 Wan、HappyHorse、可灵等候选。

这个项目把同类模型能力聚合成一个命令：

```bash
bailian-media text-to-image --models auto
bailian-media text-to-video --models auto
```

当使用 `--models auto` 时，CLI 会为该能力选择一组默认候选模型，并让每个模型各生成一个结果。Agent 可以把多个候选结果展示给用户，由用户决定保留、继续修改或重新生成。

## 核心能力

- 从环境变量读取 `DASHSCOPE_API_KEY`，不把密钥写入文件。
- 一个创作能力对应一个命令：
  - `text-to-image`：文生图
  - `image-edit`：图像编辑/图生图
  - `text-to-video`：文生视频
  - `image-to-video`：图生视频，支持首帧/首尾帧等媒体输入
  - `reference-to-video`：参考图生视频
  - `video-edit`：视频编辑
- `--models auto` 自动选择同类候选模型。
- 允许显式指定模型，例如 `wan2.7-image-pro qwen-image-2.0-pro z-image-turbo`。
- 每个模型单独保存请求、响应、下载结果和错误信息。
- 单个模型失败不会影响其它模型继续返回结果。
- Python 标准库实现，无第三方运行时依赖。

## 支持的模型家族

当前模型注册表位于 [tools/bailian-media/models.json](tools/bailian-media/models.json)，覆盖：

- Wan：图像生成、图像编辑、文生视频、图生视频、参考生视频、视频编辑
- Qwen-Image：中文文字渲染、海报、产品图、图像编辑
- Z-Image：快速文生图
- HappyHorse：文生视频、图生视频、参考生视频、视频编辑
- 可灵/Kling：图像生成、视频生成、Omni 视频工作流

更多说明见 [docs/MODELS.md](docs/MODELS.md)。

## 项目结构

```text
.
├── skill/bailian-media/          # Agent Skill 包
├── tools/bailian-media/          # CLI 与模型注册表
├── scripts/install.sh            # 本地安装脚本
├── examples/                     # 示例命令
└── docs/                         # 补充文档
```

## 环境要求

- Python 3.9+
- 阿里云百炼/DashScope API Key

设置环境变量：

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

可选环境变量：

```bash
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/api/v1"
export BAILIAN_MEDIA_OUTPUT_ROOT="$HOME/.cc-switch/outputs/bailian-media"
```

提示：可灵/Kling 模型通常要求中国内地北京地域，并且需要在百炼控制台开通可灵 AI。

## 快速开始

查看模型：

```bash
./tools/bailian-media/bailian-media list-models
```

使用默认候选模型生成图片：

```bash
./tools/bailian-media/bailian-media text-to-image \
  --prompt "一张中文科技发布会海报，标题为「灵感发生器」，玻璃质感产品装置" \
  --models auto
```

显式指定模型：

```bash
./tools/bailian-media/bailian-media text-to-image \
  --prompt "极简产品摄影，一只透明玻璃香水瓶，高清细节" \
  --models wan2.7-image-pro qwen-image-2.0-pro z-image-turbo
```

图生视频，传入远程首帧图片：

```bash
./tools/bailian-media/bailian-media image-to-video \
  --prompt "让画面中的人物缓慢转头看向镜头，电影感光影" \
  --media '[{"type":"first_frame","url":"https://example.com/first.png"}]' \
  --models auto
```

视频编辑：

```bash
./tools/bailian-media/bailian-media video-edit \
  --prompt "把视频改成日落海边风格，保留人物动作" \
  --media '[{"type":"base","url":"https://example.com/input.mp4"}]' \
  --models auto
```

## 安装到 Agent

安装到本机常见 Agent Skill 目录：

```bash
./scripts/install.sh
```

默认安装目标：

- `~/.cc-switch/skills/bailian-media`
- `~/.cc-switch/tools/bailian-media`
- `~/.codex/skills/bailian-media`
- `~/.claude/skills/bailian-media`
- `~/.config/opencode/skills/bailian-media`
- `~/.local/bin/bailian-media`

安装脚本会把项目复制到 `~/.cc-switch`，再为 Codex、Claude Code、opencode 创建软链接。之后在 Agent 中触发 `bailian-media` skill，或者直接在命令行使用：

```bash
bailian-media list-models
```

## 输出目录

默认输出位置：

```text
~/.cc-switch/outputs/bailian-media/{capability}/{timestamp}/
```

每个模型会有独立目录：

```text
text-to-image/20260601-210000/
├── wan2.7-image-pro/
│   ├── request.json
│   ├── create-response.json
│   ├── final-response.json
│   └── result-1.png
├── qwen-image-2.0-pro/
│   ├── request.json
│   ├── create-response.json
│   └── result-1.png
└── summary.json
```

`summary.json` 是 Agent 最应该读取的文件，它会列出每个模型是否成功、输出文件路径和错误信息。

## 媒体输入说明

百炼的图片/视频接口通常要求可公网访问的 URL。当前 CLI 会拒绝本地文件路径，并提示先上传到 OSS 或其它可访问地址。

示例：

```json
[{"type":"image","url":"https://example.com/input.png"}]
```

```json
[
  {"type":"first_frame","url":"https://example.com/first.png"},
  {"type":"last_frame","url":"https://example.com/last.png"}
]
```

## 安全提醒

不要提交：

- `.env`
- API Key
- 生成结果
- 含有临时签名 URL 的响应 JSON
- 私有图片/视频素材

更多见 [SECURITY.md](SECURITY.md)。

## 开发检查

```bash
python3 -m py_compile tools/bailian-media/bailian_media.py
python3 -m json.tool tools/bailian-media/models.json >/dev/null
./tools/bailian-media/bailian-media list-models
```

## English

Bailian Media Skill is an agent skill and dependency-free Python CLI for Alibaba Cloud Bailian/DashScope media generation models.

It groups comparable models behind capability-based commands. With `--models auto`, each selected model produces its own result, so an agent can show multiple creative options and let the user choose.

### Features

- Reads `DASHSCOPE_API_KEY` from the environment.
- Supports text-to-image, image edit, text-to-video, image-to-video, reference-to-video, and video edit.
- Supports Wan, Qwen-Image, Z-Image, HappyHorse, and Kling model families.
- Saves request, response, downloaded outputs, and per-model errors.
- Continues when one candidate model fails and another succeeds.
- Uses only the Python standard library.

### Quick Start

```bash
export DASHSCOPE_API_KEY="your-api-key"
./tools/bailian-media/bailian-media list-models
./tools/bailian-media/bailian-media text-to-image \
  --prompt "A clean product poster with Chinese title text" \
  --models auto
```

### Install For Agents

```bash
./scripts/install.sh
```

The installer copies the skill and CLI to `~/.cc-switch`, then creates symlinks for Codex, Claude Code, and opencode.

### License

MIT. See [LICENSE](LICENSE).

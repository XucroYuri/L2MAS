# Live2D Multi-Agent Animation System

[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-orange.svg)](https://modelcontextprotocol.io)
[![A2A](https://img.shields.io/badge/A2A-1.0-purple.svg)](https://a2a-protocol.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

面向 2026 协议生态的 Live2D 多 Agent 动画生成原型，目标是逐步达到生产可部署。

本项目探索用 A2A 1.0 连接多个创作 Agent，用 MCP 2025-11-25 + Streamable HTTP + Tasks 暴露动画生产工具，并通过 provider registry 同时接入云端模型和本地运行模型。Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 等仅作为 2026 能力基准，不是系统硬依赖。

## 当前状态

这是一个两阶段演进项目：

| 阶段 | 目标 | 状态 |
| --- | --- | --- |
| MVP 原型 | 在单机或本地 Docker 中跑通 `script -> storyboard -> model -> voice -> motion -> render` | 进行中 |
| v2.0 架构 | 扩展为 A2A 注册发现、MCP 工具集群、任务流式进度、Kubernetes、观测、安全和多租户 | 规划中 |

当前仓库已有 5 个 Agent 骨架：Director、Modeling、Animation、Voice、Renderer。Writer、Artist、LipSync、QA 属于 v2.0 扩展目标。

## 核心原则

- **协议优先**：Agent 间通信采用 A2A 1.0；工具调用采用 MCP 2025-11-25，包含 Streamable HTTP 和 Tasks 能力。
- **能力路由**：Agent 调用 `voice.generate`、`motion.generate` 等 capability，不直接绑定供应商模型名。
- **本地模型一等公民**：每类模型都可以通过本地 provider 接入，不把本地推理当成云端不可用时的临时降级。
- **可验证演进**：性能、成本和生产可用性均作为待验证 benchmark，而不是当前完成承诺。

## 两阶段路线

### MVP 原型

MVP 目标是用当前已有 Agent 跑通一条最短动画生产链路：

1. Director 将脚本拆成分镜。
2. Modeling 使用 sample Live2D 模型、Textoon local pipeline 或 mock provider 生成角色模型路径。
3. Voice 通过云端或本地 TTS provider 生成音频。
4. Animation 基于动作参数和口型输入生成镜头片段。
5. Renderer 使用本地 FFmpeg 组合最终视频。

MVP 必须允许没有云端 API key 的环境使用 mock/local provider 完成演示。

### v2.0 架构

v2.0 目标是把原型扩展为分布式智能体动画生产系统：

- A2A Registry 提供 Agent Card、能力发现、任务路由和版本协商。
- MCP Gateway 暴露 Live2D、Textoon、FFmpeg、TTS、STT、视觉生成、检索等工具。
- Writer、Artist、LipSync、QA Agent 补齐创作、角色设计、音素对齐和质量审查。
- Kubernetes + Istio 提供部署、弹性伸缩、流量治理和多租户隔离。
- Prometheus、Grafana、结构化日志和审计日志提供可观测性。

## 通用框架与专用模型

| 层级 | 职责 | 示例 |
| --- | --- | --- |
| 通用协议层 | Agent 通信、工具调用、任务状态、进度流 | A2A、MCP、Streamable HTTP、Tasks |
| 编排层 | 状态机、artifact 依赖、重试和缓存 | LangGraph、custom orchestrator、A2A task router |
| 模型路由层 | 按 capability、成本、隐私、延迟选择 provider | provider registry、capability routing |
| 专用工具层 | 实际生成和处理资产 | Live2D、Textoon、VTube/Live2D runtime、FFmpeg、TTS/STT、ComfyUI |

模型选择必须用“能力类别 + 当前基准候选”表达。例如，Director/Writer 需要长上下文、工具调用和结构化输出能力；Qwen3.7-Max 是云端基准候选，本地可接 Ollama、vLLM、LM Studio 或 llama.cpp server。

## Capability 名称

系统文档和配置统一使用以下 capability：

- `script.plan`
- `character.generate`
- `model.live2d.generate`
- `voice.generate`
- `speech.transcribe`
- `voice.convert`
- `lip_sync.align`
- `motion.generate`
- `video.compose`
- `video.edit`
- `quality.review`

## Provider Registry

Provider registry 描述每个模型或工具 provider 的能力、协议、本地/云端属性和回退关系。示例见 [config/provider_registry.example.json](config/provider_registry.example.json)。

固定字段：

| 字段 | 说明 |
| --- | --- |
| `provider_id` | provider 唯一标识 |
| `locality` | `cloud`、`local` 或 `hybrid` |
| `protocol` | `openai-compatible`、`ollama`、`mcp`、`comfyui`、`a2a` 或 `custom-rest` |
| `capabilities` | provider 支持的 capability 列表 |
| `endpoint` | API 或本地服务地址 |
| `models` | 可选模型列表 |
| `hardware_profile` | 运行所需或推荐硬件 |
| `priority` | 默认选择优先级，数字越小越优先 |
| `fallbacks` | 失败时可回退的 provider |
| `privacy_mode` | `remote`、`local-only` 或 `hybrid` |

## 本地模型兼容矩阵

| 能力类别 | 云端基准候选 | 本地/自托管接口 |
| --- | --- | --- |
| LLM / Agent | Qwen3.7-Max、Claude、GPT、Gemini | OpenAI-compatible endpoint、Ollama、vLLM、LM Studio、llama.cpp server |
| 图像/视频/角色 | Gemini Omni、专用图像/视频 API | ComfyUI local API、Diffusers worker、Textoon local pipeline |
| TTS / STT | Eleven v3、云端 STT/TTS | 本地 TTS、Whisper、whisper.cpp |
| Voice conversion | 云端 voice conversion API | RVC、SeedVC 类本地 provider |
| Embedding / Rerank | 云端 embedding/rerank API | 本地 embedding 服务、OpenAI-compatible embedding endpoint |
| Render / Compose | 托管媒体处理服务 | FFmpeg local、FFmpeg MCP server |

## 默认路由策略

- **Director/Writer**：优先选择长上下文、工具调用、中文能力强、结构化输出稳定的 LLM。
- **Artist/Video**：优先选择多模态生成与编辑 provider。
- **Modeling**：MVP 默认支持 sample model 或 Textoon local pipeline；云端 Textoon/API provider 可选。
- **Voice**：最终配音可使用高表现力 TTS；低延迟预览可使用本地或低延迟 provider。
- **Render**：MVP 使用 FFmpeg local；v2.0 可包装为 MCP 分布式服务。

## 快速开始

当前仓库仍处于原型阶段。推荐先查看部署指南中的 MVP 路径：

```bash
cp .env.example .env
docker compose config
```

如果要接入本地 LLM，可先启动任意 OpenAI-compatible endpoint，例如 Ollama、vLLM、LM Studio 或 llama.cpp server，然后在 provider registry 中把对应 provider 设为更高优先级。

## 文档

- [两阶段架构路线图](docs/architecture/two-stage-roadmap.md)
- [部署指南](deployment_guide.md)
- [Provider Registry 示例](config/provider_registry.example.json)

## 开源协作

本项目以 Apache-2.0 许可证开源，目标是让协议、provider registry、Agent 分工和本地/云端模型兼容设计可以被社区复用、验证和扩展。

- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [安全披露](SECURITY.md)
- [支持方式](SUPPORT.md)
- [变更记录](CHANGELOG.md)
- [许可证](LICENSE)

请不要提交 API key、模型权重、商业素材或未获授权的 Live2D 资产。仓库中的模型、服务和 endpoint 多为原型配置或占位示例，实际部署需要按各 provider 和第三方工具的许可证单独确认。

## 技术基准参考

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Agent2Agent Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [Live2D Cubism](https://www.live2d.com/en/cubism/update/)
- [Textoon](https://github.com/Human3DAIGC/Textoon)
- [ElevenLabs Models](https://elevenlabs.io/docs/overview/models)

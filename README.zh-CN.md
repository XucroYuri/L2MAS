# L2MAS：Live2D 多 Agent 动画生成系统

[English](README.md) | 简体中文 | [한국어](README.ko.md) | [Español](README.es.md) | [日本語](README.ja.md)

L2MAS 是面向 2026 协议生态的 Live2D 多 Agent 动画生成原型，目标是先跑通本地 MVP，再逐步演进到可生产部署的 v2.0 架构。

项目使用 A2A 连接创作 Agent，使用 MCP 2025-11-25 + Streamable HTTP + Tasks 暴露工具能力，并通过 provider registry 同时接入云端模型和本地运行模型。Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 等只作为能力基准，不是硬编码依赖。

## 当前状态

| 阶段 | 目标 | 状态 |
| --- | --- | --- |
| MVP 原型 | 本地跑通 `script -> storyboard -> model -> voice -> motion -> render` | 进行中 |
| v2.0 架构 | A2A 注册发现、MCP 工具集群、任务流式进度、Kubernetes、观测、安全、多租户 | 规划中 |

当前已有 Director、Modeling、Animation、Voice、Renderer 五个 Agent 骨架。Writer、Artist、LipSync、QA 属于 v2.0 目标。

## 核心原则

- 协议优先：A2A 用于 Agent 协作，MCP 用于工具和任务。
- 能力路由：Agent 调用 `voice.generate`、`motion.generate` 等 capability，不直接绑定模型名。
- 本地模型一等公民：Ollama、vLLM、LM Studio、llama.cpp、ComfyUI、Diffusers、Whisper、FFmpeg 等都可以通过 provider 接入。
- 两阶段演进：先 MVP，再 v2.0，不把目标指标写成已经完成的生产承诺。

## 快速开始

```bash
cp .env.example .env
docker compose config
```

更多细节见英文 canonical 文档：[README.md](README.md) 和 [deployment_guide.md](deployment_guide.md)。中文部署摘要见 [deployment_guide.zh-CN.md](deployment_guide.zh-CN.md)。

## 关键文档

- [两阶段架构路线图](docs/architecture/two-stage-roadmap.md)
- [Provider Registry 示例](config/provider_registry.example.json)
- [国际化维护策略](docs/i18n/README.md)
- [GitHub 发布清单](docs/github/repository-launch-checklist.md)

## 开源

本项目使用 [Apache-2.0](LICENSE) 许可证。请不要提交 API key、私有 endpoint、模型权重、商业素材或未获授权的 Live2D 资产。

本项目与 Live2D Inc. 无从属关系。Live2D、Cubism 及相关名称属于其各自权利人。

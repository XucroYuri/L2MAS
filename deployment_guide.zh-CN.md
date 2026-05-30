# 部署与演进指南

## L2MAS: Live2D Multi-Agent Animation System

L2MAS 是面向 2026 协议生态的 Live2D 多 Agent 动画生成原型。项目采用两阶段路线：先跑通本地 MVP，再逐步演进到可生产部署的 v2.0 架构。

本指南描述部署路线，不把当前仓库表述为已经生产可用。

## 1. 技术基线

| 类别 | 基线 |
| --- | --- |
| Agent 通信 | A2A 1.0 目标 |
| 工具协议 | MCP 2025-11-25 + Streamable HTTP + Tasks |
| 模型接入 | Provider registry + capability routing |
| 本地 LLM | OpenAI-compatible endpoint、Ollama、vLLM、LM Studio、llama.cpp server |
| 本地图像/视频 | ComfyUI local API、Diffusers worker、Textoon local pipeline |
| 本地语音 | 本地 TTS、Whisper/whisper.cpp、RVC/SeedVC 类 voice conversion |
| 渲染 | MVP 使用 FFmpeg local，v2.0 可包装为 FFmpeg MCP server |

Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 是能力基准，不是硬编码依赖。

## 2. MVP 部署路径

MVP 应允许没有云端 API key 的环境通过 mock 或本地 provider 跑通演示链路。

最低建议：

- Python 3.11+
- Docker 25+
- Docker Compose 2.20+
- FFmpeg
- 可选 GPU：用于 Textoon、ComfyUI、Diffusers、vLLM 等本地推理

配置环境变量：

```bash
cp .env.example .env
```

配置预检：

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
docker compose config
```

## 3. Provider Registry

Provider registry 是模型和工具的统一入口。Agent 只依赖 capability，例如 `script.plan`、`voice.generate`、`video.compose`，不直接依赖固定厂商或模型。

示例：

```json
{
  "provider_id": "local-ollama-agent",
  "locality": "local",
  "protocol": "ollama",
  "capabilities": ["script.plan", "quality.review"],
  "endpoint": "http://localhost:11434",
  "models": ["qwen3.7:latest", "llama3.3:latest"],
  "hardware_profile": "developer workstation",
  "priority": 20,
  "fallbacks": ["cloud-qwen-agent"],
  "privacy_mode": "local-only"
}
```

完整示例见 [config/provider_registry.example.json](config/provider_registry.example.json)。

## 4. MVP 完成标准

MVP 完成标准是链路可验证，而不是性能数字：

1. 输入短脚本和角色描述。
2. Director 输出结构化 storyboard。
3. Modeling 返回 sample 或生成模型路径。
4. Voice 返回音频路径或 mock 音频 artifact。
5. Animation 返回镜头片段或 mock video artifact。
6. Renderer 使用 FFmpeg local 或 mock composer 返回 final video artifact。
7. 全流程在没有云端 key 时也能通过 mock/local provider 运行。

## 5. v2.0 演进

v2.0 在 MVP 之上增加：

- A2A Agent Card、发现、任务路由和版本协商。
- MCP 2025-11-25 工具服务，支持 Tasks 和 Streamable HTTP。
- task id、进度事件、artifact schema、重试和恢复。
- Kubernetes、服务网格、对象存储和 provider registry 服务化。
- Prometheus、Grafana、结构化日志和审计日志。
- 每请求鉴权、privacy mode、多租户隔离和密钥管理。

## 6. 相关文档

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md)
- [docs/github/repository-launch-checklist.md](docs/github/repository-launch-checklist.md)

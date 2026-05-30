# 部署与演进指南

## Live2D Multi-Agent Animation System

面向 2026 协议生态的 Live2D 多 Agent 动画生成原型，目标是逐步达到生产可部署。

本指南分成两个阶段：

1. **MVP 原型部署**：本地或单机 Docker 环境，优先跑通端到端链路。
2. **v2.0 生产演进**：A2A 注册发现、MCP 工具集群、Kubernetes、观测、安全、多租户和多 provider 路由。

## 1. 技术基线

| 类别 | 基线 |
| --- | --- |
| Agent 通信 | A2A 1.0 |
| 工具协议 | MCP 2025-11-25 + Streamable HTTP + Tasks |
| 模型接入 | Provider registry + capability routing |
| 本地 LLM | OpenAI-compatible endpoint、Ollama、vLLM、LM Studio、llama.cpp server |
| 本地图像/视频 | ComfyUI local API、Diffusers worker、Textoon local pipeline |
| 本地语音 | 本地 TTS、Whisper/whisper.cpp、RVC/SeedVC 类 voice conversion |
| 渲染 | FFmpeg local，后续可包装为 FFmpeg MCP server |

Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 是能力基准，不是硬编码依赖。

## 2. 项目现状

当前源码包含：

```text
agents/
  director/    # 分镜与编排骨架
  modeling/    # Live2D/Textoon 建模骨架
  animation/   # 动作与表情参数生成骨架
  voice/       # TTS 配音骨架
  renderer/    # FFmpeg 合成骨架
config/
  a2a_config.json
  mcp_config.json
  provider_registry.example.json
```

v2.0 目标中的 Writer、Artist、LipSync、QA Agent 尚未落地，应在后续迭代补齐。

## 3. MVP 原型部署

### 3.1 环境要求

MVP 可以使用 mock provider 或本地 provider，不要求一开始具备全部云端 API key。

最低建议：

- Python 3.11+
- Docker 25+
- Docker Compose 2.20+
- FFmpeg
- 可选 GPU：用于 Textoon、ComfyUI、Diffusers、vLLM 等本地推理

### 3.2 配置环境变量

```bash
cp .env.example .env
```

MVP 推荐先保留云端 key 为空，使用本地或 mock provider 跑通流程。需要真实云端能力时再配置：

```bash
QWEN_API_KEY=your_qwen_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

MCP 版本字段应使用日期版本：

```bash
MCP_VERSION=2025-11-25
MCP_TRANSPORT=streamable-http
```

### 3.3 配置 provider registry

Provider registry 是模型和工具的统一入口。示例：

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

每个 provider 必须声明：

- `provider_id`
- `locality`: `cloud | local | hybrid`
- `protocol`: `openai-compatible | ollama | mcp | comfyui | a2a | custom-rest`
- `capabilities`
- `endpoint`
- `models`
- `hardware_profile`
- `priority`
- `fallbacks`
- `privacy_mode`

完整示例见 [config/provider_registry.example.json](config/provider_registry.example.json)。

### 3.4 本地模型接入

#### LLM / Agent

可选入口：

- Ollama: `http://localhost:11434`
- vLLM OpenAI-compatible server
- LM Studio local server
- llama.cpp server
- 任意 OpenAI-compatible endpoint

Director/Writer 类 Agent 只依赖 `script.plan` 和 `quality.review` 等 capability，不关心底层模型来自云端还是本地。

#### 图像、视频与角色生成

可选入口：

- ComfyUI local API
- Diffusers worker
- Textoon local pipeline
- 云端图像/视频生成 API

Artist/Modeling 类能力通过 `character.generate`、`model.live2d.generate`、`video.edit` 暴露。

#### 语音与口型

可选入口：

- Eleven v3 或其他云端 TTS
- 本地 TTS
- Whisper/whisper.cpp
- RVC/SeedVC 类 voice conversion

Voice/LipSync 类能力通过 `voice.generate`、`speech.transcribe`、`voice.convert`、`lip_sync.align` 暴露。

### 3.5 Docker 配置预检

```bash
docker compose config
```

此命令只验证 Compose 配置能否展开。当前仓库仍需要补齐真实 MCP server 镜像、mock provider、SDK 包装和监控配置后，才能宣称完整启动成功。

## 4. MVP 验证目标

MVP 的完成标准不是性能数字，而是链路可验证：

1. 输入短脚本和角色描述。
2. Director 输出结构化 storyboard。
3. Modeling 返回可用的 sample 或生成模型路径。
4. Voice 返回音频路径或 mock 音频 artifact。
5. Animation 返回镜头片段路径或 mock video artifact。
6. Renderer 使用 FFmpeg 或 mock composer 返回 final video artifact。
7. 全流程在没有云端 key 时也能通过 mock/local provider 运行。

## 5. v2.0 生产演进

v2.0 在 MVP 之上增加分布式和生产能力。

### 5.1 Agent 层

目标 Agent：

| Agent | Capability |
| --- | --- |
| Director | `script.plan`、任务编排、质量门禁 |
| Writer | 剧本扩写、台词、情绪标签 |
| Artist | `character.generate`、风格设定、角色一致性 |
| Modeling | `model.live2d.generate` |
| Voice | `voice.generate`、`voice.convert` |
| LipSync | `speech.transcribe`、`lip_sync.align` |
| Animation | `motion.generate` |
| Renderer | `video.compose`、`video.edit` |
| QA | `quality.review` |

### 5.2 协议层

- A2A 1.0 用于 Agent Card、能力发现、任务路由、版本协商和跨 Agent 通信。
- MCP 2025-11-25 用于工具、资源、任务状态和 Streamable HTTP。
- 所有长任务必须有 task id、状态、进度、错误信息和 artifact 输出。

### 5.3 部署层

生产部署目标：

- Kubernetes 管理 Agent、MCP server 和 worker。
- Istio 或同类服务网格处理流量治理、mTLS 和重试。
- 对象存储保存模型、音频、镜头片段和最终视频。
- Provider registry 由配置中心或数据库管理。

### 5.4 可观测与安全

生产目标：

- Prometheus/Grafana 采集任务数量、耗时、失败率、provider 命中率、成本估算。
- 结构化日志记录 task id、agent id、provider id、artifact id。
- 审计日志记录跨 Agent 调用和高风险工具调用。
- 支持 `local-only` privacy mode，确保敏感素材不离开本地或私有集群。

## 6. Benchmark 策略

文档中的性能数据必须以“目标指标”或“待验证指标”呈现。建议验证：

| 指标 | MVP 验证 | v2.0 验证 |
| --- | --- | --- |
| 端到端成功率 | 单机短脚本 10 次运行 | 多 Agent 并发任务 |
| 生成耗时 | 分镜、配音、渲染分段计时 | provider 路由和集群吞吐 |
| 成本 | 云端 token 和语音调用估算 | 每分钟视频成本 |
| 本地可用性 | 无云端 key 可跑通 mock/local 链路 | local-only 隐私模式 |
| 质量 | 人工审查分镜、口型、动作一致性 | QA Agent + 人工抽检 |

## 7. 故障排查方向

- 如果云端 key 缺失，确认 provider registry 中存在可用 local 或 mock provider。
- 如果本地 LLM 无响应，检查 OpenAI-compatible endpoint、Ollama、vLLM、LM Studio 或 llama.cpp server 是否启动。
- 如果 ComfyUI/Textoon 任务失败，检查 workflow、模型权重、GPU 内存和路径挂载。
- 如果 A2A 注册失败，检查 Agent Card、协议版本和 registry endpoint。
- 如果 MCP 工具不可见，检查 MCP server 的工具列表、协议版本和 Streamable HTTP 连接。

## 8. 参考文档

- [两阶段架构路线图](docs/architecture/two-stage-roadmap.md)
- [Provider Registry 示例](config/provider_registry.example.json)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Agent2Agent Protocol Specification](https://a2a-protocol.org/latest/specification/)


# Two-Stage Roadmap: Live2D Multi-Agent Animation Prototype

## 1. Positioning

This project is a Live2D multi-agent animation generation prototype for the 2026 protocol ecosystem. The goal is to move from a local, verifiable MVP to a production-deployable v2.0 architecture.

The system must not hard-code a single model vendor. Cloud models and local models are both first-class providers. Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon, and Live2D Cubism 5.3 are treated as capability benchmarks, not as required dependencies.

## 2. Architecture Layers

| Layer | Responsibility | Examples |
| --- | --- | --- |
| Agent protocol | Agent discovery, cards, tasks, version negotiation | A2A 1.0 |
| Tool protocol | Tools, resources, long tasks, streaming transport | MCP 2025-11-25, Streamable HTTP, Tasks |
| Orchestration | Artifact graph, retries, caching, progress | LangGraph or custom orchestrator |
| Provider routing | Select models/tools by capability, locality, cost, privacy | Provider registry |
| Media tools | Generate, animate, sync, compose assets | Live2D, Textoon, ComfyUI, FFmpeg, TTS/STT |

## 3. Capability Contract

Agents and tools communicate through capabilities:

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

Agents must request capabilities, not model names. Routing chooses the provider.

## 4. Provider Registry Contract

Every provider entry uses the same fields:

| Field | Required | Description |
| --- | --- | --- |
| `provider_id` | yes | Unique provider id |
| `locality` | yes | `cloud`, `local`, or `hybrid` |
| `protocol` | yes | `openai-compatible`, `ollama`, `mcp`, `comfyui`, `a2a`, or `custom-rest` |
| `capabilities` | yes | Capability names exposed by this provider |
| `endpoint` | yes | HTTP, local, or cluster endpoint |
| `models` | yes | Model ids or workflow ids |
| `hardware_profile` | yes | Required or expected runtime profile |
| `priority` | yes | Lower number is preferred |
| `fallbacks` | yes | Provider ids to try next |
| `privacy_mode` | yes | `remote`, `local-only`, or `hybrid` |

Routing defaults:

1. Filter providers by requested capability.
2. Filter by privacy mode. `local-only` tasks may not call remote providers.
3. Sort by priority.
4. Use fallback providers if the selected provider fails or times out.

## 5. MVP Stage

MVP objective: run a short animation pipeline locally or in Docker with cloud, local, or mock providers.

Required flow:

1. `script.plan`: Director converts a script into storyboard shots.
2. `model.live2d.generate`: Modeling returns a sample model path, Textoon output, or mock model artifact.
3. `voice.generate`: Voice returns audio artifacts from cloud TTS, local TTS, or mock audio.
4. `motion.generate`: Animation returns shot video artifacts or mock shot artifacts.
5. `video.compose`: Renderer returns a final video artifact using FFmpeg local or mock compose.

MVP acceptance:

- The full flow can run without cloud API keys.
- Every step emits a task id, status, and artifact path.
- Provider selection is visible in logs or structured output.
- The README and deployment guide do not claim production readiness.

## 6. v2.0 Stage

v2.0 objective: evolve the MVP into a distributed multi-agent production architecture.

Add these agents:

| Agent | Capability focus |
| --- | --- |
| Writer | Script expansion, dialogue, emotion tags |
| Artist | Character generation and style consistency |
| LipSync | Speech transcription and viseme alignment |
| QA | Visual/audio/story quality review |

Add these platform capabilities:

- A2A Registry for Agent Card discovery and task routing.
- MCP Gateway for Live2D, Textoon, ComfyUI, FFmpeg, TTS/STT, retrieval, and QA tools.
- Kubernetes deployments for agents, tool servers, and workers.
- Object storage for model, audio, shot, and final video artifacts.
- Observability for task latency, provider hit rate, failure rate, cost, and artifact lineage.
- Zero-trust controls for authentication, authorization, audit logs, and `local-only` privacy.

## 7. Local Provider Compatibility

Local providers are not fallback-only. They are supported as normal production choices when privacy, cost, or offline operation requires them.

| Capability group | Local provider examples | Protocol preference |
| --- | --- | --- |
| LLM / Agent | Ollama, vLLM, LM Studio, llama.cpp server | OpenAI-compatible or Ollama |
| Image / Video | ComfyUI, Diffusers worker | ComfyUI API or custom REST |
| Live2D model | Textoon local pipeline | MCP or custom REST |
| TTS / STT | Local TTS, Whisper, whisper.cpp | custom REST or MCP |
| Voice conversion | RVC, SeedVC-like workers | custom REST or MCP |
| Render | FFmpeg local | local process or MCP |
| Embedding / Rerank | Local embedding service | OpenAI-compatible or custom REST |

## 8. Benchmark Policy

All performance numbers are targets until measured in this repository.

Benchmark reports must include:

- Hardware profile.
- Provider id and model/workflow id.
- Input duration and shot count.
- Per-stage latency.
- Total cost estimate for cloud providers.
- Whether privacy mode was `remote`, `local-only`, or `hybrid`.

## 9. Implementation Notes

- Keep the MVP path simple and testable.
- Prefer mock providers before integrating expensive or unstable services.
- Do not require Kubernetes for MVP.
- Do not require cloud API keys for smoke tests.
- Do not add a new model-specific code path when capability routing can cover the need.


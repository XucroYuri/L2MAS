# Deployment and Evolution Guide

## L2MAS: Live2D Multi-Agent Animation System

L2MAS is a protocol-first Live2D multi-agent animation prototype for the 2026 agent ecosystem. The goal is to move in two stages: first a local MVP, then a v2.0 architecture that can become production-deployable.

This guide is intentionally written as a deployment roadmap, not as a claim that the current repository is production-ready.

## 1. Technical Baseline

| Area | Baseline |
| --- | --- |
| Agent communication | A2A 1.0 target |
| Tool protocol | MCP 2025-11-25 + Streamable HTTP + Tasks |
| Model access | Provider registry + capability routing |
| Local LLM | OpenAI-compatible endpoint, Ollama, vLLM, LM Studio, llama.cpp server |
| Local image/video | ComfyUI local API, Diffusers worker, Textoon local pipeline |
| Local speech | local TTS, Whisper/whisper.cpp, RVC-like and SeedVC-like voice conversion |
| Rendering | FFmpeg local for MVP; FFmpeg MCP server for v2.0 |

Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon, and Live2D Cubism 5.3 are capability baselines, not hard-coded dependencies.

## 2. Current Repository Shape

```text
agents/
  director/    # storyboard and orchestration skeleton
  modeling/    # Live2D/Textoon modeling skeleton
  animation/   # motion and expression parameter skeleton
  voice/       # TTS voice skeleton
  renderer/    # FFmpeg composition skeleton
config/
  a2a_config.json
  mcp_config.json
  provider_registry.example.json
```

Writer, Artist, LipSync, and QA agents are v2.0 targets.

## 3. MVP Deployment Path

### 3.1 Requirements

The MVP should be able to run with mock or local providers. Cloud API keys should improve quality, not be required for a first demonstration.

Minimum recommended environment:

- Python 3.11+
- Docker 25+
- Docker Compose 2.20+
- FFmpeg
- optional GPU for Textoon, ComfyUI, Diffusers, vLLM, or similar local inference

### 3.2 Configure Environment Variables

```bash
cp .env.example .env
```

Keep cloud keys empty for a mock/local first run. Add real keys only when testing cloud providers:

```bash
QWEN_API_KEY=your_qwen_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

MCP should use the date-versioned spec field:

```bash
MCP_VERSION=2025-11-25
MCP_TRANSPORT=streamable-http
```

### 3.3 Configure Provider Registry

Provider registry is the unified entry point for models and tools:

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

Full example: [config/provider_registry.example.json](config/provider_registry.example.json).

### 3.4 Local Provider Compatibility

| Capability family | Local options |
| --- | --- |
| LLM / Agent | Ollama, vLLM, LM Studio, llama.cpp server, OpenAI-compatible endpoints |
| Image / video / character | ComfyUI local API, Diffusers worker, Textoon local pipeline |
| Speech | local TTS, Whisper, whisper.cpp |
| Voice conversion | RVC-like and SeedVC-like providers |
| Render | FFmpeg local |

Agents depend on capability names such as `script.plan`, `voice.generate`, and `video.compose`; they should not depend on a fixed vendor model.

### 3.5 Preflight

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
docker compose config
```

This validates configuration shape. The repository now includes a deterministic mock MVP path for smoke tests, but still needs real MCP server implementations, SDK wrappers, and provider adapters before claiming full startup success.

### 3.6 Local mock smoke test

```bash
python3 -m unittest discover -s tests -v
python3 examples/test_end_to_end.py
```

The smoke path writes placeholder artifacts under `output/mvp/` and does not require cloud API keys.

## 4. MVP Completion Criteria

The MVP is complete when the following flow is reproducible without cloud keys:

1. Input a short script and character description.
2. Director returns structured storyboard data.
3. Modeling returns a sample or generated model artifact path.
4. Voice returns an audio artifact path or mock audio artifact.
5. Animation returns shot clips or mock video artifacts.
6. Renderer returns a final video artifact through FFmpeg local or a mock composer.
7. The run emits task status, artifact paths, and recoverable error messages.

## 5. v2.0 Evolution

v2.0 adds distributed and production-oriented capabilities on top of the MVP:

| Layer | Direction |
| --- | --- |
| Agent | A2A Agent Cards, discovery, task routing, and version negotiation |
| Tooling | MCP 2025-11-25 tool servers with Tasks and Streamable HTTP |
| State | task IDs, progress events, artifact schemas, retries, and resumability |
| Deployment | Kubernetes, service mesh, object storage, provider registry service |
| Observability | Prometheus, Grafana, structured logs, audit logs |
| Security | per-request auth, privacy modes, tenant isolation, secret management |

## 6. Benchmark Strategy

Performance numbers should be written as target metrics or benchmark results with date, hardware, provider, model, and input details.

Recommended benchmark dimensions:

| Metric | MVP validation | v2.0 validation |
| --- | --- | --- |
| End-to-end success | 10 short-script local runs | concurrent distributed tasks |
| Latency | local mock and FFmpeg baseline | provider-specific routing comparison |
| Cost | cloud calls disabled by default | provider cost reports |
| Quality | human review checklist | QA agent plus human review |
| Privacy | local-only provider path | tenant and audit validation |

## 7. Related Docs

- [README.md](README.md)
- [README.zh-CN.md](README.zh-CN.md)
- [docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md)
- [docs/github/repository-launch-checklist.md](docs/github/repository-launch-checklist.md)

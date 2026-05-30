# L2MAS: Live2D Multi-Agent Animation System

[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-2025--11--25-orange.svg)](https://modelcontextprotocol.io)
[![A2A](https://img.shields.io/badge/A2A-1.0-purple.svg)](https://a2a-protocol.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Protocol-first Live2D multi-agent animation prototype for the 2026 agent ecosystem.

L2MAS explores how creative agents can plan, generate, voice, animate, review, and render Live2D animation through interoperable protocols. It uses A2A for agent collaboration, MCP 2025-11-25 + Streamable HTTP + Tasks for tool access, and a provider registry so cloud models and local models are first-class peers.

Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon, and Live2D Cubism 5.3 are treated as 2026 capability baselines, not hard-coded dependencies.

## Languages

English is the canonical documentation entry. Localized READMEs are limited to the top language set for Live2D technical development and community distribution: English, Japanese, Simplified Chinese, Korean, and Spanish.

| Language | README |
| --- | --- |
| English | [README.md](README.md) |
| 日本語 | [README.ja.md](README.ja.md) |
| 简体中文 | [README.zh-CN.md](README.zh-CN.md) |
| 한국어 | [README.ko.md](README.ko.md) |
| Español | [README.es.md](README.es.md) |

Translation policy: [docs/i18n/README.md](docs/i18n/README.md).

## Project Status

L2MAS is an early open-source prototype. The repository is designed around a two-stage roadmap:

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run a local end-to-end path: `script -> storyboard -> model -> voice -> motion -> render` | In progress |
| v2.0 architecture | Evolve into distributed A2A agents, MCP tool clusters, streaming task progress, Kubernetes, observability, security, and multi-tenant provider routing | Planned |

Current agent skeletons:

| Agent | MVP role | v2.0 direction |
| --- | --- | --- |
| Director | Storyboard planning and orchestration | Cross-agent task routing and quality gates |
| Modeling | Sample model, Textoon local pipeline, or mock Live2D model path | Text/image-to-Live2D provider routing |
| Voice | Cloud/local TTS or mock audio artifact | Emotional TTS, voice conversion, STT integration |
| Animation | Motion and expression parameter planning | Motion generation, lip-sync aware shot animation |
| Renderer | FFmpeg local composition | Distributed MCP render service |

Planned v2.0 agents include Writer, Artist, LipSync, and QA.

## Why This Exists

Most AI animation experiments bind directly to one model, one tool API, or one workflow graph. L2MAS instead separates the system into:

- **Generic protocol layer**: A2A, MCP, task state, artifact schema, provider registry, and capability routing.
- **Specialized creative layer**: Live2D, Textoon, VTube/Live2D runtime, FFmpeg, TTS/STT, video generation, and video editing providers.
- **Cloud/local parity**: local providers are not a fallback afterthought; they are a supported deployment mode for privacy, cost control, offline work, and experimentation.

Agents call capabilities such as `voice.generate` or `motion.generate`. They do not call a fixed vendor model directly.

## Architecture

```mermaid
flowchart TB
    user["User / App / API"] --> director["Director Agent"]
    director --> writer["Writer Agent v2.0"]
    director --> artist["Artist Agent v2.0"]
    director --> modeling["Modeling Agent"]
    director --> voice["Voice Agent"]
    director --> animation["Animation Agent"]
    director --> renderer["Renderer Agent"]
    voice --> lipsync["LipSync Agent v2.0"]
    animation --> qa["QA Agent v2.0"]

    subgraph protocol["Protocol and Routing Layer"]
        a2a["A2A Agent Cards and Tasks"]
        mcp["MCP 2025-11-25 Streamable HTTP and Tasks"]
        registry["Provider Registry"]
        artifacts["Artifact Schema"]
    end

    director --> protocol
    modeling --> protocol
    voice --> protocol
    animation --> protocol
    renderer --> protocol

    subgraph providers["Cloud, Local, and Hybrid Providers"]
        llm["LLM / Agent Providers"]
        visual["Image, Video, Character Providers"]
        live2d["Live2D / Textoon Tooling"]
        speech["TTS / STT / Voice Conversion"]
        ffmpeg["FFmpeg Render Pipeline"]
    end

    protocol --> providers
```

## Capability Surface

The project standardizes on capability names that can be routed to cloud, local, or hybrid providers:

| Capability | Purpose |
| --- | --- |
| `script.plan` | script planning, storyboard structure, shot metadata |
| `character.generate` | character concepts, visual references, style exploration |
| `model.live2d.generate` | Live2D model generation or model artifact selection |
| `voice.generate` | dialogue voice generation |
| `speech.transcribe` | speech-to-text or phoneme preparation |
| `voice.convert` | voice conversion or cloning workflows |
| `lip_sync.align` | phoneme, viseme, and mouth-shape alignment |
| `motion.generate` | expression, pose, parameter, and motion sequencing |
| `video.compose` | scene composition and final render |
| `video.edit` | post-generation video editing |
| `quality.review` | script, motion, audio, render, and policy review |

## Provider Registry

Provider registry is the central contract for model and tool routing. Example: [config/provider_registry.example.json](config/provider_registry.example.json).

Required fields:

| Field | Meaning |
| --- | --- |
| `provider_id` | stable provider identifier |
| `locality` | `cloud`, `local`, or `hybrid` |
| `protocol` | `openai-compatible`, `ollama`, `mcp`, `comfyui`, `a2a`, or `custom-rest` |
| `capabilities` | supported capability names |
| `endpoint` | cloud API, local service URL, or MCP/A2A endpoint |
| `models` | available model identifiers or workflow names |
| `hardware_profile` | expected hardware or runtime profile |
| `priority` | routing priority; lower is preferred |
| `fallbacks` | ordered fallback provider IDs |
| `privacy_mode` | `remote`, `local-only`, or `hybrid` |

## Local Model Support

L2MAS treats local inference and local media pipelines as first-class runtime targets.

| Category | Cloud baseline examples | Local/self-hosted compatibility |
| --- | --- | --- |
| LLM / Agent | Qwen3.7-Max, Claude, GPT, Gemini | OpenAI-compatible endpoint, Ollama, vLLM, LM Studio, llama.cpp server |
| Image / video / character | Gemini Omni, specialized image/video APIs | ComfyUI local API, Diffusers worker, Textoon local pipeline |
| TTS / STT | Eleven v3, cloud STT/TTS APIs | local TTS, Whisper, whisper.cpp |
| Voice conversion | cloud voice conversion APIs | RVC-like and SeedVC-like providers |
| Embedding / rerank | cloud embedding/rerank APIs | local embedding services, OpenAI-compatible embedding endpoints |
| Render / compose | hosted media processing | FFmpeg local, FFmpeg MCP server |

## Quick Start

Validate the current prototype configuration:

```bash
cp .env.example .env
docker compose config
```

Validate JSON configuration:

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
```

Use a local LLM by starting any compatible endpoint, then prioritizing that provider in the registry:

- Ollama: `http://localhost:11434`
- vLLM OpenAI-compatible server
- LM Studio local server
- llama.cpp server
- Any OpenAI-compatible endpoint

The MVP path must remain runnable with mock or local providers when cloud API keys are absent.

## Documentation

| Document | Purpose |
| --- | --- |
| [docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md) | MVP to v2.0 architecture roadmap |
| [deployment_guide.md](deployment_guide.md) | English deployment and evolution guide |
| [deployment_guide.zh-CN.md](deployment_guide.zh-CN.md) | Simplified Chinese deployment guide |
| [config/provider_registry.example.json](config/provider_registry.example.json) | provider registry reference example |
| [docs/i18n/README.md](docs/i18n/README.md) | localization policy |
| [docs/github/repository-launch-checklist.md](docs/github/repository-launch-checklist.md) | GitHub publishing checklist and metadata |

## Open Source

L2MAS is licensed under Apache-2.0.

| Community file | Purpose |
| --- | --- |
| [CONTRIBUTING.md](CONTRIBUTING.md) | contribution workflow and validation |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | community behavior expectations |
| [SECURITY.md](SECURITY.md) | private vulnerability reporting |
| [SUPPORT.md](SUPPORT.md) | support channels and issue guidance |
| [CHANGELOG.md](CHANGELOG.md) | notable changes |
| [GOVERNANCE.md](GOVERNANCE.md) | maintainer-led governance |
| [CITATION.cff](CITATION.cff) | citation metadata for GitHub |

Do not commit API keys, private endpoints, proprietary model weights, commercial media, or unauthorized Live2D assets.

This project is not affiliated with Live2D Inc. Live2D, Cubism, and related names are trademarks or registered trademarks of their respective owners.

## GitHub Discovery

Suggested repository description:

> Protocol-first Live2D multi-agent animation prototype with MCP, A2A, provider routing, and cloud/local model support.

Suggested topics:

`live2d`, `multi-agent`, `mcp`, `a2a`, `ai-agents`, `animation`, `generative-ai`, `provider-registry`, `local-ai`, `ollama`, `vllm`, `comfyui`, `diffusers`, `ffmpeg`, `text-to-animation`, `vtuber`, `tts`, `lip-sync`, `python`, `docker`

More launch details: [docs/github/repository-launch-checklist.md](docs/github/repository-launch-checklist.md).

## Keywords

Live2D animation generation, multi-agent AI, AI agents, MCP, Model Context Protocol, A2A, Agent2Agent, provider registry, capability routing, local AI, Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, FFmpeg, Textoon, TTS, STT, lip sync, VTuber automation, cloud local hybrid AI.

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Agent2Agent Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [GitHub repository topics](https://docs.github.com/en/github/administering-a-repository/classifying-your-repository-with-topics)
- [GitHub community profiles](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories)
- [GitHub citation files](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Live2D Cubism](https://www.live2d.com/en/cubism/update/)
- [Textoon](https://github.com/Human3DAIGC/Textoon)
- [ElevenLabs Models](https://elevenlabs.io/docs/overview/models)

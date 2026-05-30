# GitHub Discovery Profile

This profile keeps the public repository presentation aligned with the project's positioning: a protocol-first Live2D multi-agent animation prototype that can grow from a local MVP into a production-deployable v2.0 architecture.

## Repository About

| Field | Value |
| --- | --- |
| Name | `L2MAS` |
| Full name | `Live2D Multi-Agent Animation System` |
| Description | `Live2D multi-agent animation prototype with MCP, A2A, provider routing, local AI, ComfyUI/Ollama/vLLM, and FFmpeg.` |
| Homepage | `https://github.com/XucroYuri/L2MAS/releases/latest` |
| License | `Apache-2.0` |
| Default branch | `main` |
| Discussions | Enabled; welcome thread: [#11](https://github.com/XucroYuri/L2MAS/discussions/11) |
| Wiki | Disabled; canonical documentation stays in Git. |

## Topics

Use all 20 GitHub topic slots for a mix of domain, protocol, model-runtime, and implementation keywords:

```text
live2d
vtuber
animation-generation
text-to-animation
generative-ai
ai-agents
multi-agent
mcp
model-context-protocol
a2a
agent-to-agent
provider-registry
local-ai
openai-compatible
ollama
vllm
comfyui
diffusers
ffmpeg
python
```

## First-Impression Funnel

| Visitor intent | Repository surface |
| --- | --- |
| "What is this?" | README title, badges, one-line positioning, and At a Glance table |
| "Can I run it?" | Quick Start and MVP smoke test commands |
| "Is it model-locked?" | Provider Registry and Local Model Support sections |
| "Is it real or aspirational?" | Project Status, release notes, and Known Gaps |
| "Can I contribute?" | CONTRIBUTING, issue templates, labels, starter issues, and Discussions |

## Labels

Use labels to make the issue list searchable and welcoming:

| Label | Purpose |
| --- | --- |
| `triage` | New issue awaiting maintainer classification |
| `area:provider-registry` | Capability routing, registry schema, provider selection |
| `area:local-ai` | Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, local TTS/STT |
| `area:live2d` | Live2D, Cubism, Textoon, runtime, asset, or render integration |
| `area:docs` | README, examples, guides, launch material |
| `protocol:mcp` | Model Context Protocol work |
| `protocol:a2a` | Agent-to-agent collaboration work |
| `mvp` | Current local prototype scope |
| `v2-roadmap` | Production architecture direction |

## Starter Issues

Open a small set of public issues to show the contribution path without implying production readiness:

1. [Provider adapter: OpenAI-compatible and Ollama local LLM routing](https://github.com/XucroYuri/L2MAS/issues/8)
2. [Provider adapter: ComfyUI character and storyboard visual workflow](https://github.com/XucroYuri/L2MAS/issues/9)
3. [Live2D runtime spike: Cubism render adapter contract](https://github.com/XucroYuri/L2MAS/issues/10)

Each issue should state current status, target capability names, acceptance criteria, and validation commands.

## Social Preview

Use [docs/assets/social-preview.svg](../assets/social-preview.svg) as the source artwork for a GitHub social preview image. GitHub repository social preview images are configured from repository settings, so this file is kept in Git as the canonical design asset.

Recommended export size: 1280 x 640 px.

## Maintenance Loop

- Revisit topics when the first real provider adapters land.
- Keep the README At a Glance table honest; do not claim production readiness before verified adapters exist.
- Close or refresh stale starter issues after each release.
- Mention visible demos or screenshots in release notes once real Live2D rendering is integrated.

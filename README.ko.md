# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | 한국어 | [Español](README.es.md)

L2MAS는 2026년 에이전트 프로토콜 생태계를 목표로 하는 Live2D 멀티 에이전트 애니메이션 생성 프로토타입입니다. 먼저 로컬 MVP를 완성하고, 이후 배포 가능한 v2.0 분산 아키텍처로 발전시키는 것을 목표로 합니다.

A2A는 에이전트 협업에 사용하고, MCP 2025-11-25 + Streamable HTTP + Tasks는 도구 접근에 사용합니다. provider registry는 클라우드 모델과 로컬 모델을 동일한 라우팅 계층에서 다룹니다.

## 상태

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## 설계 원칙

- 에이전트는 고정 모델명이 아니라 `voice.generate`, `motion.generate` 같은 capability를 호출합니다.
- Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper, FFmpeg 같은 로컬 provider를 일급 대상으로 봅니다.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon, Live2D Cubism 5.3은 능력 기준선이며 하드 의존성이 아닙니다.

## 빠른 시작

```bash
cp .env.example .env
docker compose config
```

Canonical documentation: [README.md](README.md). Localization policy: [docs/i18n/README.md](docs/i18n/README.md).

## 라이선스

L2MAS는 [Apache-2.0](LICENSE) 라이선스로 배포됩니다. API key, private endpoint, model weights, 상업용 미디어, 승인되지 않은 Live2D assets를 커밋하지 마세요.

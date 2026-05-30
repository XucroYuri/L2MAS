# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português](README.pt-BR.md) | Русский

L2MAS - это прототип мультиагентной генерации Live2D-анимации, построенный вокруг протоколов для экосистемы агентов 2026 года. Дорожная карта начинается с локального MVP и затем развивается к архитектуре v2.0, пригодной для производственного развертывания.

Проект использует A2A для взаимодействия агентов, MCP 2025-11-25 + Streamable HTTP + Tasks для доступа к инструментам и provider registry для единой маршрутизации облачных и локальных моделей.

## Status

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## Принципы

- Агенты вызывают capabilities вроде `voice.generate` и `motion.generate`, а не жестко заданные имена моделей.
- Локальные providers, включая Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper и FFmpeg, являются полноценными целями.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon и Live2D Cubism 5.3 - это ориентиры возможностей, а не обязательные зависимости.

## Быстрый старт

```bash
cp .env.example .env
docker compose config
```

Каноническая документация: [README.md](README.md). Политика локализации: [docs/i18n/README.md](docs/i18n/README.md).

## Лицензия

L2MAS распространяется под лицензией [Apache-2.0](LICENSE). Не добавляйте в репозиторий API keys, приватные endpoints, веса моделей, коммерческие медиа или неавторизованные Live2D assets.

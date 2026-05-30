# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md) | Español | [日本語](README.ja.md)

L2MAS es un prototipo de generacion de animacion Live2D multiagente y orientado a protocolos para el ecosistema de agentes de 2026. La hoja de ruta empieza con un MVP local y evoluciona hacia una arquitectura v2.0 desplegable en produccion.

Usa A2A para la colaboracion entre agentes, MCP 2025-11-25 + Streamable HTTP + Tasks para el acceso a herramientas, y un provider registry para tratar modelos en la nube y modelos locales como opciones de primera clase.

## Estado

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## Principios

- Los agentes llaman capabilities como `voice.generate` y `motion.generate`, no nombres fijos de modelos.
- Providers locales como Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper y FFmpeg son objetivos de primera clase.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon y Live2D Cubism 5.3 son referencias de capacidad, no dependencias obligatorias.

## Inicio rapido

```bash
cp .env.example .env
docker compose config
```

Documentacion canonica: [README.md](README.md). Politica de localizacion: [docs/i18n/README.md](docs/i18n/README.md).

## Licencia

L2MAS se publica bajo [Apache-2.0](LICENSE). No subas API keys, endpoints privados, pesos de modelos, material comercial ni assets Live2D no autorizados.

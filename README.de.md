# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | Deutsch | [Português](README.pt-BR.md) | [Русский](README.ru.md)

L2MAS ist ein protokollorientierter Live2D-Multi-Agent-Prototyp fuer Animationsgenerierung im Agenten-Oekosystem 2026. Die Roadmap beginnt mit einem lokalen MVP und entwickelt sich danach zu einer produktionsnah deploybaren v2.0-Architektur.

Das Projekt nutzt A2A fuer Agenten-Zusammenarbeit, MCP 2025-11-25 + Streamable HTTP + Tasks fuer Tool-Zugriff und eine provider registry, damit Cloud-Modelle und lokale Modelle gleichwertige Laufzeitziele sind.

## Status

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## Prinzipien

- Agenten rufen capabilities wie `voice.generate` und `motion.generate` auf, keine fest verdrahteten Modellnamen.
- Lokale Provider wie Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper und FFmpeg sind gleichwertige Ziele.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon und Live2D Cubism 5.3 sind Faehigkeits-Benchmarks, keine harten Abhaengigkeiten.

## Schnellstart

```bash
cp .env.example .env
docker compose config
```

Kanonische Dokumentation: [README.md](README.md). Lokalisierungsrichtlinie: [docs/i18n/README.md](docs/i18n/README.md).

## Lizenz

L2MAS steht unter der Lizenz [Apache-2.0](LICENSE). Bitte keine API-Keys, privaten Endpoints, Modellgewichte, kommerziellen Medien oder nicht autorisierten Live2D-Assets committen.

# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | Français | [Deutsch](README.de.md) | [Português](README.pt-BR.md) | [Русский](README.ru.md)

L2MAS est un prototype de generation d'animation Live2D multi-agent, concu autour des protocoles pour l'ecosysteme agentique de 2026. La feuille de route commence par un MVP local, puis evolue vers une architecture v2.0 deployable en production.

Il utilise A2A pour la collaboration entre agents, MCP 2025-11-25 + Streamable HTTP + Tasks pour l'acces aux outils, et un provider registry pour prendre en charge les modeles cloud et locaux dans la meme couche de routage.

## Etat

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## Principes

- Les agents appellent des capabilities comme `voice.generate` et `motion.generate`, pas des noms de modeles fixes.
- Les providers locaux comme Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper et FFmpeg sont des cibles de premiere classe.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon et Live2D Cubism 5.3 sont des references de capacite, pas des dependances obligatoires.

## Demarrage rapide

```bash
cp .env.example .env
docker compose config
```

Documentation canonique : [README.md](README.md). Politique de localisation : [docs/i18n/README.md](docs/i18n/README.md).

## Licence

L2MAS est publie sous licence [Apache-2.0](LICENSE). Ne commitez pas d'API keys, d'endpoints prives, de poids de modeles, de medias commerciaux ou d'assets Live2D non autorises.

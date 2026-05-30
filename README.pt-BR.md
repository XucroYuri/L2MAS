# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | Português do Brasil | [Русский](README.ru.md)

L2MAS e um prototipo de geracao de animacao Live2D multiagente, orientado a protocolos, para o ecossistema de agentes de 2026. O roadmap comeca com um MVP local e evolui para uma arquitetura v2.0 implantavel em producao.

Ele usa A2A para colaboracao entre agentes, MCP 2025-11-25 + Streamable HTTP + Tasks para acesso a ferramentas, e um provider registry para tratar modelos em nuvem e modelos locais como opcoes de primeira classe.

## Estado

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## Principios

- Agentes chamam capabilities como `voice.generate` e `motion.generate`, nao nomes fixos de modelos.
- Providers locais como Ollama, vLLM, LM Studio, llama.cpp, ComfyUI, Diffusers, Whisper e FFmpeg sao alvos de primeira classe.
- Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon e Live2D Cubism 5.3 sao referencias de capacidade, nao dependencias obrigatorias.

## Inicio rapido

```bash
cp .env.example .env
docker compose config
```

Documentacao canonica: [README.md](README.md). Politica de localizacao: [docs/i18n/README.md](docs/i18n/README.md).

## Licenca

L2MAS e licenciado sob [Apache-2.0](LICENSE). Nao envie API keys, endpoints privados, pesos de modelos, midia comercial ou assets Live2D nao autorizados.

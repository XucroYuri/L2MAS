# L2MAS: Live2D Multi-Agent Animation System

[English](README.md) | [简体中文](README.zh-CN.md) | 日本語 | [한국어](README.ko.md) | [Español](README.es.md)

L2MAS は、2026 年のエージェント・プロトコル環境を見据えた Live2D マルチエージェント・アニメーション生成プロトタイプです。まずローカル MVP を動かし、その後 v2.0 の分散アーキテクチャへ進化させることを目標にしています。

A2A でエージェント間連携を行い、MCP 2025-11-25 + Streamable HTTP + Tasks でツールを公開し、provider registry によってクラウドモデルとローカルモデルを同じ仕組みで扱います。

## ステータス

| Stage | Goal | Status |
| --- | --- | --- |
| MVP prototype | Run `script -> storyboard -> model -> voice -> motion -> render` locally | In progress |
| v2.0 architecture | A2A discovery, MCP tool clusters, streaming task progress, Kubernetes, observability, security, multi-tenancy | Planned |

## 設計原則

- エージェントは固定モデル名ではなく、`voice.generate` や `motion.generate` などの capability を呼び出します。
- Ollama、vLLM、LM Studio、llama.cpp、ComfyUI、Diffusers、Whisper、FFmpeg などのローカル provider を第一級の実行対象として扱います。
- Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 は能力基準であり、必須依存ではありません。

## クイックスタート

```bash
cp .env.example .env
docker compose config
```

Canonical documentation: [README.md](README.md). Localization policy: [docs/i18n/README.md](docs/i18n/README.md).

## ライセンス

L2MAS は [Apache-2.0](LICENSE) でライセンスされています。API key、private endpoint、model weights、商用メディア、未許可の Live2D assets はコミットしないでください。

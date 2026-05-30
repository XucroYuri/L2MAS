# L2MAS：Live2D 多 Agent 動畫生成系統

[English](README.md) | [简体中文](README.zh-CN.md) | 繁體中文 | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português](README.pt-BR.md) | [Русский](README.ru.md)

L2MAS 是面向 2026 協議生態的 Live2D 多 Agent 動畫生成原型。專案目標是先完成本地 MVP，再逐步演進到可生產部署的 v2.0 架構。

它使用 A2A 進行 Agent 協作，使用 MCP 2025-11-25 + Streamable HTTP + Tasks 暴露工具能力，並透過 provider registry 同時接入雲端模型與本地模型。

## 狀態

| 階段 | 目標 | 狀態 |
| --- | --- | --- |
| MVP 原型 | 本地跑通 `script -> storyboard -> model -> voice -> motion -> render` | 進行中 |
| v2.0 架構 | A2A 註冊發現、MCP 工具叢集、串流任務進度、Kubernetes、觀測、安全、多租戶 | 規劃中 |

## 核心設計

- Agent 依賴 capability，例如 `voice.generate`、`motion.generate`，而不是固定模型名稱。
- 雲端模型與本地模型都是一等 provider。
- Qwen3.7-Max、Gemini Omni、Eleven v3、Textoon、Live2D Cubism 5.3 只作為能力基準，不是硬依賴。

## 快速開始

```bash
cp .env.example .env
docker compose config
```

Canonical documentation: [README.md](README.md). 中文部署摘要：[deployment_guide.zh-CN.md](deployment_guide.zh-CN.md)。

## 開源

本專案使用 [Apache-2.0](LICENSE) 授權。請勿提交 API key、私有 endpoint、模型權重、商業素材或未授權 Live2D 資產。

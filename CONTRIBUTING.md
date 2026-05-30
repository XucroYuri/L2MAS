# Contributing

感谢你愿意参与 L2MAS。这个仓库当前定位为“面向 2026 协议生态的 Live2D 多 Agent 动画生成原型”，贡献重点是把 MVP 跑通，并保持后续 v2.0 分布式架构可演进。

## 开始之前

- 阅读 [README.md](README.md)、[docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md) 和 [deployment_guide.md](deployment_guide.md)。
- 不要提交 API key、私有 endpoint、模型权重、商业素材、未授权 Live2D 资产或大体积生成文件。
- 新增模型或工具集成时，请通过 provider registry 和 capability routing 接入，不要在 Agent 逻辑中写死供应商或模型名。

## 本地检查

提交 PR 前建议至少运行：

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
docker compose config > /dev/null
```

如果修改了 provider registry，请确认每个 capability 至少有一个 cloud 示例和一个 local 示例，或者在 PR 中说明为什么暂时做不到。

## 贡献流程

1. 从 `main` 创建一个短分支名，例如 `docs/open-source-ready` 或 `feat/provider-router`。
2. 让变更尽量小而完整。文档、配置、代码和测试应一起更新。
3. 提交 PR，并说明变更目的、影响范围、验证方式和未完成事项。
4. 维护者会优先审查可复现性、协议兼容性、许可证风险和是否破坏 MVP 路径。

## Commit 风格

推荐使用简短的 Conventional Commits 前缀：

- `docs:` 文档
- `feat:` 新能力
- `fix:` 修复
- `chore:` 仓库维护
- `test:` 测试或验证脚本

## 许可证

除非特别声明，你提交到本仓库的贡献会按 [Apache-2.0](LICENSE) 授权。

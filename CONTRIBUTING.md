# Contributing

Thank you for helping improve L2MAS. The project is an early prototype for protocol-first Live2D multi-agent animation, with an MVP path that should eventually evolve into a deployable v2.0 architecture.

## Before You Start

- Read [README.md](README.md), [docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md), and [deployment_guide.md](deployment_guide.md).
- Do not commit API keys, private endpoints, model weights, commercial media, unauthorized Live2D assets, or large generated files.
- Add new models and tools through provider registry and capability routing. Do not hard-code vendor or model names inside agent logic unless the file is explicitly a provider adapter.
- Keep English as the canonical documentation language. Localized READMEs should summarize and link back to the English source.

## Local Validation

Run these checks before opening a pull request:

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
docker compose config > /dev/null
```

If you change provider registry examples, confirm that each capability still has at least one cloud provider example and one local provider example, or explain the temporary exception in the PR.

## Contribution Workflow

1. Create a short branch from `main`, such as `docs/i18n-readmes` or `feat/provider-router`.
2. Keep the change small and complete. Update docs, configuration, tests, and examples together when behavior changes.
3. Open a pull request with the purpose, impact, validation results, and known gaps.
4. Maintainers will review reproducibility, protocol compatibility, licensing risk, and whether the MVP path remains intact.

## Commit Style

Conventional Commit prefixes are recommended:

- `docs:` documentation
- `feat:` new capability
- `fix:` bug fix
- `chore:` repository maintenance
- `test:` tests or validation scripts

## Localization

The canonical source is [README.md](README.md). Localized README files should:

- keep technical claims aligned with the English README
- avoid adding locale-only roadmap promises
- link to the English canonical docs for detailed setup
- be updated when the project status, capability list, or provider matrix changes

See [docs/i18n/README.md](docs/i18n/README.md).

## License

Unless stated otherwise, contributions submitted to this repository are licensed under [Apache-2.0](LICENSE).

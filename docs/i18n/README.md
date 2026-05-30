# Localization Policy

English is the canonical source for L2MAS documentation. Localized README files are intentionally limited to the top language set for Live2D technical development and community distribution.

## Supported README Locales

| Locale | File | Status |
| --- | --- | --- |
| `en` | [../../README.md](../../README.md) | canonical |
| `ja` | [../../README.ja.md](../../README.ja.md) | maintained summary |
| `zh-CN` | [../../README.zh-CN.md](../../README.zh-CN.md) | maintained summary |
| `ko` | [../../README.ko.md](../../README.ko.md) | maintained summary |
| `es` | [../../README.es.md](../../README.es.md) | maintained summary |

## Selection Rationale

- English: default technical development and GitHub discovery language.
- Japanese: Live2D's origin market and core creator/developer documentation language.
- Simplified Chinese: large Live2D, VTuber, illustration, and local AI creator/developer market.
- Korean: officially supported Cubism language and strong VTuber/game creator community.
- Spanish: growing Spanish-speaking creator community with official Live2D website support.

## Rules

- Keep detailed technical claims in English first.
- Localized READMEs should link to [../../README.md](../../README.md) for canonical setup, provider registry, capability names, and status.
- Do not add locale-only roadmap promises or benchmark claims.
- When the project status, capability list, provider registry fields, or quick-start commands change, update all locale summaries in the same pull request.
- Prefer clear technical wording over marketing language.

## File Naming

Use root-level README names that are common on GitHub:

```text
README.md
README.zh-CN.md
README.ja.md
README.ko.md
README.es.md
```

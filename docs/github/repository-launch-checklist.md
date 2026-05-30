# GitHub Repository Launch Checklist

This checklist prepares L2MAS for GitHub discovery, sharing, and community contributions.

GitHub's own documentation highlights README quality, community profile files, topics, and citation metadata as useful repository signals. This repository includes those files and keeps the launch metadata below ready for the repository settings page.

## Repository Identity

| Field | Recommended value |
| --- | --- |
| Repository name | `L2MAS` |
| Full name | `Live2D Multi-Agent Animation System` |
| Short description | `Protocol-first Live2D multi-agent animation prototype with MCP, A2A, provider routing, and cloud/local model support.` |
| Visibility | Public, after final secret scan |
| License | Apache-2.0 |
| Default branch | `main` |

## Suggested GitHub Topics

GitHub topics should describe purpose, subject area, community, and language. Use up to 20 focused topics:

```text
live2d
multi-agent
mcp
a2a
ai-agents
animation
generative-ai
provider-registry
local-ai
ollama
vllm
comfyui
diffusers
ffmpeg
text-to-animation
vtuber
tts
lip-sync
python
docker
```

## Social Preview Copy

Use this copy when creating a repository social preview image:

```text
L2MAS
Live2D Multi-Agent Animation System
MCP + A2A + provider routing for cloud and local AI animation pipelines
```

Recommended image size: 1280 x 640 px. Keep the design high contrast, legible at small sizes, and free of third-party trademarks unless usage rights are clear.

## Community Profile Files

Already present:

- [../../README.md](../../README.md)
- [../../LICENSE](../../LICENSE)
- [../../CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md)
- [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
- [../../SECURITY.md](../../SECURITY.md)
- [../../SUPPORT.md](../../SUPPORT.md)
- [../../.github/ISSUE_TEMPLATE/bug_report.yml](../../.github/ISSUE_TEMPLATE/bug_report.yml)
- [../../.github/ISSUE_TEMPLATE/feature_request.yml](../../.github/ISSUE_TEMPLATE/feature_request.yml)
- [../../.github/pull_request_template.md](../../.github/pull_request_template.md)

## Discovery Files

Already present:

- [../../CITATION.cff](../../CITATION.cff)
- [../../NOTICE](../../NOTICE)
- [../../CHANGELOG.md](../../CHANGELOG.md)
- [../../ROADMAP.md](../../ROADMAP.md)
- [../../GOVERNANCE.md](../../GOVERNANCE.md)
- [../../.github/repository-metadata.yml](../../.github/repository-metadata.yml)

## Final Local Checks

Run before creating the GitHub repository:

```bash
python3 -m json.tool config/a2a_config.json > /dev/null
python3 -m json.tool config/mcp_config.json > /dev/null
python3 -m json.tool config/provider_registry.example.json > /dev/null
docker compose config > /dev/null
python3 - <<'PY'
from pathlib import Path
import re

patterns = [
    re.compile("sk-" + r"[A-Za-z0-9_-]+"),
    re.compile("BEGIN " + r"(RSA|OPENSSH|EC|PRIVATE) KEY"),
    re.compile("GF_SECURITY_ADMIN_PASSWORD=" + "admin"),
]

hits = []
for path in Path(".").rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for pattern in patterns:
        if pattern.search(text):
            hits.append(str(path))

if hits:
    raise SystemExit("Potential secret/default-password hits:\n" + "\n".join(hits))
PY
```

The final command should return no results.

## Suggested Creation Command

After choosing the GitHub owner and confirming authentication:

```bash
gh repo create L2MAS \
  --public \
  --description "Protocol-first Live2D multi-agent animation prototype with MCP, A2A, provider routing, and cloud/local model support." \
  --source . \
  --remote origin \
  --push
```

After creation, set topics from the GitHub UI or with GitHub CLI if available:

```bash
gh repo edit --add-topic live2d --add-topic multi-agent --add-topic mcp --add-topic a2a --add-topic ai-agents --add-topic animation --add-topic generative-ai --add-topic provider-registry --add-topic local-ai --add-topic ollama --add-topic vllm --add-topic comfyui --add-topic diffusers --add-topic ffmpeg --add-topic text-to-animation --add-topic vtuber --add-topic tts --add-topic lip-sync --add-topic python --add-topic docker
```

## References

- [GitHub Docs: repository topics](https://docs.github.com/en/github/administering-a-repository/classifying-your-repository-with-topics)
- [GitHub Docs: repository README](https://docs.github.com/articles/about-readmes)
- [GitHub Docs: community profiles](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories)
- [GitHub Docs: citation files](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)

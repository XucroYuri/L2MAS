# CLAUDE.md — L2MAS Development Baseline

## Project Identity
- **Name**: L2MAS (Live2D Multi-Agent Animation System)
- **Type**: Protocol-first Live2D multi-agent animation prototype for the 2026 agent ecosystem
- **Stack**: Python 3.11+, MCP (2025-11-25) + A2A (1.0) protocols, Docker, Live2D Cubism 5.3
- **Remote**: `origin` = XucroYuri/L2MAS

## Quick Reference

```bash
pip install -r requirements.txt     # Install runtime deps
pip install -r requirements-dev.txt # Install dev deps
docker-compose up                   # Start full stack
python -m pytest tests/             # Run tests
```

## Architecture

```
User/App/API
  → Director Agent (storyboard planning, orchestration)
    → Modeling Agent (Live2D model/text-to-Live2D)
    → Voice Agent (TTS, voice conversion)
    → Animation Agent (motion, expression, lip-sync)
    → Renderer Agent (FFmpeg composition)

Protocol layer: A2A (agent collaboration) + MCP (tool access)
Provider registry: cloud and local models are first-class peers
```

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `agents/` | Multi-agent system implementations (Director, Modeling, Voice, Animation, Renderer) |
| `live2d_ai/` | Live2D AI animation integration |
| `mcp/` | MCP protocol compatibility layer |
| `a2a/` | A2A protocol compatibility layer |
| `config/` | Configuration files |
| `examples/` | Example projects and demos |
| `tests/` | Test suites |
| `docs/` | Detailed documentation and release notes |
| `k8s/` | Kubernetes deployment config |

## Development Rules

1. **Protocol-first design**: Agents call capabilities (e.g., `voice.generate`), not fixed vendor models
2. **Provider registry**: All model/runtime integrations go through the provider registry with capability routing
3. **Cloud/local parity**: Local providers are not a fallback — they are a supported deployment mode
4. **Python 3.11+**: Use modern Python features, type hints recommended
5. **Docker**: All services should be Docker-compatible
6. **Testing**: Write tests for agent behavior and protocol compliance
7. **Commit style**: Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)

## Dependencies
- Python 3.11+
- Docker & Docker Compose
- MCP 2025-11-25
- A2A 1.0
- FFmpeg (for rendering)
- Optional: Live2D Cubism SDK, Textoon, ComfyUI

## Avoid
- Hardcoding model names or vendor APIs — use the provider registry
- Mixing protocol concerns with creative logic
- Adding dependencies without updating requirements.txt
- Committing `.env` files or secrets

# Roadmap

The full architecture narrative lives in [docs/architecture/two-stage-roadmap.md](docs/architecture/two-stage-roadmap.md). This file is a GitHub-facing summary.

## MVP Prototype

- Run an end-to-end local flow from script to rendered video.
- Keep the deterministic mock path available when cloud API keys are absent.
- Stabilize provider registry and capability routing.
- Validate FFmpeg local rendering as the default composition path.
- Add focused tests for registry parsing, routing, and artifact schemas.

## v2.0 Production-Deployable Direction

- Introduce A2A registry-backed Agent discovery and task routing.
- Wrap core tools behind MCP 2025-11-25 Streamable HTTP and Tasks.
- Add Writer, Artist, LipSync, and QA agents.
- Move selected services to Kubernetes with observability, security, and tenant isolation.
- Publish benchmark reports for latency, cost, quality, and provider fallback behavior.

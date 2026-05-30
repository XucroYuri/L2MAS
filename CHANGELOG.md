# Changelog

All notable changes to this project will be documented in this file.

This project follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/) once versioned releases begin.

## [Unreleased]

### Added

- GitHub discovery profile with search-focused metadata, topics, labels, starter issues, and social preview guidance.
- README at-a-glance section for faster project recognition by GitHub visitors and searchers.

## [0.1.0] - 2026-05-30

### Added

- Deterministic local mock MVP pipeline for provider routing and smoke tests.
- Local A2A/MCP compatibility layers for prototype imports and mock tool calls.
- Local FFmpeg `video.compose` provider for real MP4 container smoke tests.
- Apache-2.0 license and open-source community files.
- GitHub issue templates, pull request template, and lightweight CI checks.
- Two-stage MVP to v2.0 architecture documentation.
- Provider registry example covering cloud, local, and hybrid model providers.

### Changed

- CI now runs static checks, dependency metadata checks, Python compile checks, and MVP smoke tests.
- Project framing now treats Qwen3.7-Max, Gemini Omni, Eleven v3, Textoon, and Live2D Cubism 5.3 as capability baselines instead of hard dependencies.
- Deployment narrative now describes target metrics and validation work instead of completed production guarantees.

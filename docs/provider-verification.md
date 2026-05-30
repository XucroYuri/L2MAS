# Provider Verification Matrix

This matrix records what is implemented, contract-tested, and live-verified in this repository. Public documentation must not describe a provider as verified unless it appears here with `verified` status and a validation note.

Status meanings:

- `verified`: live execution was validated in this repository environment.
- `experimental`: adapter boundary and mocked contract tests exist; live verification is optional and environment-gated.
- `template`: registry entry and generic adapter contract exist; a concrete service implementation still needs validation.
- `mock`: deterministic local test provider.

## v0.2.0 Adapter Status

| Provider | Status | Capabilities | Validation |
| --- | --- | --- | --- |
| `local-ffmpeg` | verified | `video.compose` | Live local MP4 smoke test when FFmpeg is installed. |
| `cloud-qwen-agent` | experimental | `script.plan`, `quality.review` | OpenAI-compatible contract path; live test requires `L2MAS_LIVE_QWEN` and `QWEN_API_KEY`. |
| `local-ollama-agent` | experimental | `script.plan`, `quality.review` | Ollama OpenAI-compatible contract path; live test requires `L2MAS_LIVE_OLLAMA`. |
| `local-vllm-agent` | experimental | `script.plan`, `quality.review` | OpenAI-compatible contract path; live test requires `L2MAS_LIVE_VLLM`. |
| `local-lmstudio-agent` | experimental | `script.plan`, `quality.review` | OpenAI-compatible contract path; live test requires `L2MAS_LIVE_LMSTUDIO`. |
| `local-llamacpp-agent` | experimental | `script.plan`, `quality.review` | OpenAI-compatible contract path; live test requires `L2MAS_LIVE_LLAMACPP`. |
| `cloud-gemini-video` | experimental | `character.generate`, `video.edit`, `quality.review` | Generic multimodal REST boundary; live test requires `L2MAS_LIVE_GEMINI` and `GEMINI_API_KEY`. |
| `local-comfyui-visual` | experimental | `character.generate`, `video.edit` | ComfyUI `/prompt` contract path; live test requires `L2MAS_LIVE_COMFYUI`. |
| `local-diffusers-visual` | template | `character.generate`, `video.edit` | Generic REST contract only. |
| `local-textoon` | template | `model.live2d.generate` | Generic REST contract only. |
| `cloud-textoon` | template | `model.live2d.generate` | Generic REST contract only. |
| `cloud-elevenlabs-voice` | experimental | `voice.generate` | ElevenLabs TTS contract path; live test requires `L2MAS_LIVE_ELEVENLABS` and `ELEVENLABS_API_KEY`. |
| `local-tts` | template | `voice.generate` | Generic REST contract only. |
| `local-openai-whisper` | template | `speech.transcribe` | OpenAI-compatible transcription contract only. |
| `local-whisper` | template | `speech.transcribe` | Generic REST contract only. |
| `cloud-stt` | template | `speech.transcribe` | Generic REST contract only. |
| `local-rvc` | template | `voice.convert` | Generic REST contract only. |
| `cloud-voice-conversion` | template | `voice.convert` | Generic REST contract only. |
| `local-lipsync` | template | `lip_sync.align` | Generic REST contract only. |
| `cloud-lipsync` | template | `lip_sync.align` | Generic REST contract only. |
| `local-live2d-motion` | template | `motion.generate` | MCP template boundary only. |
| `cloud-motion` | template | `motion.generate` | Generic REST contract only. |
| `cloud-render` | template | `video.compose` | Generic REST contract only. |
| `local-embedding` | template | `quality.review` | OpenAI-compatible contract path only. |
| `mock-agent` | mock | `script.plan`, `quality.review` | Deterministic local tests. |
| `mock-visual` | mock | `character.generate`, `video.edit` | Deterministic local tests. |
| `mock-live2d-model` | mock | `model.live2d.generate` | Deterministic local tests. |
| `mock-voice` | mock | `voice.generate` | Deterministic local tests. |
| `mock-transcribe` | mock | `speech.transcribe` | Deterministic local tests. |
| `mock-voice-convert` | mock | `voice.convert` | Deterministic local tests. |
| `mock-lipsync` | mock | `lip_sync.align` | Deterministic local tests. |
| `mock-motion` | mock | `motion.generate` | Deterministic local tests. |
| `mock-render` | mock | `video.compose` | Deterministic local tests. |

## Disclosure Rule

README, release notes, and GitHub descriptions may say that a provider is verified only when this matrix marks it `verified`. Experimental and template providers must be described as adapter contracts or optional live-test targets, not as production-ready integrations.

## Probe Command

Generate a JSON report without enabling live HTTP probes:

```bash
python3 examples/probe_providers.py --output output/provider-probe.json
```

Probe one provider:

```bash
python3 examples/probe_providers.py --provider mock-voice --output output/provider-probe-mock-voice.json
```

Live HTTP probes require either `--include-live` or the provider-specific `L2MAS_LIVE_*` environment variable. Do not update a provider to `verified` until the report is reviewed and the validation evidence is added to this document.

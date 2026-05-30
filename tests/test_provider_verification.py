import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from live2d_ai.provider_registry import Provider, ProviderRegistry
from live2d_ai.provider_verification import ProviderVerifier, report_to_markdown


def provider(**overrides):
    raw = {
        "provider_id": "local-http",
        "locality": "local",
        "protocol": "custom-rest",
        "capabilities": ["voice.generate"],
        "endpoint": "http://provider.test",
        "models": ["model"],
        "hardware_profile": "test",
        "priority": 1,
        "fallbacks": [],
        "privacy_mode": "local-only",
        "status": "experimental",
        "live_test_env": "L2MAS_LIVE_TEST_PROVIDER",
        "healthcheck": {"method": "GET", "path": "/health"},
    }
    raw.update(overrides)
    return Provider.from_dict(raw)


class ProviderVerificationTest(unittest.IsolatedAsyncioTestCase):
    async def test_skips_live_http_probe_when_env_is_not_enabled(self):
        registry = ProviderRegistry([provider()])

        report = await ProviderVerifier(registry).run()

        self.assertEqual(report["providers"][0]["probe_result"], "skipped")
        self.assertEqual(report["providers"][0]["live_test_env"], "L2MAS_LIVE_TEST_PROVIDER")

    async def test_runs_http_probe_when_env_is_enabled(self):
        requests = []

        async def transport(request):
            requests.append(request)
            self.assertEqual(request["path"], "/health")
            return {"status_code": 200, "json": {"ok": True}}

        registry = ProviderRegistry([provider()])
        with patch.dict("os.environ", {"L2MAS_LIVE_TEST_PROVIDER": "1"}, clear=False):
            report = await ProviderVerifier(registry, http_transport=transport).run()

        self.assertEqual(len(requests), 1)
        self.assertEqual(report["providers"][0]["probe_result"], "passed")

    async def test_reports_binary_healthcheck(self):
        registry = ProviderRegistry(
            [
                provider(
                    provider_id="local-tool",
                    protocol="mcp",
                    capabilities=["video.compose"],
                    status="verified",
                    live_test_env="L2MAS_LIVE_TOOL",
                    healthcheck={"type": "binary", "name": "python3"},
                    verification_evidence="docs/verification/local-tool.json",
                )
            ]
        )

        report = await ProviderVerifier(registry).run()

        self.assertEqual(report["providers"][0]["probe_result"], "passed")
        self.assertEqual(report["providers"][0]["configured_status"], "verified")
        self.assertEqual(report["providers"][0]["verification_evidence"], "docs/verification/local-tool.json")

    async def test_writes_json_report(self):
        registry = ProviderRegistry([provider()])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"

            report = await ProviderVerifier(registry).write_json(path)

            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["summary"], report["summary"])

    async def test_report_to_markdown_lists_provider_results(self):
        registry = ProviderRegistry([provider(provider_id="mock-voice", endpoint="mock://voice", status="mock")])
        report = await ProviderVerifier(registry).run()

        markdown = report_to_markdown(report)

        self.assertIn("| Provider | Configured status | Probe result |", markdown)
        self.assertIn("`mock-voice`", markdown)


if __name__ == "__main__":
    unittest.main()

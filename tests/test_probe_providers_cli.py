import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ProbeProvidersCliTest(unittest.TestCase):
    def test_cli_writes_json_report_for_selected_mock_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "examples/probe_providers.py",
                    "--provider",
                    "mock-voice",
                    "--output",
                    str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertIn("Provider probe report written", completed.stdout)
        self.assertEqual(report["providers"][0]["provider_id"], "mock-voice")
        self.assertEqual(report["providers"][0]["probe_result"], "mock")


if __name__ == "__main__":
    unittest.main()

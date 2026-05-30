import unittest
from pathlib import Path

from live2d_ai import __version__


class ReleaseMetadataTest(unittest.TestCase):
    def test_version_is_exposed_and_documented(self):
        citation = Path("CITATION.cff").read_text(encoding="utf-8")
        changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertIn(f"version: {__version__}", citation)
        self.assertIn(f"## [{__version__}]", changelog)


if __name__ == "__main__":
    unittest.main()

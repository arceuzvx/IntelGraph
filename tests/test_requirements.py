import re
import unittest
from pathlib import Path


class RequirementsCompatibilityTests(unittest.TestCase):
    def _requirement_version(self, package: str) -> str:
        requirements_text = Path("requirements.txt").read_text(encoding="utf-8")
        match = re.search(rf"^{re.escape(package)}==(.+)$", requirements_text, re.MULTILINE)
        self.assertIsNotNone(match, f"{package} pin not found in requirements.txt")
        return match.group(1)

    def test_python_311_compatible_pins(self) -> None:
        """Verify that directly-pinned packages use Python 3.11 compatible versions."""
        self.assertEqual(self._requirement_version("numpy"), "1.26.4")
        self.assertEqual(self._requirement_version("torch"), "2.2.2+cpu")


if __name__ == "__main__":
    unittest.main()

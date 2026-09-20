# -*- coding: utf-8 -*-
"""
==============================================================================
Unit tests for AegisFlow Tech-Stack Sniffer (tools/stack_sniffer.py)
==============================================================================
"""

import json
import tempfile
import unittest
from pathlib import Path

from tools.stack_sniffer import StackSniffer


class TestStackSniffer(unittest.TestCase):
    """
    Unit test suite for multi-language stack sniffer.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sniff_python_project(self):
        """Test detection of Python ecosystem and default unittest command."""
        (self.root / "requirements.txt").write_text("pytest>=7.0.0\n", encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()

        sniffer = StackSniffer(str(self.root))
        profile = sniffer.sniff()

        self.assertIn("Python", profile["detected_languages"])
        self.assertEqual(profile["primary_language"], "Python")
        self.assertIn("python -m unittest", profile["default_test_command"])
        self.assertTrue(profile["has_src_dir"])
        self.assertTrue(profile["has_tests_dir"])

    def test_sniff_node_project(self):
        """Test detection of Node.js / TypeScript ecosystem."""
        pkg_data = {
            "name": "demo-app",
            "scripts": {
                "test": "jest",
                "build": "tsc"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "jest": "^29.0.0"
            }
        }
        (self.root / "package.json").write_text(json.dumps(pkg_data), encoding="utf-8")

        sniffer = StackSniffer(str(self.root))
        profile = sniffer.sniff()

        self.assertTrue(any("Node" in lang or "TypeScript" in lang for lang in profile["detected_languages"]))
        self.assertEqual(profile["default_test_command"], "npm test")
        self.assertEqual(profile["default_build_command"], "npm run build")

    def test_sniff_go_project(self):
        """Test detection of Go ecosystem."""
        (self.root / "go.mod").write_text("module example.com/demo\n\ngo 1.21\n", encoding="utf-8")

        sniffer = StackSniffer(str(self.root))
        profile = sniffer.sniff()

        self.assertIn("Go", profile["detected_languages"])
        self.assertEqual(profile["default_test_command"], "go test ./...")
        self.assertEqual(profile["default_build_command"], "go build ./...")

    def test_sniff_rust_project(self):
        """Test detection of Rust ecosystem."""
        (self.root / "Cargo.toml").write_text("[package]\nname = \"demo\"\nversion = \"0.1.0\"\n", encoding="utf-8")

        sniffer = StackSniffer(str(self.root))
        profile = sniffer.sniff()

        self.assertIn("Rust", profile["detected_languages"])
        self.assertEqual(profile["default_test_command"], "cargo test")
        self.assertEqual(profile["default_build_command"], "cargo build")

    def test_save_profile(self):
        """Test persisting profile to JSON file."""
        (self.root / "setup.py").write_text("# setup\n", encoding="utf-8")
        sniffer = StackSniffer(str(self.root))
        saved_path = sniffer.save_profile()

        self.assertTrue(saved_path.exists())
        data = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(data["primary_language"], "Python")


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""
==============================================================================
Unit tests for AegisFlow Git Pre-commit Hook Guard (tools/git_hook.py)
==============================================================================
"""

import tempfile
import unittest
from pathlib import Path

from tools.git_hook import GitHookManager
from tools.state_manager import StateManager
from tools.repo_hygiene import RepoHygieneGuard


class TestGitHookManager(unittest.TestCase):
    """
    Test suite for GitHookManager install, uninstall, and pre-commit verification.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        # Create fake .git directory
        (self.root / ".git").mkdir()
        self.hook_mgr = GitHookManager(str(self.root))
        self.sm = StateManager(str(self.root))
        self.hyg = RepoHygieneGuard(str(self.root))
        self.hyg.init_scaffolding()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_install_and_uninstall_hook(self):
        """Test installing and removing the pre-commit hook file."""
        ok, msg = self.hook_mgr.install_hook()
        self.assertTrue(ok)
        hook_path = self.root / ".git" / "hooks" / "pre-commit"
        self.assertTrue(hook_path.exists())

        ok, msg = self.hook_mgr.uninstall_hook()
        self.assertTrue(ok)
        self.assertFalse(hook_path.exists())

    def test_verify_fails_without_active_task(self):
        """Test pre-commit rejected when there are no active tasks on board."""
        passed, msg = self.hook_mgr.verify_pre_commit(self.sm, self.hyg)
        self.assertFalse(passed)
        self.assertIn("No active task card found", msg)

    def test_verify_passes_with_active_task_and_clean_root(self):
        """Test pre-commit passes when active task exists and root is clean."""
        self.sm.create_task("TSK-101", "Implement hook", tier=1, assignee="developer")
        self.sm.start_task("TSK-101", "developer")

        passed, msg = self.hook_mgr.verify_pre_commit(self.sm, self.hyg)
        self.assertTrue(passed)
        self.assertIn("Pre-commit verified", msg)

    def test_verify_fails_on_root_pollution(self):
        """Test pre-commit rejected when root directory has stray pollution files."""
        self.sm.create_task("TSK-102", "Implement feature", tier=1, assignee="developer")
        self.sm.start_task("TSK-102", "developer")

        # Create an illegal stray file in root
        (self.root / "temp_scratch_pad.py").write_text("# stray file", encoding="utf-8")

        passed, msg = self.hook_mgr.verify_pre_commit(self.sm, self.hyg)
        self.assertFalse(passed)
        self.assertIn("Cleanliness Violation", msg)


if __name__ == "__main__":
    unittest.main()

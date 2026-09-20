# -*- coding: utf-8 -*-
"""
==============================================================================
Unit tests for AegisFlow Studio Heartbeat Monitor (tools/heartbeat.py)
==============================================================================
"""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from tools.heartbeat import StudioHeartbeat
from tools.state_manager import StateManager


class TestStudioHeartbeat(unittest.TestCase):
    """
    Test suite for StudioHeartbeat health scoring and anomaly inspection.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.sm = StateManager(str(self.root))
        self.heartbeat = StudioHeartbeat(self.root, stale_threshold_hours=8.0)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_studio_heartbeat(self):
        """Test health score is 100 on clean studio with no anomalies."""
        report = self.heartbeat.run_inspection()
        self.assertEqual(report["health_score"], 100)
        self.assertEqual(report["status_label"], "HEALTHY")
        self.assertEqual(len(report["stale_tasks"]), 0)
        self.assertEqual(len(report["near_circuit_breaker_tasks"]), 0)
        self.assertEqual(len(report["blocked_tasks"]), 0)

    def test_near_circuit_breaker_detection(self):
        """Test detection of task with 2 rejections (1 away from circuit breaker)."""
        self.sm.create_task("TSK-201", "Complex Feature", tier=2, assignee="developer")
        self.sm.start_task("TSK-201", "developer")
        self.sm.advance_stage("TSK-201", "CODE_REVIEW", "developer")
        self.sm.reject_task("TSK-201", "reviewer", "QR", "First quality rejection")
        self.sm.advance_stage("TSK-201", "CODE_REVIEW", "developer")
        self.sm.reject_task("TSK-201", "reviewer", "QR", "Second quality rejection")

        report = self.heartbeat.run_inspection()
        self.assertEqual(len(report["near_circuit_breaker_tasks"]), 1)
        self.assertEqual(report["near_circuit_breaker_tasks"][0]["task_id"], "TSK-201")
        # 100 - 15 = 85
        self.assertEqual(report["health_score"], 85)
        self.assertEqual(report["status_label"], "ATTENTION")

    def test_blocked_task_detection(self):
        """Test detection of blocked tasks after circuit breaker triggers."""
        self.sm.create_task("TSK-202", "Fragile Feature", tier=2, assignee="developer")
        self.sm.start_task("TSK-202", "developer")
        self.sm.advance_stage("TSK-202", "CODE_REVIEW", "developer")
        self.sm.reject_task("TSK-202", "reviewer", "QR", "First rejection")
        self.sm.advance_stage("TSK-202", "CODE_REVIEW", "developer")
        self.sm.reject_task("TSK-202", "reviewer", "QR", "Second rejection")
        self.sm.advance_stage("TSK-202", "CODE_REVIEW", "developer")
        # Third rejection triggers circuit breaker -> BLOCKED
        self.sm.reject_task("TSK-202", "reviewer", "QR", "Third rejection - Circuit Breaker")

        report = self.heartbeat.run_inspection()
        self.assertEqual(len(report["blocked_tasks"]), 1)
        self.assertEqual(report["blocked_tasks"][0]["task_id"], "TSK-202")
        # Deduct 20 pts for blocked task
        self.assertEqual(report["health_score"], 80)

    def test_stale_task_detection(self):
        """Test detection of task exceeding the 8h duration limit."""
        self.sm.create_task("TSK-203", "Stale Feature", tier=2, assignee="developer")
        self.sm.start_task("TSK-203", "developer")

        # Artificially age the task started_at to 12 hours ago
        stale_time = (datetime.now() - timedelta(hours=12)).isoformat()
        self.sm.data["tasks"]["TSK-203"]["started_at"] = stale_time
        self.sm._save()

        report = self.heartbeat.run_inspection()
        self.assertEqual(len(report["stale_tasks"]), 1)
        self.assertEqual(report["stale_tasks"][0]["task_id"], "TSK-203")
        self.assertGreaterEqual(report["stale_tasks"][0]["duration_hours"], 11.5)
        # Deduct 10 pts for stale task
        self.assertEqual(report["health_score"], 90)

    def test_print_heartbeat_report(self):
        """Test print_heartbeat_report executes without error."""
        try:
            self.heartbeat.print_heartbeat_report()
        except Exception as e:
            self.fail(f"print_heartbeat_report raised unexpected exception: {e}")


if __name__ == "__main__":
    unittest.main()

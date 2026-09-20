"""
Unit tests for AegisFlow StateManager (state_manager.py)
=========================================================

验证任务状态机全生命周期逻辑：
- 任务卡片创建格式校验与单一职责原则 (SRP <= 8.0h) 阈值管控。
- 任务开始、推进与人类专属终审阶段权限屏障。
- 四维专业打回 (#QR/#SR/#FR/#DR) 原工单编号继承。
- 三振出局熔断机制 (Circuit Breaker) 与强制挂起锁定。
- 检查点快照与时光倒流 (Time-Travel Rollback) 状态回退。
- OpenHands 风格不可变事件流审计记录。
- 防 Token 膨胀 Top-5 活跃任务截断。
"""

import json
import tempfile
import unittest
from pathlib import Path
from tools.state_manager import StateManager, STAGES, ROLES, ITEM_TYPES, REJECT_TYPES


class TestStateManager(unittest.TestCase):
    """
    StateManager 核心方法单元测试用例集。
    """

    def setUp(self):
        """
        为每个测试用例创建干净隔离的临时工作目录，避免污染实际项目状态。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = StateManager(root_dir=self.temp_dir.name)

    def tearDown(self):
        """
        清理临时目录。
        """
        self.temp_dir.cleanup()

    def test_create_task_success(self):
        """
        测试正常任务创建流程，验证初始字段、持久化及 EventStream 事件记录。
        """
        task = self.manager.create_task(
            task_id="TSK-1001",
            title="Implement User Authentication",
            desc="Add JWT token generation and validation",
            tier=2,
            item_type="TSK",
            priority="HIGH",
            assignee="pm",
            est_hours=6.0
        )
        self.assertEqual(task["id"], "TSK-1001")
        self.assertEqual(task["title"], "Implement User Authentication")
        self.assertEqual(task["tier"], 2)
        self.assertEqual(task["stage"], "BACKLOG")
        self.assertEqual(task["est_hours"], 6.0)
        self.assertEqual(self.manager.data["metrics"]["total_created"], 1)

        # 验证看板数据库持久化
        storage_file = Path(self.temp_dir.name) / ".agents" / ".virtual_company_board.json"
        self.assertTrue(storage_file.exists())

        # 验证 EventStream 事件日志落盘
        event_stream = Path(self.temp_dir.name) / ".agents" / "event_stream.jsonl"
        self.assertTrue(event_stream.exists())
        with open(event_stream, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            event = json.loads(lines[0])
            self.assertEqual(event["event_type"], "TASK_CREATED")
            self.assertEqual(event["task_id"], "TSK-1001")

    def test_create_task_invalid_id_format(self):
        """
        测试非法工单编号前缀与格式校验拦截。
        """
        with self.assertRaises(ValueError):
            self.manager.create_task(task_id="INVALID_FORMAT", title="Bad ID")

        with self.assertRaises(ValueError):
            self.manager.create_task(task_id="BUG-1001", title="Non-standard prefix")

    def test_create_task_duplicate_id(self):
        """
        测试反洗刷机制：严禁重复创建已存在的同名工单。
        """
        self.manager.create_task(task_id="TSK-1002", title="First Task")
        with self.assertRaises(ValueError):
            self.manager.create_task(task_id="TSK-1002", title="Duplicate Task")

    def test_create_task_srp_cap_violation(self):
        """
        测试单一职责原则 (SRP) 工时上限校验：Tier 2/3 超出 8.0h 必须抛出异常。
        """
        # Tier 2 超过 8.0h 必须被拒绝并提示拆单
        with self.assertRaises(ValueError) as ctx:
            self.manager.create_task(
                task_id="TSK-1003",
                title="Massive task",
                tier=2,
                est_hours=12.0
            )
        self.assertIn("SRP Violation", str(ctx.exception))

        # Tier 1 探针或小型补丁不受该限制 (例如技术尖峰 Spike)
        task = self.manager.create_task(
            task_id="SPK-1004",
            title="Spike Exploration",
            tier=1,
            est_hours=12.0
        )
        self.assertEqual(task["est_hours"], 12.0)

    def test_start_task(self):
        """
        测试启动任务：记录 started_at 时间戳并迁移至 IN_PROGRESS。
        """
        self.manager.create_task(task_id="TSK-2001", title="Start Test Task")
        started = self.manager.start_task("TSK-2001", role="developer")
        self.assertEqual(started["stage"], "IN_PROGRESS")
        self.assertEqual(started["assignee"], "developer")
        self.assertIsNotNone(started["started_at"])

    def test_start_task_forbidden_on_terminal_state(self):
        """
        测试终态不可逆：已处于 ACCEPTED 状态的任务禁止重新启动。
        """
        self.manager.create_task(task_id="TSK-2002", title="Terminal Task")
        self.manager.data["tasks"]["TSK-2002"]["stage"] = "ACCEPTED"
        with self.assertRaises(ValueError):
            self.manager.start_task("TSK-2002", role="developer")

    def test_advance_stage_standard_flow(self):
        """
        测试标准正向阶段推进与凭证收据追加。
        """
        self.manager.create_task(task_id="TSK-3001", title="Advance Test Task")
        self.manager.start_task("TSK-3001", role="developer")
        
        advanced = self.manager.advance_stage(
            task_id="TSK-3001",
            target_stage="CODE_REVIEW",
            role="code_reviewer",
            note="Ready for peer review",
            receipt_path="receipts/REC-G1.json"
        )
        self.assertEqual(advanced["stage"], "CODE_REVIEW")
        self.assertEqual(advanced["assignee"], "code_reviewer")
        self.assertIn("receipts/REC-G1.json", advanced["deliverables"]["receipts"])

    def test_advance_stage_agent_forbidden_from_accepted(self):
        """
        测试人类专属终态保护：Agent 严禁擅自将任务推进至 ACCEPTED 状态。
        """
        self.manager.create_task(task_id="TSK-3002", title="Advance to Accept Test")
        with self.assertRaises(PermissionError):
            self.manager.advance_stage(
                task_id="TSK-3002",
                target_stage="ACCEPTED",
                role="developer",
                note="Agent attempting self-acceptance"
            )

    def test_rejections_and_veto_tagging(self):
        """
        测试专业打回原号继承：生成 TSK-xxxx#<TYPE>-<N> 格式并记录回退。
        """
        self.manager.create_task(task_id="TSK-4001", title="Rejectable Task")
        self.manager.start_task("TSK-4001", role="developer")

        # 1. 质量审查一票否决 (#QR)
        task = self.manager.reject_task(
            task_id="TSK-4001",
            role="code_reviewer",
            reject_type="QR",
            reason="Unchecked null pointer in auth handler",
            target_stage="IN_PROGRESS"
        )
        self.assertEqual(len(task["rejections"]), 1)
        self.assertEqual(task["rejections"][0]["tag"], "TSK-4001#QR-1")
        self.assertEqual(task["stage"], "IN_PROGRESS")
        self.assertEqual(task["assignee"], "developer")
        self.assertEqual(self.manager.data["metrics"]["total_rejections"], 1)

        # 2. 安全审计一票否决 (#SR)
        task = self.manager.reject_task(
            task_id="TSK-4001",
            role="security_engineer",
            reject_type="SR",
            reason="Plaintext API token found in config",
            target_stage="IN_PROGRESS"
        )
        self.assertEqual(len(task["rejections"]), 2)
        self.assertEqual(task["rejections"][1]["tag"], "TSK-4001#SR-2")

    def test_circuit_breaker_locks_to_blocked(self):
        """
        测试三振出局熔断机制：累计打回达 3 次时，任务强制锁定为 BLOCKED 并指派 CTO。
        """
        self.manager.create_task(task_id="TSK-4002", title="Troublesome Task")
        self.manager.start_task("TSK-4002", role="developer")

        self.manager.reject_task("TSK-4002", "code_reviewer", "QR", "Style issue 1")
        self.manager.reject_task("TSK-4002", "security_engineer", "SR", "Security issue 2")
        
        # 第 3 次打回触发强熔断保护
        task = self.manager.reject_task("TSK-4002", "qa_engineer", "FR", "Functional bug 3")
        self.assertEqual(len(task["rejections"]), 3)
        self.assertEqual(task["stage"], "BLOCKED")
        self.assertEqual(task["assignee"], "cto")
        self.assertEqual(self.manager.data["metrics"]["circuit_breakers_triggered"], 1)

    def test_time_travel_rollback(self):
        """
        测试时光倒流回滚 (Time-Travel)：从历史检查点完整恢复任务快照。
        """
        self.manager.create_task(task_id="TSK-5001", title="Time Travel Task")
        self.manager.start_task("TSK-5001", role="developer")
        self.manager.advance_stage("TSK-5001", target_stage="CODE_REVIEW", role="code_reviewer")
        self.manager.advance_stage("TSK-5001", target_stage="SECURITY_AUDIT", role="security_engineer")

        # 回滚至 IN_PROGRESS 历史检查点
        restored = self.manager.rollback_to_checkpoint("TSK-5001", target_stage="IN_PROGRESS")
        self.assertEqual(restored["stage"], "IN_PROGRESS")
        self.assertEqual(self.manager.get_task("TSK-5001")["stage"], "IN_PROGRESS")

    def test_human_acceptance_flow(self):
        """
        测试人类终审验收业务逻辑 (Gate 6)。
        """
        self.manager.create_task(task_id="TSK-6001", title="Feature Ready for Acceptance")
        self.manager.start_task("TSK-6001", role="developer")
        self.manager.advance_stage("TSK-6001", target_stage="COMPLETED", role="release_engineer")

        # 未处于 COMPLETED 状态的工单禁止验收
        self.manager.create_task(task_id="TSK-6002", title="Unfinished Feature")
        with self.assertRaises(ValueError):
            self.manager.accept_task("TSK-6002", accepted_by="HUMAN_OPERATOR")

        # 对 COMPLETED 工单正式确认验收
        accepted = self.manager.accept_task("TSK-6001", accepted_by="HUMAN_OPERATOR", note="Verified in staging")
        self.assertEqual(accepted["stage"], "ACCEPTED")
        self.assertTrue(accepted["gate_status"]["gate_6_human_accept"])
        self.assertIsNotNone(accepted["accepted_at"])
        self.assertEqual(self.manager.data["metrics"]["total_accepted"], 1)

    def test_list_tasks_and_top5_anti_token_bleed(self):
        """
        测试工单列表与 Top-5 节流逻辑，保障终端看板防 Token 膨胀。
        """
        for i in range(1, 10):
            self.manager.create_task(task_id=f"TSK-700{i}", title=f"Task {i}", est_hours=2.0)

        all_tasks = self.manager.list_tasks()
        self.assertEqual(len(all_tasks), 9)

        # Top-5 最多仅返回 5 条活跃卡片
        top5 = self.manager.get_top5_active()
        self.assertEqual(len(top5), 5)


if __name__ == "__main__":
    unittest.main()

"""
Integration tests for AegisFlow CLI (vc_cli.py)
================================================

通过真实子进程调用测试 vc-cli 命令行端到端闭环交互：
- CLI 帮助信息与版本查看 (--help)。
- 项目脚手架与看板初始化 (vc-cli init & board)。
- 完整工单生命周期：建单 -> 启动 -> 推进 -> 否决打回 -> 修复 -> 终审验收 -> 状态查询。
- SWE-agent 快速语法快筛 (vc-cli lint) 与 AST Repo Map 刷新 (vc-cli repomap)。
"""

import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestVcCli(unittest.TestCase):
    """
    vc-cli 命令行子进程集成测试用例集。
    """

    def setUp(self):
        """
        初始化隔离的临时工作目录，并准备被测 CLI 脚本的绝对路径。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project_root = Path(__file__).resolve().parent.parent
        self.cli_path = self.project_root / "tools" / "vc_cli.py"

    def tearDown(self):
        """
        清理临时测试目录。
        """
        self.temp_dir.cleanup()

    def run_cli(self, args: list, input_str: str = None) -> subprocess.CompletedProcess:
        """
        在隔离工作目录下以子进程方式运行 vc-cli，强制指定 UTF-8 编码防乱码。

        :param args: 传递给 vc-cli 的命令行参数列表
        :param input_str: 标准输入流数据 (可选)
        :return: CompletedProcess 执行结果对象
        """
        cmd = [sys.executable, str(self.cli_path)] + args
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            cmd,
            cwd=str(self.root),
            capture_output=True,
            text=True,
            input=input_str,
            env=env,
            timeout=30,
            encoding="utf-8",
            errors="replace"
        )

    def test_cli_help(self):
        """
        测试 vc-cli --help 基础可用性与说明文本输出。
        """
        res = self.run_cli(["--help"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("AegisFlow Virtual Studio Management CLI", res.stdout)

    def test_cli_init_and_board(self):
        """
        测试工程脚手架初始化及空看板渲染。
        """
        # 1. 执行 init 初始化脚手架
        res = self.run_cli(["init", "--title", "E2E Test System"])
        self.assertEqual(res.returncode, 0)
        self.assertTrue((self.root / "docs" / "PROJECT_STRUCTURE.md").exists())
        self.assertTrue((self.root / ".agents" / ".virtual_company_board.json").exists())

        # 2. 执行 board 渲染空看板
        res = self.run_cli(["board"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("AEGISFLOW VIRTUAL STUDIO", res.stdout)

    def test_cli_full_task_lifecycle(self):
        """
        测试通过命令行完成工单全生命周期：
        创建 -> 领单研发 -> 提交审查 -> 质量打回 (#QR-1) -> 研发修复 -> 完成推进 -> 人类验收 -> 状态核验。
        """
        # 1. 初始化
        self.run_cli(["init"])

        # 2. 创建工单
        res = self.run_cli([
            "create",
            "--id", "TSK-8001",
            "--title", "Implement OAuth2 Flow",
            "--tier", "2",
            "--hours", "4.0",
            "--assignee", "pm"
        ])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Task created: TSK-8001", res.stdout)

        # 3. 领单开工
        res = self.run_cli([
            "start",
            "--id", "TSK-8001",
            "--role", "developer"
        ])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Work started on TSK-8001", res.stdout)

        # 4. 推进至代码评审
        res = self.run_cli([
            "advance",
            "--id", "TSK-8001",
            "--stage", "CODE_REVIEW",
            "--role", "code_reviewer",
            "--note", "Code submitted for PR"
        ])
        self.assertEqual(res.returncode, 0)
        self.assertIn("advanced to stage [CODE_REVIEW]", res.stdout)

        # 5. 代码审查员行使一票否决权打回
        res = self.run_cli([
            "reject",
            "--id", "TSK-8001",
            "--role", "code_reviewer",
            "--type", "QR",
            "--reason", "Missing unit tests for edge case"
        ])
        self.assertEqual(res.returncode, 0)
        self.assertIn("[VETO] Task TSK-8001 rejected", res.stdout)
        self.assertIn("TSK-8001#QR-1", res.stdout)

        # 6. 修复后推进至 COMPLETED 待验收
        res = self.run_cli([
            "advance",
            "--id", "TSK-8001",
            "--stage", "COMPLETED",
            "--role", "release_engineer"
        ])
        self.assertEqual(res.returncode, 0)

        # 7. 人类终审验收 (--yes 参数用于自动化测试免交互)
        res = self.run_cli([
            "accept",
            "--id", "TSK-8001",
            "--yes",
            "--note", "Verified in staging"
        ])
        self.assertEqual(res.returncode, 0)
        self.assertIn("[ACCEPTED] Task TSK-8001 successfully accepted", res.stdout)

        # 8. 状态与审计记录核验
        res = self.run_cli(["status", "--id", "TSK-8001"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("ACCEPTED", res.stdout)
        self.assertIn("TSK-8001#QR-1", res.stdout)

    def test_cli_lint_and_repomap(self):
        """
        测试 fast lint 代码快筛与 repomap 架构地图刷新子命令。
        """
        res = self.run_cli(["lint", "--target", str(self.cli_path)])
        self.assertEqual(res.returncode, 0)
        self.assertIn("[LINT PASS]", res.stdout)

        # 刷新 Repo Map
        self.run_cli(["init"])
        res = self.run_cli(["repomap"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("AST Repo Map refreshed", res.stdout)


if __name__ == "__main__":
    unittest.main()

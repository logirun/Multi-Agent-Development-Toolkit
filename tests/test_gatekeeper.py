"""
Unit tests for AegisFlow Gatekeeper (gatekeeper.py)
====================================================

验证六重质量门禁与安全防作弊逻辑：
- 契约文件 SHA256 签名计算与冻结判定 (Gate 1)。
- SWE-agent 风格快速 AST 语法快筛自测。
- Cline 风格角色最小权限物理隔离 (架构师禁写 src/、开发禁写 tests/、QA 禁写 src/)。
- Conventional Commits v1.0.0 提交格式与代码评审报告合规性 (Gate 2)。
- OWASP 漏洞与硬编码密钥扫描 (Gate 3, 安全一票否决权 #SR)。
- Living Documentation 代码与文档同步校验 (Gate 5, 文档一票否决权 #DR)。
- 密码学防篡改收据 (Cryptographic Receipts) 生成与签名校验。
"""

import json
import tempfile
import unittest
from pathlib import Path
from tools.gatekeeper import Gatekeeper


class TestGatekeeper(unittest.TestCase):
    """
    Gatekeeper 单元测试用例集。
    """

    def setUp(self):
        """
        初始化隔离临时目录与 Gatekeeper 实例。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.gatekeeper = Gatekeeper(root_dir=self.temp_dir.name)

    def tearDown(self):
        """
        清理临时目录。
        """
        self.temp_dir.cleanup()

    def test_hash_file(self):
        """
        测试 SHA256 文件哈希计算的确定性与输出长度。
        """
        test_file = self.root / "contract.json"
        test_file.write_text('{"api": "v1"}', encoding="utf-8")
        h1 = self.gatekeeper.hash_file(test_file)
        self.assertEqual(len(h1), 64)
        
        # 相同内容必须输出相同的 SHA256 摘要
        h2 = self.gatekeeper.hash_file(test_file)
        self.assertEqual(h1, h2)

    def test_fast_lint(self):
        """
        测试 SWE-agent 快速语法快筛：
        语法正确的代码快速通过，语法错误的代码精确捕获 SyntaxError 与行号。
        """
        good_file = self.root / "good.py"
        good_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
        passed, errors = self.gatekeeper.fast_lint(str(good_file.name))
        self.assertTrue(passed)
        self.assertEqual(errors, [])

        bad_file = self.root / "bad.py"
        bad_file.write_text("def broken(:\n    return 'broken'\n", encoding="utf-8")
        passed, errors = self.gatekeeper.fast_lint(str(bad_file.name))
        self.assertFalse(passed)
        self.assertTrue(any("Syntax Error" in e for e in errors))

    def test_check_role_permission(self):
        """
        测试 Cline 角色物理权限隔离：
        架构师禁写 src/，开发者禁写 tests/，测试员禁写 src/。
        """
        # 架构师严禁写入业务源码目录 src/
        allowed, msg = self.gatekeeper.check_role_permission("architect", "src/models/user.py")
        self.assertFalse(allowed)
        self.assertIn("Permission Denied", msg)

        # 开发者严禁修改测试用例 tests/（核心防作弊防线）
        allowed, msg = self.gatekeeper.check_role_permission("developer", "tests/unit/test_user.py")
        self.assertFalse(allowed)
        self.assertIn("Anti-Cheating", msg)

        # QA 工程师严禁直接修改 src/ 修复 bug
        allowed, msg = self.gatekeeper.check_role_permission("qa_engineer", "src/services/auth.py")
        self.assertFalse(allowed)
        self.assertIn("Permission Denied", msg)

        # 开发者合规写入业务代码
        allowed, msg = self.gatekeeper.check_role_permission("developer", "src/services/auth.py")
        self.assertTrue(allowed)

    def test_gate_1_contract(self):
        """
        测试 Gate 1 契约冻结逻辑与 SHA256 固化。
        """
        contract_file = self.root / "SPEC-001.json"
        contract_file.write_text('{"version": "1.0.0"}', encoding="utf-8")

        passed, msg, details = self.gatekeeper.check_gate_1_contract("TSK-101", str(contract_file.name))
        self.assertTrue(passed)
        self.assertIn("sha256_checksum", details)

        # 文件不存在时必须校验失败
        passed, msg, details = self.gatekeeper.check_gate_1_contract("TSK-101", "non_existent.json")
        self.assertFalse(passed)

    def test_gate_2_review(self):
        """
        测试 Gate 2 Conventional Commits 格式规范与评审报告标记。
        """
        # 合法的 Conventional Commit 格式
        passed, msg, _ = self.gatekeeper.check_gate_2_review("TSK-101", "feat(auth): support OAuth2 token refresh")
        self.assertTrue(passed)

        # 非法 Commit 格式必须被拦截
        passed, msg, _ = self.gatekeeper.check_gate_2_review("TSK-101", "WIP: fixed stuff")
        self.assertFalse(passed)
        self.assertIn("Conventional Commits Violation", msg)

        # 评审意见书通过判定
        review_file = self.root / "review.md"
        review_file.write_text("# Code Review\nSTATUS: PASS\nLooks great!", encoding="utf-8")
        passed, msg, _ = self.gatekeeper.check_gate_2_review(
            "TSK-101", "feat: add feature", review_file=str(review_file.name)
        )
        self.assertTrue(passed)

        # 评审意见书驳回判定
        review_file.write_text("# Code Review\nSTATUS: REJECT\nFound memory leak!", encoding="utf-8")
        passed, msg, _ = self.gatekeeper.check_gate_2_review(
            "TSK-101", "feat: add feature", review_file=str(review_file.name)
        )
        self.assertFalse(passed)

    def test_gate_3_security(self):
        """
        测试 Gate 3 安全扫描：拦截硬编码密钥（API Key/Token）及危险执行（eval/exec）。
        """
        src_dir = self.root / "src"
        src_dir.mkdir()

        # 安全合规源码文件
        (src_dir / "clean.py").write_text("PORT = 8080\n", encoding="utf-8")
        passed, msg, findings = self.gatekeeper.check_gate_3_security("TSK-101", target_dir="src")
        self.assertTrue(passed)
        self.assertEqual(len(findings), 0)

        # 包含硬编码敏感 Key 的代码文件
        (src_dir / "secret.py").write_text('API_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8")
        passed, msg, findings = self.gatekeeper.check_gate_3_security("TSK-101", target_dir="src")
        self.assertFalse(passed)
        self.assertTrue(any(f["type"] == "HARDCODED_SECRET" for f in findings))

        # 包含高危 eval 调用的代码文件
        (src_dir / "secret.py").unlink()
        (src_dir / "danger.py").write_text('eval(user_payload)\n', encoding="utf-8")
        passed, msg, findings = self.gatekeeper.check_gate_3_security("TSK-101", target_dir="src")
        self.assertFalse(passed)
        self.assertTrue(any(f["type"] == "INSECURE_EXEC" for f in findings))

    def test_gate_5_doc_sync(self):
        """
        测试 Gate 5 活文档同步：修改 API 路由必须同步更新文档。
        """
        # API 发生变动但缺少对应文档更新 -> 一票否决
        passed, msg = self.gatekeeper.check_gate_5_doc_sync(
            "TSK-101", ["src/api/users.py", "src/models/user.py"]
        )
        self.assertFalse(passed)
        self.assertIn("Doc Specialist VETO", msg)

        # 同步更新了文档 -> 门禁通过
        passed, msg = self.gatekeeper.check_gate_5_doc_sync(
            "TSK-101", ["src/api/users.py", "docs/api/users.md"]
        )
        self.assertTrue(passed)

    def test_issue_receipt(self):
        """
        测试密码学防篡改收据签发：
        验证收据生成、JSON 结构完整性及 signature_sha256 签名有效性。
        """
        receipt_rel = self.gatekeeper.issue_receipt(
            task_id="TSK-101",
            gate_key="g2_review",
            outcome=True,
            details={"commit": "feat: test", "reviewer": "code_reviewer"}
        )
        receipt_path = self.root / receipt_rel
        self.assertTrue(receipt_path.exists())

        with open(receipt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["task_id"], "TSK-101")
            self.assertEqual(data["outcome"], "PASS")
            self.assertIn("signature_sha256", data)

    def test_run_unified_qa_audit_pipeline(self):
        """
        测试质检审查小组 (qa_board) 统一质检流水线：
        规范 (AST+Commit) -> 安全 (SAST) -> 单测流水线递进校验。
        """
        src_dir = self.root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        py_file = src_dir / "app.py"
        py_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

        # 1. 提交信息不合规 -> 阻断于 Gate 2 (QR)
        passed, msg, meta = self.gatekeeper.run_unified_qa_audit(
            task_id="TSK-QA-1",
            commit_msg="bad commit msg"
        )
        self.assertFalse(passed)
        self.assertEqual(meta.get("veto_type"), "QR")
        self.assertIn("Conventional Commits Violation", msg)

        # 2. 引入安全隐患 -> 阻断于 Gate 3 (SR)
        vuln_file = src_dir / "vuln.py"
        vuln_file.write_text('API_KEY = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8")
        passed, msg, meta = self.gatekeeper.run_unified_qa_audit(
            task_id="TSK-QA-2",
            commit_msg="feat(core): add vuln script"
        )
        self.assertFalse(passed)
        self.assertEqual(meta.get("veto_type"), "SR")
        vuln_file.unlink()

        # 3. 补齐独立单元测试用例，执行全流水线 -> 生成综合质检报告与防篡改收据
        tests_dir = self.root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        test_file = tests_dir / "test_app.py"
        test_file.write_text(
            "import unittest\n\n"
            "class TestApp(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8"
        )

        passed, msg, meta = self.gatekeeper.run_unified_qa_audit(
            task_id="TSK-QA-3",
            commit_msg="feat(core): add add function"
        )
        self.assertTrue(passed, f"Expected pass, got: {msg}")
        self.assertTrue(meta["receipt_file"].endswith(".json"))
        verify_doc = self.root / "docs" / "qa" / "VERIFY-TSK-QA-3.md"
        self.assertTrue(verify_doc.exists())
        self.assertIn("综合质检评估报告", verify_doc.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

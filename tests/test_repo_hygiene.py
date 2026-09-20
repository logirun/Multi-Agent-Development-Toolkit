"""
Unit tests for AegisFlow RepoHygieneGuard (repo_hygiene.py)
============================================================

验证代码库整洁度与脚手架防御逻辑：
- 根目录白名单零污染检查（拦截游离脚本与非法目录）。
- 生产代码与测试代码 1:1 镜像一致性检测 (Test-Mirror Consistency)。
- 防目录无限递归嵌套层级深度限制。
- 基于 AST 的 Aider 风格代码架构地图 (Repo Map) 自动化生成。
- 标准目录脚手架初始化与 .gitignore 自动补全。
"""

import tempfile
import unittest
from pathlib import Path
from tools.repo_hygiene import RepoHygieneGuard


class TestRepoHygieneGuard(unittest.TestCase):
    """
    RepoHygieneGuard 单元测试用例集。
    """

    def setUp(self):
        """
        初始化隔离的临时工作目录与 Guard 实例。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.guard = RepoHygieneGuard(root_dir=self.temp_dir.name)

    def tearDown(self):
        """
        清理临时目录。
        """
        self.temp_dir.cleanup()

    def test_root_cleanliness_clean_state(self):
        """
        测试标准工程目录结构下的根目录检查（预期 0 违规）。
        """
        (self.root / "README.md").touch()
        (self.root / ".gitignore").touch()
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "docs").mkdir()
        (self.root / "tools").mkdir()
        (self.root / ".agents").mkdir()

        violations = self.guard.check_root_cleanliness()
        self.assertEqual(violations, [])

    def test_root_cleanliness_stray_file_and_directory(self):
        """
        测试根目录游离临时脚本与非白名单目录拦截。
        """
        (self.root / "rogue_script.py").touch()
        (self.root / "random_scratch").mkdir()

        violations = self.guard.check_root_cleanliness()
        self.assertEqual(len(violations), 2)
        self.assertTrue(any("[ROOT POLLUTION]" in v and "rogue_script.py" in v for v in violations))
        self.assertTrue(any("[ILLEGAL DIRECTORY]" in v and "random_scratch" in v for v in violations))

    def test_test_mirror_consistency(self):
        """
        测试代码-测试镜像一致性检测：
        当 src/ 下新增业务代码但缺少对应 tests/test_*.py 时必须报警，补齐后报警消除。
        """
        src_dir = self.root / "src"
        tests_dir = self.root / "tests"
        src_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        # 1. 只有业务代码没有对应测试 -> 触发 [TEST GAP] 告警
        (src_dir / "payment_gateway.py").write_text("def pay(): pass\n", encoding="utf-8")
        violations = self.guard.check_test_mirror_consistency()
        self.assertEqual(len(violations), 1)
        self.assertIn("[TEST GAP]", violations[0])
        self.assertIn("payment_gateway.py", violations[0])

        # 2. 补全测试镜像文件 -> 告警自动消除
        (tests_dir / "test_payment_gateway.py").write_text("import unittest\n", encoding="utf-8")
        violations = self.guard.check_test_mirror_consistency()
        self.assertEqual(violations, [])

    def test_check_directory_depth(self):
        """
        测试目录层级深度检测：防止 Agent 幻觉引发深层目录套娃。
        """
        # 3 层目录（小于等于 4 层限制，合规）
        shallow = self.root / "src" / "services" / "payment"
        shallow.mkdir(parents=True)
        (shallow / "stripe.py").touch()

        violations = self.guard.check_directory_depth(max_depth=4)
        self.assertEqual(violations, [])

        # 6 层嵌套目录（超出 4 层限制，违规报警）
        deep = self.root / "src" / "a" / "b" / "c" / "d" / "e"
        deep.mkdir(parents=True)
        (deep / "deep_file.py").touch()

        violations = self.guard.check_directory_depth(max_depth=4)
        self.assertTrue(any("[EXCESSIVE DEPTH]" in v for v in violations))

    def test_generate_repo_map(self):
        """
        测试 AST Repo Map 生成：验证类名、方法名及入参是否被精确提取并格式化输出。
        """
        src_dir = self.root / "src"
        src_dir.mkdir(parents=True)
        code = '''
class OrderProcessor:
    def process_order(self, order_id, amount):
        pass
    def refund(self, order_id):
        pass

def calculate_tax(subtotal, rate):
    return subtotal * rate
'''
        (src_dir / "orders.py").write_text(code, encoding="utf-8")
        rel_path = self.guard.generate_repo_map()
        self.assertEqual(rel_path.replace("\\", "/"), "docs/PROJECT_STRUCTURE.md")

        content = (self.root / "docs" / "PROJECT_STRUCTURE.md").read_text(encoding="utf-8")
        self.assertIn("# AegisFlow Codebase Architecture Map", content)
        self.assertIn("class OrderProcessor(process_order, refund)", content)
        self.assertIn("def calculate_tax(subtotal, rate)", content)

    def test_init_scaffolding(self):
        """
        测试脚手架初始化方法：验证 docs/, src/, tests/, tools/ 等目录和 .gitignore 正确建立。
        """
        created = self.guard.init_scaffolding()
        
        # 验证核心目录存在性
        self.assertTrue((self.root / "docs" / "specs").exists())
        self.assertTrue((self.root / "docs" / "adr").exists())
        self.assertTrue((self.root / "docs" / "contracts").exists())
        self.assertTrue((self.root / "src").exists())
        self.assertTrue((self.root / "tests" / "unit").exists())
        self.assertTrue((self.root / "tools").exists())
        self.assertTrue((self.root / ".agents" / "receipts").exists())

        # 验证基础文件
        self.assertTrue((self.root / ".gitignore").exists())
        self.assertTrue((self.root / "docs" / "PROJECT_STRUCTURE.md").exists())


if __name__ == "__main__":
    unittest.main()

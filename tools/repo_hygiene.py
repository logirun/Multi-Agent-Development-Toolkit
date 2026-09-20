"""
AegisFlow Repository Scaffolding & Hygiene Guard (repo_hygiene.py)
==================================================================

负责强制执行根目录零污染白名单策略、测试镜像一致性检测 (Test Mirror Consistency)、
防目录无限递归、以及基于 AST 自动生成 Aider 风格的代码架构全景地图 (Repo Map)。
"""

import os
import sys
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 根目录允许存在的白名单文件（不区分大小写比较）
ROOT_WHITELIST_FILES = {
    "readme.md",
    "changelog.md",
    "license",
    "license.md",
    "license.txt",
    ".gitignore",
    ".gitattributes",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "tsconfig.json",
    "docker-compose.yml",
    "dockerfile",
    ".env.example"
}

# 根目录下允许存在的标准子目录
ALLOWED_ROOT_DIRS = {
    "docs",
    "src",
    "tests",
    "tools",
    "scripts",
    ".agents",
    ".git",
    ".github",
    ".scratch",
    "deploy",
    "public",
    "static",
    "assets",
    "dist",
    "build",
    "node_modules"
}


class RepoHygieneGuard:
    """
    仓库清洁度与工程脚手架卫士。
    负责检测违规临时散落文件、确保测试用例与生产代码 1:1 配套、生成代码架构地图。
    """

    def __init__(self, root_dir: str = "."):
        """
        初始化卫生守卫。

        :param root_dir: 仓库根目录路径
        """
        self.root_dir = Path(root_dir).resolve()

    def check_root_cleanliness(self) -> List[str]:
        """
        核验根目录清洁度，拦截随手创建在根目录的游离脚本或未知目录。
        除明确白名单（如 README.md, .gitignore）外，业务代码必须严格收拢在 src/，测试在 tests/，文档在 docs/。

        :return: 发现的根目录污染告警列表
        """
        violations = []
        for item in self.root_dir.iterdir():
            name_lower = item.name.lower()
            if item.is_file():
                if name_lower not in ROOT_WHITELIST_FILES and not name_lower.startswith("."):
                    violations.append(
                        f"[ROOT POLLUTION] Stray file in root: '{item.name}'. "
                        "All source code belongs in 'src/', tests in 'tests/', docs in 'docs/'."
                    )
            elif item.is_dir():
                if item.name not in ALLOWED_ROOT_DIRS and not item.name.startswith("."):
                    violations.append(
                        f"[ILLEGAL DIRECTORY] Unauthorized root directory: '{item.name}'. "
                        f"Allowed standard directories: {sorted(list(ALLOWED_ROOT_DIRS))}"
                    )
        return violations

    def check_test_mirror_consistency(self) -> List[str]:
        """
        测试镜像一致性检测 (Test-Mirror Consistency)。
        验证 src/ 下所有业务 Python 文件（排除 __init__.py）是否在 tests/ 下存在对应命名的 test_*.py。
        防止开发者盲目编写功能代码却遗漏配套自动化测试。

        :return: 测试缺失违规列表
        """
        src_dir = self.root_dir / "src"
        tests_dir = self.root_dir / "tests"
        
        if not src_dir.exists():
            return []
        
        violations = []
        for file in src_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            rel_path = file.relative_to(src_dir)
            expected_test_name = f"test_{file.name}"
            
            # 在 tests/ 树中搜索是否存在同名测试文件
            has_test = False
            for test_file in tests_dir.rglob("test_*.py"):
                if test_file.name == expected_test_name:
                    has_test = True
                    break
            
            if not has_test:
                violations.append(
                    f"[TEST GAP] Source file 'src/{rel_path}' lacks corresponding mirror test '{expected_test_name}' in 'tests/'."
                )
        return violations

    def check_directory_depth(self, max_depth: int = 4) -> List[str]:
        """
        目录层级深度防幻觉守卫。
        防止自主 Agent 因上下文失控陷入无休止递归，创建例如 src/a/b/c/d/e/f/g/ 的畸形深度结构。
        系统隐藏目录（如 .agents）自动跳过。

        :param max_depth: 允许的最大子目录嵌套层级 (默认 4)
        :return: 超出深度限制的路径违规列表
        """
        violations = []
        ignored_dir_names = {
            ".git", ".agents", ".next", ".cache", ".idea", ".vscode",
            "node_modules", "dist", "build", "coverage", "__pycache__", ".venv", "venv"
        }
        for path in self.root_dir.rglob("*"):
            if any(part.startswith(".") or part.lower() in ignored_dir_names for part in path.parts):
                continue
            rel_parts = path.relative_to(self.root_dir).parts
            if len(rel_parts) > max_depth:
                violations.append(
                    f"[EXCESSIVE DEPTH] Path exceeds {max_depth} levels: '{path.relative_to(self.root_dir)}'."
                )
        return violations

    def generate_repo_map(self) -> str:
        """
        Aider 风格 AST 代码架构地图生成器。
        使用 Python 原生 ast 模块扫描 src/ 与 tools/ 下所有源码文件，
        提取类名、成员函数名、全局函数名及入参概要，聚合成紧凑且信息密度极高的代码地图，
        写入 docs/PROJECT_STRUCTURE.md 供后续 Agent 进行全局架构感知。

        :return: 生成的 docs/PROJECT_STRUCTURE.md 相对文件路径
        """
        lines = [
            "# AegisFlow Codebase Architecture Map (Repo Map)",
            f"# Generated via AST Analysis | Root: {self.root_dir.name}",
            ""
        ]

        target_dirs = ["src", "tools"]
        for tdir_name in target_dirs:
            tdir = self.root_dir / tdir_name
            if not tdir.exists():
                continue

            lines.append(f"## /{tdir_name}")
            for py_file in sorted(tdir.rglob("*.py")):
                rel_path = py_file.relative_to(self.root_dir)
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=str(py_file))
                    
                    symbols = []
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            # 提取类中定义的函数与方法列表
                            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                            methods_str = f"({', '.join(methods[:5])}{'...' if len(methods)>5 else ''})" if methods else ""
                            symbols.append(f"class {node.name}{methods_str}")
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # 提取独立函数及关键入参
                            args = [a.arg for a in node.args.args if a.arg != "self"]
                            symbols.append(f"def {node.name}({', '.join(args[:3])}{'...' if len(args)>3 else ''})")

                    if symbols:
                        lines.append(f"- `{rel_path}`:")
                        for s in symbols[:8]:
                            lines.append(f"    • {s}")
                except Exception:
                    lines.append(f"- `{rel_path}` (unparseable)")
            lines.append("")

        output_content = "\n".join(lines)
        docs_dir = self.root_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        repo_map_file = docs_dir / "PROJECT_STRUCTURE.md"
        with open(repo_map_file, "w", encoding="utf-8") as f:
            f.write(output_content)
        return str(repo_map_file.relative_to(self.root_dir))

    def init_scaffolding(self) -> List[str]:
        """
        初始化 AegisFlow 标准工程脚手架目录结构。
        按需创建 docs/ (specs, adr, contracts, api, reviews, security, qa), src/, tests/,
        tools/, .agents/ 等目录，并补齐基础 .gitignore 条目。

        :return: 新创建的目录与文件路径列表
        """
        created = []
        standard_dirs = [
            self.root_dir / "docs" / "specs",
            self.root_dir / "docs" / "adr",
            self.root_dir / "docs" / "contracts",
            self.root_dir / "docs" / "api",
            self.root_dir / "docs" / "reviews",
            self.root_dir / "docs" / "security",
            self.root_dir / "docs" / "qa",
            self.root_dir / "src",
            self.root_dir / "tests" / "unit",
            self.root_dir / "tests" / "integration",
            self.root_dir / "tools",
            self.root_dir / ".agents" / "receipts",
            self.root_dir / ".agents" / "knowledge",
            self.root_dir / ".scratch"
        ]
        for d in standard_dirs:
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                created.append(str(d.relative_to(self.root_dir)))

        gitignore_path = self.root_dir / ".gitignore"
        gitignore_entries = [
            ".scratch/",
            "*.tmp",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            ".coverage"
        ]
        if not gitignore_path.exists():
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("\n".join(gitignore_entries) + "\n")
            created.append(".gitignore")
        else:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()
            missing = [e for e in gitignore_entries if e not in content]
            if missing:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n# AegisFlow hygiene\n" + "\n".join(missing) + "\n")

        self.generate_repo_map()
        return created

    def run_full_scan(self) -> Dict[str, Any]:
        """
        运行仓库卫生全面扫描（聚合根目录清洁度、测试镜像与目录深度）。

        :return: 包含扫描结论与违规清单的字典
        """
        root_violations = self.check_root_cleanliness()
        test_violations = self.check_test_mirror_consistency()
        depth_violations = self.check_directory_depth()
        all_violations = root_violations + test_violations + depth_violations
        return {
            "passed": len(all_violations) == 0,
            "total_violations": len(all_violations),
            "root_violations": root_violations,
            "test_violations": test_violations,
            "depth_violations": depth_violations
        }

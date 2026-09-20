"""
AegisFlow Project Tech-Stack Sniffer (stack_sniffer.py)
======================================================

负责自动嗅探当前工作区的技术栈架构（编程语言、包管理器、测试运行器、构建工具），
输出标准化项目画像 (.agents/project_profile.json)，使 Gate 4 自动化测试门禁与语法快筛
能够自适应多语言生态（Python, Node.js/TS, Go, Rust, Java 等），避免命令硬编码。
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DEFAULT_PROFILE_FILE = Path(".agents") / "project_profile.json"


class StackSniffer:
    """
    自适应技术栈探测器与项目架构嗅探引擎。
    """

    def __init__(self, root_dir: str = "."):
        """
        初始化探测器。

        :param root_dir: 项目根目录绝对或相对路径
        """
        self.root_dir = Path(root_dir).resolve()
        self.profile_path = self.root_dir / DEFAULT_PROFILE_FILE

    def sniff(self) -> Dict[str, Any]:
        """
        扫描工作区特征文件与标识，推导出当前项目的多语言技术栈画像。

        :return: 包含主语言、依赖清单、默认测试命令与构建命令的画像字典
        """
        languages = []
        frameworks = []
        test_commands = []
        lint_commands = []
        build_commands = []

        # 1. Python 生态特征探测
        is_python = any((self.root_dir / f).exists() for f in [
            "requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock"
        ]) or list(self.root_dir.glob("*.py")) or (self.root_dir / "src").exists()
        if is_python:
            languages.append("Python")
            # 探测测试框架：优先 pytest，兜底 unittest
            if (self.root_dir / "pytest.ini").exists() or (self.root_dir / "tests").exists():
                test_commands.append("python -m unittest discover tests")
            else:
                test_commands.append("python -m unittest")
            lint_commands.append("python tools/vc_cli.py lint --target src")

        # 2. Node.js / TypeScript 生态探测
        package_json = self.root_dir / "package.json"
        if package_json.exists():
            languages.append("JavaScript/TypeScript")
            try:
                with open(package_json, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                    scripts = pkg_data.get("scripts", {})
                    if "test" in scripts:
                        test_commands.append("npm test")
                    if "build" in scripts:
                        build_commands.append("npm run build")
                    if "lint" in scripts:
                        lint_commands.append("npm run lint")
                    
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    if "react" in deps: frameworks.append("React")
                    if "vue" in deps: frameworks.append("Vue")
                    if "next" in deps: frameworks.append("Next.js")
                    if "express" in deps: frameworks.append("Express")
            except Exception:
                test_commands.append("npm test")

        # 3. Go 生态探测
        if (self.root_dir / "go.mod").exists():
            languages.append("Go")
            test_commands.append("go test ./...")
            build_commands.append("go build ./...")

        # 4. Rust 生态探测
        if (self.root_dir / "Cargo.toml").exists():
            languages.append("Rust")
            test_commands.append("cargo test")
            build_commands.append("cargo build")

        # 5. Java / Kotlin 生态探测
        if (self.root_dir / "pom.xml").exists():
            languages.append("Java (Maven)")
            test_commands.append("mvn test")
            build_commands.append("mvn clean compile")
        elif (self.root_dir / "build.gradle").exists() or (self.root_dir / "build.gradle.kts").exists():
            languages.append("Java/Kotlin (Gradle)")
            test_commands.append("./gradlew test")
            build_commands.append("./gradlew build")

        # 确定主语言与主测试命令
        primary_lang = languages[0] if languages else "Generic / Unknown"
        default_test_cmd = test_commands[0] if test_commands else "python -m unittest"
        default_lint_cmd = lint_commands[0] if lint_commands else ""
        default_build_cmd = build_commands[0] if build_commands else ""

        profile = {
            "project_name": self.root_dir.name,
            "detected_languages": languages,
            "primary_language": primary_lang,
            "frameworks": frameworks,
            "default_test_command": default_test_cmd,
            "default_lint_command": default_lint_cmd,
            "default_build_command": default_build_cmd,
            "has_src_dir": (self.root_dir / "src").is_dir(),
            "has_tests_dir": (self.root_dir / "tests").is_dir(),
            "has_docs_dir": (self.root_dir / "docs").is_dir(),
        }
        return profile

    def save_profile(self, target_file: Optional[Path] = None) -> Path:
        """
        保存技术栈画像至 JSON 文件中。

        :param target_file: 目标写入路径 (可选，默认 .agents/project_profile.json)
        :return: 写入成功的 Path 路径
        """
        profile = self.sniff()
        dest = target_file or self.profile_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        return dest

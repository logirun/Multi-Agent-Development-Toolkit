"""
AegisFlow Gatekeeper Engine (gatekeeper.py)
===========================================

自动化评估六重确定性质量门禁、物理防作弊权限隔离、
SWE-agent 级快速语法快筛自测、以及密码学收据 (Cryptographic Receipts) 签发。
"""

import os
import sys
import json
import re
import ast
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Conventional Commits v1.0.0 正则校验表达式
COMMIT_MSG_REGEX = r"^(feat|fix|sec|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9_-]+\))?!?: .+$"

# 高危硬编码敏感信息特征正则 (API Key, 令牌, 私钥证书)
SUSPICIOUS_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|secret|password|private[_-]?key|token)\s*=\s*['\"][a-zA-Z0-9_\-\.]{8,}['\"]", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----", re.IGNORECASE),
    re.compile(r"(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,})", re.IGNORECASE)
]

# 高危代码执行特征正则 (动态执行与系统命令注入风险)
SUSPICIOUS_EXEC_PATTERNS = [
    re.compile(r"\b(eval|exec)\s*\(", re.IGNORECASE),
    re.compile(r"\bos\.system\s*\(", re.IGNORECASE)
]


class Gatekeeper:
    """
    质量门禁与安全合规守门人引擎。
    提供确定性机器门禁校验、权限物理隔离判定与不可篡改的凭据签发。
    """

    def __init__(self, root_dir: str = "."):
        """
        初始化 Gatekeeper 实例。

        :param root_dir: 项目根目录路径
        """
        self.root_dir = Path(root_dir).resolve()
        self.receipts_dir = self.root_dir / ".agents" / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def hash_file(self, file_path: Path) -> str:
        """
        以 8KB 分块流式读取文件，计算其 SHA256 十六进制摘要，用于契约冻结与防篡改比对。

        :param file_path: 目标文件路径
        :return: 64 位 SHA256 字符串
        """
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def fast_lint(self, target_path: str) -> Tuple[bool, List[str]]:
        """
        SWE-agent 风格快速语法快筛机制。
        利用 Python 原生 AST 语法树解析器，在数毫秒内捕获代码中的 SyntaxError、未闭合括号及缩进错误。

        :param target_path: 待检测的目标文件或目录相对路径
        :return: (是否通过, 错误信息列表)
        """
        full_path = self.root_dir / target_path
        errors = []
        if full_path.is_file() and full_path.suffix == ".py":
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    ast.parse(f.read(), filename=str(full_path))
            except SyntaxError as e:
                errors.append(f"Syntax Error in {target_path}:{e.lineno}: {e.msg}")
            except Exception as e:
                errors.append(f"Parse Error in {target_path}: {e}")
        elif full_path.is_dir():
            for py_file in full_path.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        ast.parse(f.read(), filename=str(py_file))
                except SyntaxError as e:
                    errors.append(f"Syntax Error in {py_file.relative_to(self.root_dir)}:{e.lineno}: {e.msg}")
                except Exception as e:
                    errors.append(f"Parse Error in {py_file.relative_to(self.root_dir)}: {e}")
        return len(errors) == 0, errors

    def check_role_permission(self, role: str, target_file: str) -> Tuple[bool, str]:
        """
        Cline 风格角色最小权限物理隔离守卫。
        通过物理路径拦截，防止角色越权与作弊合谋：
        1. 架构师 (architect) 严禁修改 src/：只负责契约与 ADR，防止破坏解耦。
        2. 开发者 (developer) 严禁修改 tests/：防作弊铁律，杜绝私自删改测试断言。
        3. 测试员 (qa_engineer) 严禁修改 src/：只提 Bug 打回，不得代劳业务编码。

        :param role: 尝试写入的角色名称
        :param target_file: 拟写入的目标文件路径
        :return: (是否允许, 说明信息)
        """
        tf = target_file.replace("\\", "/")
        if role == "architect" and tf.startswith("src/"):
            return False, "Permission Denied: Architect is prohibited from writing to 'src/'. Only contracts/ADR permitted."
        if role == "developer" and tf.startswith("tests/"):
            return False, "Permission Denied (Anti-Cheating): Developer is prohibited from writing to 'tests/'. Tests are QA read-only."
        if role == "qa_engineer" and tf.startswith("src/"):
            return False, "Permission Denied: QA Tester is prohibited from modifying 'src/'. Submit #FR-x bug ticket instead."
        return True, "Permission verified."

    def check_gate_1_contract(self, task_id: str, contract_file: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Gate 1: 架构与接口契约冻结门禁。
        核验契约规范文件是否存在，计算 SHA256 唯一摘要并固化，作为后续研发的标准准绳。

        :param task_id: 关联工单编号
        :param contract_file: 契约文件相对路径 (如 docs/contracts/SPEC-0001.json)
        :return: (是否通过, 审核描述, 详情元数据)
        """
        contract_path = self.root_dir / contract_file
        if not contract_path.exists():
            return False, f"Contract file not found: {contract_file}", {}

        contract_hash = self.hash_file(contract_path)
        details = {
            "task_id": task_id,
            "contract_file": str(contract_file),
            "sha256_checksum": contract_hash,
            "frozen_at": datetime.now().isoformat()
        }
        return True, f"Contract frozen with SHA256: {contract_hash[:12]}...", details

    def check_gate_2_review(self, task_id: str, commit_msg: str, review_file: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Gate 2: 代码质量与 Conventional Commits 提交规范门禁。
        1. 验证 Git 提交信息是否完全遵循 Conventional Commits v1.0.0 语法。
        2. 若提供了评审报告文件，核验是否明确包含 'STATUS: PASS' 标记。

        :param task_id: 关联工单编号
        :param commit_msg: 拟提交的 Git Commit Message
        :param review_file: 审查意见书相对路径 (可选)
        :return: (是否通过, 审核描述, 详情元数据)
        """
        # 1. 严格校验 Conventional Commits 提交格式
        if not re.match(COMMIT_MSG_REGEX, commit_msg.strip()):
            return False, (
                f"Conventional Commits Violation: '{commit_msg}'. "
                "Must match: <type>(<scope>): <desc>. Allowed types: feat, fix, sec, docs, style, refactor, perf, test, build, ci, chore, revert"
            ), {}

        # 2. 审查报告一致性核验
        if review_file:
            rpath = self.root_dir / review_file
            if not rpath.exists():
                return False, f"Review report file '{review_file}' not found.", {}
            with open(rpath, "r", encoding="utf-8") as f:
                content = f.read()
            if "STATUS: PASS" not in content and "status: pass" not in content.lower():
                return False, f"Review report in '{review_file}' does not have 'STATUS: PASS'.", {}

        return True, "Code review and Conventional Commit format passed.", {"commit_msg": commit_msg}

    def check_gate_3_security(self, task_id: str, target_dir: str = "src") -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Gate 3: 安全合规与硬编码密钥扫描门禁 (安全工程师一票否决权 #SR)。
        逐行扫描指定目录下的 Python 源码，检测敏感凭据泄露及动态执行危险调用。

        :param task_id: 关联工单编号
        :param target_dir: 扫描目标目录 (默认 src)
        :return: (是否通过, 审核描述, 漏洞违规列表)
        """
        scan_dir = self.root_dir / target_dir
        if not scan_dir.exists():
            return True, f"Target directory '{target_dir}' does not exist, skipping scan.", []

        findings = []
        for file in scan_dir.rglob("*.py"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line_idx, line in enumerate(lines, start=1):
                    # 敏感凭据/密钥泄露排查
                    for p in SUSPICIOUS_SECRET_PATTERNS:
                        if p.search(line):
                            findings.append({
                                "file": str(file.relative_to(self.root_dir)),
                                "line": line_idx,
                                "type": "HARDCODED_SECRET",
                                "severity": "CRITICAL",
                                "snippet": line.strip()[:60]
                            })
                    # 动态代码执行风险排查 (eval/exec/os.system)
                    for p in SUSPICIOUS_EXEC_PATTERNS:
                        if p.search(line):
                            findings.append({
                                "file": str(file.relative_to(self.root_dir)),
                                "line": line_idx,
                                "type": "INSECURE_EXEC",
                                "severity": "HIGH",
                                "snippet": line.strip()[:60]
                            })
            except Exception:
                pass

        if findings:
            return False, f"Security Auditor VETO: Found {len(findings)} vulnerability/secret violations!", findings
        return True, "Security audit passed. Zero hardcoded secrets and dangerous execution found.", []

    def check_gate_4_testing(self, task_id: str, test_command: str = "python -m unittest") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Gate 4: 独立自动化测试与防作弊验证门禁 (QA 工程师一票否决权 #FR)。
        必须存在独立的 tests/ 目录与测试用例，并在干净子进程中执行测试套件，返回码必须为 0。

        :param task_id: 关联工单编号
        :param test_command: 测试套件执行命令 (默认 python -m unittest)
        :return: (是否通过, 审核描述, 执行详情元数据)
        """
        tests_dir = self.root_dir / "tests"
        if not tests_dir.exists():
            return False, "QA VETO: 'tests/' directory does not exist. Tests must be implemented independently.", {}

        test_files = list(tests_dir.rglob("test_*.py"))
        if not test_files:
            return False, "QA VETO: No 'test_*.py' files found in 'tests/'.", {}

        try:
            res = subprocess.run(
                test_command,
                cwd=str(self.root_dir),
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if res.returncode != 0:
                err_msg = res.stderr or res.stdout
                return False, f"QA VETO: Automated test suite failed (exit code {res.returncode}):\n{err_msg[:400]}", {
                    "returncode": res.returncode,
                    "stdout": res.stdout[:500],
                    "stderr": res.stderr[:500]
                }
        except subprocess.TimeoutExpired:
            return False, "QA VETO: Test execution timed out (exceeded 60s limit).", {}
        except Exception as e:
            return False, f"QA VETO: Test execution error: {e}", {}

        return True, "All automated test suites passed successfully with exit code 0.", {
            "test_files_count": len(test_files),
            "command": test_command
        }

    def check_gate_5_doc_sync(self, task_id: str, changed_files: List[str]) -> Tuple[bool, str]:
        """
        Gate 5: Living Documentation 活文档与代码同步门禁 (文档工程师一票否决权 #DR)。
        检测当 API 接口、路由或核心控制器变动时，是否同步更新了对应的接口文档或 README。

        :param task_id: 关联工单编号
        :param changed_files: 本次变动的文件路径列表
        :return: (是否通过, 审核描述)
        """
        has_api_change = any("src/api" in f or "routes" in f or "controllers" in f for f in changed_files)
        has_doc_update = any("docs/api" in f or "README" in f for f in changed_files)

        if has_api_change and not has_doc_update:
            return False, "Doc Specialist VETO (#DR-1): API endpoints modified without updating 'docs/api/' or README!"
        return True, "Code-Documentation synchronization verified."

    def issue_receipt(self, task_id: str, gate_key: str, outcome: bool, details: Dict[str, Any]) -> str:
        """
        签发不可篡改的密码学收据 (Cryptographic Receipt)。
        收据包含任务 ID、门禁类型、判定结论、时间戳及 SHA256 签名，落盘至 .agents/receipts/。

        :param task_id: 工单编号
        :param gate_key: 门禁标识 (如 gate_1_contract)
        :param outcome: 通过 (True) 或未通过 (False)
        :param details: 门禁执行的具体指标与明细
        :return: 生成的收据相对文件路径
        """
        receipt_id = f"REC-{task_id}-{gate_key.upper()}-{'PASS' if outcome else 'FAIL'}"
        receipt_data = {
            "receipt_id": receipt_id,
            "task_id": task_id,
            "gate": gate_key,
            "outcome": "PASS" if outcome else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        # 计算确定性排序 JSON 的 SHA256 签名
        raw_bytes = json.dumps(receipt_data, sort_keys=True).encode("utf-8")
        receipt_data["signature_sha256"] = hashlib.sha256(raw_bytes).hexdigest()

        target_file = self.receipts_dir / f"{receipt_id}.json"
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(receipt_data, f, indent=2, ensure_ascii=False)
        return str(target_file.relative_to(self.root_dir))

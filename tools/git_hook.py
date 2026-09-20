# -*- coding: utf-8 -*-
"""
==============================================================================
AegisFlow Git 物理门禁守卫 (git_hook.py)
==============================================================================
负责在本地代码仓库的 .git/hooks/pre-commit 中安装物理级硬拦截脚本，
强制将两大核心工程红线落地为系统物理约束：
1. 拦截脱离工单的代码提交：看板中无任何活跃研发工单时，硬性阻断 git commit。
2. 拦截根目录散落文件：根目录下存在非白名单临时脚本或杂物时，硬性阻断提交。
==============================================================================
"""

import os
import sys
import stat
from pathlib import Path
from typing import Tuple, Dict, Any

HOOK_SCRIPT_CONTENT = """#!/bin/sh
# AegisFlow Git Pre-Commit 物理硬门禁脚本
# 由 AegisFlow 统一管理脚手架自动生成 (python tools/vc_cli.py hook install)

# 动态探测宿主环境中的 Python 命令解释器
if command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    echo "❌ [神盾物理门禁] 在环境变量 PATH 中未找到 python 或 python3 执行环境！"
    exit 1
fi

$PYTHON_CMD tools/vc_cli.py hook verify
STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo "🚫 [神盾物理门禁] Pre-commit 检查未通过！提交已被物理拦截 (Commit aborted)。"
    exit 1
fi

exit 0
"""


class GitHookManager:
    """
    Git 物理门禁钩子安装、卸载与校验管理器。
    """

    def __init__(self, root_dir: str = "."):
        """
        初始化钩子管理器。

        :param root_dir: 项目根目录绝对或相对路径
        """
        self.root_dir = Path(root_dir).resolve()
        self.git_dir = self.root_dir / ".git"
        self.hook_file = self.git_dir / "hooks" / "pre-commit"

    def install_hook(self) -> Tuple[bool, str]:
        """
        向 .git/hooks/pre-commit 写入物理防护门禁脚本，并赋予可执行权限 (chmod +x)。

        :return: (是否安装成功, 说明信息)
        """
        if not self.git_dir.exists():
            return False, "非 Git 代码仓库：未找到 '.git' 目录。请先在项目根目录下执行 'git init'。"

        hooks_dir = self.git_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.hook_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(HOOK_SCRIPT_CONTENT)

            # 赋予所有者与组可执行权限 (chmod +x)
            current_stat = self.hook_file.stat().st_mode
            self.hook_file.chmod(current_stat | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return True, f"Git pre-commit 物理门禁钩子安装成功: {self.hook_file}"
        except Exception as e:
            return False, f"安装 pre-commit 门禁钩子失败: {e}"

    def uninstall_hook(self) -> Tuple[bool, str]:
        """
        卸载并安全移除 .git/hooks/pre-commit 脚本。

        :return: (是否卸载成功, 说明信息)
        """
        if self.hook_file.exists():
            try:
                self.hook_file.unlink()
                return True, "Git pre-commit 物理门禁钩子已成功卸载。"
            except Exception as e:
                return False, f"移除钩子文件失败: {e}"
        return True, "当前未安装任何 pre-commit 钩子文件。"

    def verify_pre_commit(self, state_manager=None, hygiene_guard=None) -> Tuple[bool, str]:
        """
        执行 pre-commit 物理级安全核验逻辑：
        1. 检查看板中是否存在至少 1 个处于活跃状态的工单 (IN_PROGRESS, CODE_REVIEW, TESTING, DOC_SYNC, COMPLETED)。
           若无活跃任务，判定为“无工单盲目代码提交”，物理拒绝。
        2. 扫描仓库根目录是否存在游离污染文件。

        :param state_manager: StateManager 实例 (可选)
        :param hygiene_guard: RepoHygieneGuard 实例 (可选)
        :return: (是否放行, 说明信息)
        """
        from tools.state_manager import StateManager
        from tools.repo_hygiene import RepoHygieneGuard

        sm = state_manager or StateManager(root_dir=str(self.root_dir))
        hyg = hygiene_guard or RepoHygieneGuard(root_dir=str(self.root_dir))

        # 1. 活跃工单物理核验（无工单不 Git）
        active_tasks = sm.list_tasks(active_only=True)
        if not active_tasks:
            return False, (
                "🚫 [权限拒绝] 未在 AegisFlow 看板中检测到任何处于活跃状态的研发工单 (No active task card found)！\n"
                "🛡️ 核心红线：“无工单不 Git”。严禁脱离工单进行盲目代码提交。\n"
                "请先建单领单：python tools/vc_cli.py create --id TSK-xxxx --title \"...\""
            )

        # 2. 根目录零污染物理核验
        root_violations = hyg.check_root_cleanliness()
        if root_violations:
            violation_details = "\n".join(f"  - {v}" for v in root_violations[:3])
            return False, f"⚠️ [仓库整洁度违规] 根目录下发现非白名单散落游离文件 (Cleanliness Violation: Stray files in root directory):\n{violation_details}"

        return True, f"✅ Pre-commit 物理门禁核验通过 (Pre-commit verified)。当前活跃工单数: {len(active_tasks)}，根目录洁净无污染。"

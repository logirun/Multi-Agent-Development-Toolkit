# -*- coding: utf-8 -*-
"""
==============================================================================
AegisFlow 虚拟工坊运行健康与安全监视器 (heartbeat.py)
==============================================================================
负责对 AegisFlow 虚拟软件工坊中的全部活跃工单进行实时安全体检、异常检测
以及熔断风险早期预警。

核心能力：
1. 停滞超期任务筛查：检测研发耗时超过 8.0h (单一职责工时上限) 的滞留卡片。
2. 濒临熔断高危预警：预警累计打回 2 次的任务（第 3 次将触发硬熔断锁定）。
3. 熔断阻塞仲裁队列：提取所有处于 BLOCKED 状态亟需 CTO / 人工仲裁的死锁卡片。
4. 工坊健康量化评分 (0-100)：为管理者与操作员提供数字化的流水线健康指示。
==============================================================================
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保在 Windows 控制台环境下使用 UTF-8 输出，防止因特殊符号与 Emoji 触发 UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from tools.state_manager import StateManager


class StudioHeartbeat:
    """
    工坊运行健康与工作流安全监视核心引擎。
    """

    # 单一职责原则（SRP）推荐单任务最大工时上限（小时）
    DEFAULT_STALE_THRESHOLD_HOURS = 8.0

    # 三阶熔断触发打回次数阈值
    CIRCUIT_BREAKER_THRESHOLD = 3

    def __init__(self, root_dir: Optional[Path] = None, stale_threshold_hours: float = DEFAULT_STALE_THRESHOLD_HOURS):
        """
        初始化健康监视器。

        :param root_dir: 工作区根目录路径
        :param stale_threshold_hours: 判定任务停滞超期的工时阈值
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.state_manager = StateManager(str(self.root_dir))
        self.stale_threshold_hours = stale_threshold_hours

    def run_inspection(self) -> Dict[str, Any]:
        """
        全量扫描当前看板工单，计算工坊运营健康度并输出结构化指标。

        :return: 包含健康评分、风险告警清单和治理建议的字典
        """
        # 每次扫描重新加载磁盘数据，确保获取最新状态
        self.state_manager.data = self.state_manager._load()
        tasks = self.state_manager.list_tasks()

        stale_tasks: List[Dict[str, Any]] = []
        near_cb_tasks: List[Dict[str, Any]] = []
        blocked_tasks: List[Dict[str, Any]] = []
        active_count = 0

        now = datetime.now()

        for task in tasks:
            stage = task.get("stage", "")
            rejections_list = task.get("rejections", [])
            rejections_count = len(rejections_list) if isinstance(rejections_list, list) else int(rejections_list)
            task_id = task.get("id", "UNKNOWN")
            title = task.get("title", "未命名任务")
            assignee = task.get("assignee", "未指派")

            # 1. 统计熔断阻塞任务（达到3次打回或手动挂起，需CTO介入）
            if stage == "BLOCKED":
                last_reason = rejections_list[-1].get("reason", "触发三阶硬熔断或底层强阻塞") if rejections_list else "挂起阻塞"
                blocked_tasks.append({
                    "task_id": task_id,
                    "title": title,
                    "assignee": assignee,
                    "rejections": rejections_count,
                    "reason": last_reason
                })
                continue

            # 2. 统计濒临熔断高危任务（累计打回达到 2 次）
            if rejections_count >= (self.CIRCUIT_BREAKER_THRESHOLD - 1) and stage not in ("ACCEPTED", "CANCELLED", "BLOCKED"):
                near_cb_tasks.append({
                    "task_id": task_id,
                    "title": title,
                    "assignee": assignee,
                    "rejections": rejections_count,
                    "stage": stage
                })

            # 3. 统计停滞超期研发任务（超过 8.0h 单一职责上限）
            if stage in ("IN_PROGRESS", "CODE_REVIEW", "TESTING", "DOC_SYNC"):
                active_count += 1
                time_anchor = task.get("started_at") or task.get("created_at")
                if time_anchor:
                    try:
                        anchor_dt = datetime.fromisoformat(time_anchor)
                        duration_hours = (now - anchor_dt).total_seconds() / 3600.0
                        if duration_hours >= self.stale_threshold_hours:
                            stale_tasks.append({
                                "task_id": task_id,
                                "title": title,
                                "assignee": assignee,
                                "duration_hours": round(duration_hours, 1),
                                "stage": stage
                            })
                    except Exception:
                        pass

        # 计算工坊综合健康评分 (基础分: 100)
        # 扣分规则：
        # - 每项 BLOCKED 熔断任务: 扣 20 分
        # - 每项 2/3 接近熔断高危任务: 扣 15 分
        # - 每项超期停滞任务: 扣 10 分
        deductions = (len(blocked_tasks) * 20) + (len(near_cb_tasks) * 15) + (len(stale_tasks) * 10)
        health_score = max(0, min(100, 100 - deductions))

        # 判定健康等级标识
        if health_score >= 90:
            status_label = "HEALTHY"
            status_text = "健康 (HEALTHY)"
        elif health_score >= 70:
            status_label = "ATTENTION"
            status_text = "关注 (ATTENTION)"
        elif health_score >= 50:
            status_label = "WARNING"
            status_text = "预警 (WARNING)"
        else:
            status_label = "CRITICAL"
            status_text = "危急 (CRITICAL)"

        recommendations: List[str] = []
        if blocked_tasks:
            recommendations.append(
                f"[必须行动] 发现 {len(blocked_tasks)} 个任务处于 BLOCKED 熔断状态！需 CTO 介入仲裁或执行时空快照回退。"
            )
        if near_cb_tasks:
            recommendations.append(
                f"[高危预警] 发现 {len(near_cb_tasks)} 个任务已累计打回 2 次 (2/3)！请首席架构师重点介入代码与契约审查。"
            )
        if stale_tasks:
            recommendations.append(
                f"[超期警告] 发现 {len(stale_tasks)} 个任务执行已超过 {self.stale_threshold_hours}h 工时限额！建议 PMO 拆解 WBS 粒度。"
            )
        if not recommendations:
            recommendations.append("工坊全线研发运转正常，无死锁阻断，无高危熔断风险。")

        return {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "health_score": health_score,
            "status_label": status_label,
            "status_text": status_text,
            "active_tasks_count": active_count,
            "total_tasks_count": len(tasks),
            "stale_tasks": stale_tasks,
            "near_circuit_breaker_tasks": near_cb_tasks,
            "blocked_tasks": blocked_tasks,
            "recommendations": recommendations,
        }

    def print_heartbeat_report(self) -> None:
        """
        在终端打印全中文工坊运行健康体检看板。
        强制遵循 Top-5 防 Token 膨胀保护，并使用安全编码避免终端异常。
        """
        report = self.run_inspection()
        score = report["health_score"]
        status_text = report["status_text"]

        # ANSI 颜色定义
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        CYAN = "\033[96m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        color = GREEN if score >= 90 else (YELLOW if score >= 70 else RED)

        # 安全字符输出，杜绝部分旧版控制台 GBK 字符集崩溃
        try:
            print(f"\n{BOLD}{CYAN}================================================================{RESET}")
            print(f"{BOLD}             [神盾工坊] 运行健康度与流水线风险监视大盘          {RESET}")
            print(f"{BOLD}{CYAN}================================================================{RESET}")
            print(f" 工坊健康综合评分 : {color}{score}/100 [{status_text}]{RESET}")
            print(f" 活跃研发任务数   : {report['active_tasks_count']} / {report['total_tasks_count']} 项")
            print(f" 巡检扫描时间戳   : {report['timestamp']}")
            print(f"{CYAN}----------------------------------------------------------------{RESET}")

            # 1. 待仲裁熔断阻塞任务
            blocked = report["blocked_tasks"]
            if blocked:
                print(f"\n{RED}{BOLD}[!] 待 CTO / 人工仲裁的熔断阻塞任务 ({len(blocked)} 项):{RESET}")
                for item in blocked[:5]:
                    print(f"  * 【{item['task_id']}】 责任人: {item['assignee']} | 标题: {item['title']} (累计打回: {item['rejections']} 次)")
                    print(f"    阻断原因: {item['reason']}")
                if len(blocked) > 5:
                    print(f"    ... 以及其余 {len(blocked) - 5} 项阻塞任务 (请在 Web 看板查看全量)")

            # 2. 濒临熔断高危任务
            near_cb = report["near_circuit_breaker_tasks"]
            if near_cb:
                print(f"\n{YELLOW}{BOLD}[!] 濒临熔断高危任务 (累计打回 2/3 次) ({len(near_cb)} 项):{RESET}")
                for item in near_cb[:5]:
                    print(f"  * 【{item['task_id']}】 责任人: {item['assignee']} | 阶段: [{item['stage']}] | 标题: {item['title']}")
                if len(near_cb) > 5:
                    print(f"    ... 以及其余 {len(near_cb) - 5} 项高危任务")

            # 3. 超期停滞任务
            stale = report["stale_tasks"]
            if stale:
                print(f"\n{YELLOW}[~] 超过 {self.stale_threshold_hours}h 单一职责上限的停滞超期任务 ({len(stale)} 项):{RESET}")
                for item in stale[:5]:
                    print(f"  * 【{item['task_id']}】 责任人: {item['assignee']} | 已滞留: {item['duration_hours']}h (阶段: [{item['stage']}]) | 标题: {item['title']}")
                if len(stale) > 5:
                    print(f"    ... 以及其余 {len(stale) - 5} 项超期任务")

            # 4. 治理与运营建议
            print(f"\n{BOLD}工坊运营与治理建议:{RESET}")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

            print(f"{BOLD}{CYAN}================================================================\n{RESET}")
        except Exception:
            # 极度兜底纯净文本输出，杜绝任何编码崩溃
            print(f"[AEGISFLOW HEALTH] Score: {score}/100 [{status_text}], Active: {report['active_tasks_count']}/{report['total_tasks_count']}")


if __name__ == "__main__":
    heartbeat = StudioHeartbeat()
    heartbeat.print_heartbeat_report()

"""
AegisFlow Board Renderer (board_renderer.py)
=============================================

负责渲染高对比度、信息密集的终端 ANSI 敏捷看板，
并严格落实 Anti-Token Bleed（防 Token 膨胀）原则，默认仅向终端输出 Top-5 活跃工单。
"""

from typing import Dict, List, Any

# ANSI 终端色彩与样式转义码
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"


def format_stage_badge(stage: str) -> str:
    """
    根据生命周期阶段生成对应颜色的终端状态徽章。

    :param stage: 任务阶段名称 (如 IN_PROGRESS, COMPLETED, BLOCKED)
    :return: 带有 ANSI 颜色转义字符的文本徽章
    """
    if stage in ["COMPLETED", "ACCEPTED"]:
        return f"{GREEN}[{stage}]{RESET}"
    elif stage in ["IN_PROGRESS", "DEVELOPMENT"]:
        return f"{BLUE}[{stage}]{RESET}"
    elif stage in ["READY_TO_CLAIM", "CONTRACT_FROZEN"]:
        return f"{CYAN}[{stage}]{RESET}"
    elif stage in ["IN_AUDIT", "REVISE", "CODE_REVIEW", "SECURITY_AUDIT", "TESTING", "DOC_SYNC"]:
        return f"{YELLOW}[{stage}]{RESET}"
    elif stage == "BLOCKED":
        return f"{RED}{BOLD}[BLOCKED - CIRCUIT BREAKER]{RESET}"
    return f"{DIM}[{stage}]{RESET}"


def format_priority_badge(priority: str) -> str:
    """
    根据任务优先级生成醒目的颜色标签。

    :param priority: 优先级字符串 (CRIT, HIGH, MEDIUM, LOW)
    :return: 带有 ANSI 样式的短标签
    """
    p = priority.upper()
    if p in ["CRITICAL", "CRIT"]:
        return f"{RED}{BOLD}[CRIT]{RESET}"
    elif p == "HIGH":
        return f"{YELLOW}{BOLD}[HIGH]{RESET}"
    elif p == "MEDIUM":
        return f"{CYAN}[MED]{RESET}"
    return f"{DIM}[LOW]{RESET}"


class BoardRenderer:
    """
    终端敏捷看板文本格式化与渲染引擎。
    """

    @staticmethod
    def render_board(tasks: List[Dict[str, Any]], stats: Dict[str, Any], show_all: bool = False) -> str:
        """
        生成全景或精简版终端 ANSI 敏捷看板。

        设计原则：
        1. 默认展示 Top-5 活跃工单：防止 LLM 长文本上下文被数百条历史工单迅速消耗。
        2. 直观展示六重门禁通过凭据 (G1~G6) 及打回熔断进度 (X/3)。
        3. 熔断状态高危红字警示，引导 CTO 介入。

        :param tasks: 任务列表
        :param stats: 统计指标字典 (total_accepted, total_rejections, circuit_breakers_triggered)
        :param show_all: 是否显示全部任务 (为 True 时关闭 Top-5 节流)
        :return: 格式化完成的终端多行看板字符串
        """
        lines = []
        lines.append(f"{CYAN}{BOLD}===================================================================================================={RESET}")
        lines.append(f"{BOLD}                     🏢 AEGISFLOW VIRTUAL STUDIO (多Agent协同与制衡治理看板){RESET}")
        lines.append(f"{CYAN}{BOLD}===================================================================================================={RESET}")

        active_count = len([t for t in tasks if t["stage"] not in ["ACCEPTED", "CANCELLED"]])
        accepted_count = stats.get("total_accepted", 0)
        rejections_count = stats.get("total_rejections", 0)
        blocked_count = stats.get("circuit_breakers_triggered", 0)

        lines.append(
            f" 📊 活跃工单: {BOLD}{active_count}{RESET} | "
            f"已验收: {GREEN}{accepted_count}{RESET} | "
            f"累计打回制衡: {YELLOW}{rejections_count} 次{RESET} | "
            f"熔断挂起: {RED if blocked_count > 0 else GREEN}{blocked_count} 项{RESET}"
        )
        lines.append(f"{DIM}----------------------------------------------------------------------------------------------------{RESET}")

        if not tasks:
            lines.append("  (当前看板暂无工单。使用 'vc-cli create' 建立第一个需求/实施任务卡)")
            lines.append(f"{CYAN}{BOLD}===================================================================================================={RESET}")
            return "\n".join(lines)

        display_tasks = tasks if show_all else tasks[:5]

        for t in display_tasks:
            rejections = t.get("rejections", [])
            if rejections:
                last_rej = rejections[-1]
                rej_tag = last_rej.get("tag", "").split("#")[-1]
                rej_str = f"{YELLOW}{len(rejections)}/3 (#{rej_tag}){RESET}"
            elif t["stage"] == "BLOCKED":
                rej_str = f"{RED}{BOLD}3/3 (LOCKED){RESET}"
            else:
                rej_str = f"{GREEN}0/3 (CLEAN){RESET}"

            gates = t.get("gate_status", {})
            gate_badges = []
            if gates.get("gate_1_contract"):
                gate_badges.append(f"{GREEN}G1:PASS{RESET}")
            if gates.get("gate_2_review"):
                gate_badges.append(f"{GREEN}G2:PASS{RESET}")
            if gates.get("gate_3_security"):
                gate_badges.append(f"{GREEN}G3:PASS{RESET}")
            if gates.get("gate_4_testing"):
                gate_badges.append(f"{GREEN}G4:PASS{RESET}")
            if gates.get("gate_5_doc_sync"):
                gate_badges.append(f"{GREEN}G5:PASS{RESET}")
            if gates.get("gate_6_human_accept"):
                gate_badges.append(f"{GREEN}G6:ACCEPTED{RESET}")

            gate_line = " ".join(gate_badges) if gate_badges else f"{DIM}None passed yet{RESET}"

            lines.append(
                f" {BOLD}{t['id']}{RESET} {format_priority_badge(t.get('priority', 'HIGH'))} "
                f"| {t['title'][:45]} | 阶段: {format_stage_badge(t['stage'])} | 责任人: {CYAN}{t.get('assignee', 'None')}{RESET}"
            )
            lines.append(
                f"    ↳ 类型: {t.get('type', 'TSK')} (Tier {t.get('tier', 2)}) "
                f"| 工时: {t.get('est_hours', 4.0)}h "
                f"| 制衡打回: {rej_str} "
                f"| 门禁凭据: [{gate_line}]"
            )
            if rejections and t["stage"] in ["IN_PROGRESS", "BLOCKED"]:
                last_reason = rejections[-1].get("reason", "")[:70]
                lines.append(f"    ↳ {RED}驳回原因: {last_reason}...{RESET}")
            lines.append(f"{DIM}    ------------------------------------------------------------------------------------------------{RESET}")

        if not show_all and len(tasks) > 5:
            lines.append(
                f" 📌 {CYAN}Token 节流保护生效: 仅展示最近活跃的 5 条工单 (共 {len(tasks)} 条)。{RESET}"
            )
            lines.append(
                f"    查看全量: 'python tools/vc_cli.py board --all' | 浏览器大盘: 'python tools/vc_cli.py web'"
            )
        lines.append(f"{CYAN}{BOLD}===================================================================================================={RESET}")
        return "\n".join(lines)

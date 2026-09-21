"""
AegisFlow Unified Command-Line Interface (vc_cli.py)
=====================================================

AegisFlow 虚拟软件工坊统一管理命令行入口。
支持看板展示、工单全生命周期流转、六重质量门禁裁定、代码快速快筛、
时光倒流回滚以及零依赖本地 Web 大盘启动。
"""

import sys
import argparse
from pathlib import Path

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

# 确保项目根目录加入 sys.path，支持从项目任意深度直接运行该脚本
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tools.state_manager import StateManager, STAGES, ROLES, ITEM_TYPES, REJECT_TYPES
from tools.repo_hygiene import RepoHygieneGuard
from tools.gatekeeper import Gatekeeper
from tools.board_renderer import BoardRenderer
from tools.stack_sniffer import StackSniffer
from tools.git_hook import GitHookManager
from tools.heartbeat import StudioHeartbeat



def main():
    """
    CLI 命令行解析器与主分发入口。
    配置并路由 14 个核心子命令。
    """
    parser = argparse.ArgumentParser(
        prog="vc-cli",
        description="AegisFlow Virtual Studio Management CLI (多Agent协同与制衡统一命令行工具)"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用的管理子命令")

    # 1. init: 脚手架初始化
    init_p = subparsers.add_parser("init", help="初始化工程脚手架、AST Repo Map 与工单数据库")
    init_p.add_argument("--title", default="AegisFlow Project", help="项目名称")

    # 2. board: 终端看板展示
    board_p = subparsers.add_parser("board", help="显示终端 ANSI 敏捷看板 (默认 Top-5 保护)")
    board_p.add_argument("--all", action="store_true", help="显示全部工单 (禁用 Top-5 节流限制)")

    # 3. create: 创建新卡片
    create_p = subparsers.add_parser("create", help="创建新需求卡片或研发任务卡片")
    create_p.add_argument("--id", required=True, help="工单编号 (如 REQ-1001, TSK-1001-01, FIX-001)")
    create_p.add_argument("--title", required=True, help="工单标题")
    create_p.add_argument("--desc", default="", help="详细需求/技术说明")
    create_p.add_argument("--tier", type=int, default=2, choices=[0, 1, 2, 3], help="分级网关等级 (0-3)")
    create_p.add_argument("--type", default="TSK", choices=ITEM_TYPES, help="实体类型 (REQ, TSK, SPK, FIX, DOC)")
    create_p.add_argument("--priority", default="HIGH", choices=["CRIT", "HIGH", "MEDIUM", "LOW"], help="优先级")
    create_p.add_argument("--assignee", default="pm", choices=ROLES, help="初始负责人角色")
    create_p.add_argument("--hours", type=float, default=4.0, help="预估工时 (SRP原则强制 <= 8.0h)")

    # 4. start / claim: 领单开工
    start_p = subparsers.add_parser("start", help="认领工单并进入 IN_PROGRESS 研发状态")
    start_p.add_argument("--id", required=True, help="工单编号")
    start_p.add_argument("--role", default="developer", choices=ROLES, help="领单执行角色")

    claim_p = subparsers.add_parser("claim", help="认领就绪工单并锁定责任人进入 IN_PROGRESS (等价于 start)")
    claim_p.add_argument("--id", required=True, help="工单编号")
    claim_p.add_argument("--role", default="developer", choices=ROLES, help="领单执行角色")

    surrender_p = subparsers.add_parser("surrender", help="主动退还进行中的工单回待领池 (READY_TO_CLAIM)")
    surrender_p.add_argument("--id", required=True, help="工单编号")
    surrender_p.add_argument("--role", default="developer", choices=ROLES, help="退单角色 (必须是当前持单人)")
    surrender_p.add_argument("--reason", required=True, help="退单原因与技术阻碍说明")

    # 5. advance: 推进阶段
    adv_p = subparsers.add_parser("advance", help="推进工单至目标生命周期阶段")
    adv_p.add_argument("--id", required=True, help="工单编号")
    adv_p.add_argument("--stage", required=True, choices=STAGES, help="目标生命周期阶段")
    adv_p.add_argument("--role", required=True, choices=ROLES, help="操作执行角色")
    adv_p.add_argument("--note", default="", help="阶段流转备忘说明")
    adv_p.add_argument("--receipt", default=None, help="伴随的门禁凭证收据路径 (REC-xxx.json)")

    # 6. reject: 制衡打回 (行使一票否决权)
    rej_p = subparsers.add_parser("reject", help="行使专业一票否决权打回工单 (QR/SR/FR/DR)")
    rej_p.add_argument("--id", required=True, help="工单编号")
    rej_p.add_argument("--role", required=True, choices=ROLES, help="否决角色")
    rej_p.add_argument("--type", required=True, choices=REJECT_TYPES, help="打回类别 (QR/SR/FR/DR)")
    rej_p.add_argument("--reason", required=True, help="打回的详细理由与修改要求")
    rej_p.add_argument("--target", default="IN_PROGRESS", choices=STAGES, help="打回回滚的目标阶段")

    # 7. gate-check: 门禁评估
    gate_p = subparsers.add_parser("gate-check", help="执行六重确定性门禁自动化评估并签发密码学收据")
    gate_p.add_argument("--id", required=True, help="工单编号")
    gate_p.add_argument("--gate", required=True, choices=[
        "gate_1_contract",
        "gate_2_review",
        "gate_3_security",
        "gate_4_testing",
        "gate_5_doc_sync"
    ], help="门禁类型标识")
    gate_p.add_argument("--file", default=None, help="门禁关联校验的目标文件路径或测试执行命令")
    gate_p.add_argument("--commit-msg", default=None, help="用于 Gate 2 校验的 Git Commit 信息")

    # 7b. audit: 质检审查小组三合一流水线 (规范 + 安全 + 单测)
    audit_p = subparsers.add_parser("audit", help="质检审查小组 (qa_board) 执行三合一递进质检流水线")
    audit_p.add_argument("--id", required=True, help="工单编号")
    audit_p.add_argument("--commit-msg", default=None, help="用于工序1校验的 Git 提交信息")
    audit_p.add_argument("--target", default="src", help="工序2扫描源码目录 (默认 src)")
    audit_p.add_argument("--test-cmd", default="python -m unittest", help="工序3自动化测试命令")

    # 7c. arbitrate: 唤醒休眠 CTO 深度剖析熔断死锁工单
    arb_p = subparsers.add_parser("arbitrate", help="唤醒休眠 CTO 深度剖析熔断死锁工单并输出诊断报告")
    arb_p.add_argument("--id", required=True, help="工单编号")

    # 8. lint: 快速语法快筛 (SWE-agent 理念)
    lint_p = subparsers.add_parser("lint", help="SWE-agent 风格快速 AST 语法与括号解析快筛")
    lint_p.add_argument("--target", default="src", help="目标文件或目录路径 (默认 src)")

    # 9. repomap: 刷新代码结构地图
    subparsers.add_parser("repomap", help="基于 AST 生成或刷新 Aider 风格代码架构地图")

    # 10. rollback: 时光倒流回滚
    rb_p = subparsers.add_parser("rollback", help="基于历史检查点执行 LangGraph 风格时光倒流回退")
    rb_p.add_argument("--id", required=True, help="工单编号")
    rb_p.add_argument("--stage", required=True, choices=STAGES, help="目标回滚阶段名称")

    # 11. hygiene: 仓库清洁度体检
    hyg_p = subparsers.add_parser("hygiene", help="扫描仓库根目录零污染白名单与测试镜像一致性")
    hyg_p.add_argument("--fix", action="store_true", help="自动修复缺失的标准工程脚手架目录")

    # 12. accept: 人类终审验收 (Gate 6)
    accept_p = subparsers.add_parser("accept", help="人类操作员物理交互终审验收 (终态不可逆)")
    accept_p.add_argument("--id", required=True, help="工单编号")
    accept_p.add_argument("--by", default="HUMAN_OPERATOR", help="验收人签名")
    accept_p.add_argument("--note", default="", help="最终验收备忘")
    accept_p.add_argument("--yes", action="store_true", help="自动化或 CI 环境下的免交互确认参数")

    # 13. status: 综合审计与履历查询
    status_p = subparsers.add_parser("status", help="查询任务详尽审计追踪、门禁凭证与流转历史")
    status_p.add_argument("--id", required=True, help="工单编号")

    # 14. web: 离线 Web 看板启动
    web_p = subparsers.add_parser("web", help="启动零依赖本地 Web 敏捷仪表盘")
    web_p.add_argument("--port", type=int, default=8848, help="绑定端口 (默认 8848)")

    # 15. detect: 自动嗅探多语言技术栈并生成画像
    detect_p = subparsers.add_parser("detect", help="自动快筛多语言工程技术栈 (Python, Node/TS, Go, Rust, Java) 并生成配置")
    detect_p.add_argument("--save", action="store_true", default=True, help="保存项目配置至 .agents/project_profile.json")

    # 16. hook: 物理 Git pre-commit 钩子管理
    hook_p = subparsers.add_parser("hook", help="物理 Git pre-commit 钩子管理 (无工单禁止提交与根目录零污染)")
    hook_p.add_argument("action", choices=["install", "uninstall", "verify"], help="钩子操作 (install, uninstall, verify)")

    # 17. heartbeat: 工坊运行健康体检
    hb_p = subparsers.add_parser("heartbeat", help="工坊运行健康体检、停滞任务预警与熔断风险排查")
    hb_p.add_argument("--stale-hours", type=float, default=8.0, help="判定停滞任务的超期工时阈值 (默认 8.0h)")

    # 18. reset: 清空看板与测试数据恢复纯净初始状态
    reset_p = subparsers.add_parser("reset", help="重置看板数据库、收据与日志，恢复开源纯净初始状态")
    reset_p.add_argument("--confirm", action="store_true", help="确认重置全部工单数据与运行时收据")

    args = parser.parse_args()

    sm = StateManager()
    hygiene = RepoHygieneGuard()
    gk = Gatekeeper()

    # --- 执行分支分发 ---
    if args.command == "init":
        created = hygiene.init_scaffolding()
        sm._save()
        print(f"🛡️  AegisFlow 虚拟软件工坊脚手架初始化成功！")
        print(f"📁 已创建目录与核心配置: {len(created)} 个。")
        print(f"🗺️  AST Repo Map 代码结构地图已生成: docs/PROJECT_STRUCTURE.md")
        print(f"💾 看板数据库路径: {sm.storage_path}")

    elif args.command == "board":
        tasks = sm.list_tasks()
        stats = sm.data.get("metrics", {})
        print(BoardRenderer.render_board(tasks, stats, show_all=args.all))

    elif args.command == "create":
        try:
            task = sm.create_task(
                task_id=args.id,
                title=args.title,
                desc=args.desc,
                tier=args.tier,
                item_type=args.type,
                priority=args.priority,
                assignee=args.assignee,
                est_hours=args.hours
            )
            print(f"✅ [工单已创建] Task created: {task['id']} [{task['priority']}] - {task['title']}")
        except Exception as e:
            print(f"❌ 创建工单失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command in ["start", "claim"]:
        try:
            task = sm.start_task(args.id, args.role)
            print(f"🚀 [领单开工成功] [CLAIM PASS] Work started on {task['id']} (已由 {args.role} 认领锁定)！")
            print(f"   开工时间: {task['started_at']}")
            print(f"   当前阶段: [{task['stage']}] (WIP 并发限制 [最多3个] 已生效)")
        except Exception as e:
            print(f"❌ 领单操作被物理门禁拦截: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "surrender":
        try:
            task = sm.surrender_task(args.id, args.role, args.reason)
            print(f"🔄 [主动退单成功] [SURRENDER PASS] Task {task['id']} 已退回待领池 [READY_TO_CLAIM]！")
            print(f"   退单人:   {args.role}")
            print(f"   退单原因: {args.reason}")
        except Exception as e:
            print(f"❌ 退单操作失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "advance":
        try:
            task = sm.advance_stage(args.id, args.stage, args.role, args.note, args.receipt)
            print(f"➡️ [阶段跃迁] Task {args.id} advanced to stage [{task['stage']}] by {args.role}。")
        except Exception as e:
            print(f"❌ 推进阶段失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "reject":
        try:
            task = sm.reject_task(args.id, args.role, args.type, args.reason, args.target)
            last_rej = task["rejections"][-1]
            print(f"🚫 [专业一票否决] [VETO] Task {args.id} rejected by {args.role}: {last_rej['tag']}")
            print(f"   否决理由: {args.reason}")
            print(f"   当前阶段: [{task['stage']}] (当前负责人: {task['assignee']})")
            if task["stage"] == "BLOCKED":
                print(f"🚨 [三振出局硬熔断] 工单累计打回达到 3 次，已锁定为 BLOCKED 状态，等待 CTO 仲裁！")
        except Exception as e:
            print(f"❌ 否决打回操作失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "gate-check":
        if args.gate == "gate_1_contract":
            if not args.file:
                print("❌ Gate 1 契约核验必须提供契约路径: --file <contract_path>", file=sys.stderr)
                sys.exit(1)
            passed, msg, details = gk.check_gate_1_contract(args.id, args.file)
        elif args.gate == "gate_2_review":
            commit_msg = args.commit_msg or "feat(core): implementation update"
            passed, msg, details = gk.check_gate_2_review(args.id, commit_msg, args.file)
        elif args.gate == "gate_3_security":
            passed, msg, details = gk.check_gate_3_security(args.id)
        elif args.gate == "gate_4_testing":
            if args.file:
                cmd = args.file
            else:
                sniffer = StackSniffer()
                profile = sniffer.sniff()
                cmd = profile.get("default_test_command") or "python -m unittest discover tests"
            passed, msg, details = gk.check_gate_4_testing(args.id, cmd)

        elif args.gate == "gate_5_doc_sync":
            files = [args.file] if args.file else ["src/api/routes.py", "docs/api/README.md"]
            passed, msg = gk.check_gate_5_doc_sync(args.id, files)
            details = {}
        else:
            passed, msg, details = False, "未知门禁类型", {}

        if passed:
            receipt = gk.issue_receipt(args.id, args.gate, True, details)
            sm.data["tasks"][args.id]["gate_status"][args.gate] = True
            sm.advance_stage(args.id, sm.get_task(args.id)["stage"], "gatekeeper", note=msg, receipt_path=receipt)
            print(f"✅ [门禁核验通过] [GATE PASSED] {args.gate}: {msg}")
            print(f"   已签发密码学收据: {receipt}")
        else:
            receipt = gk.issue_receipt(args.id, args.gate, False, details)
            print(f"❌ [门禁核验未通过] [GATE FAILED] {args.gate}: {msg}")
            print(f"   失败审计记录已归档: {receipt}")
            sys.exit(1)

    elif args.command == "audit":
        passed, msg, meta = gk.run_unified_qa_audit(
            args.id,
            commit_msg=args.commit_msg,
            target_dir=args.target,
            test_command=args.test_cmd
        )
        if passed:
            try:
                sm.advance_stage(
                    args.id,
                    "DOC_SYNC",
                    "qa_board",
                    note="QA Board 统一三合一质检全通",
                    receipt_path=meta.get("receipt_file")
                )
                print(f"✅ [质检小组三审全通] [AUDIT PASS] Task {args.id} 规范、安全、自动化单测全部绿灯！")
                print(f"   📑 综合质检报告: {meta.get('report_file')}")
                print(f"   📜 密码学收据:   {meta.get('receipt_file')}")
                print(f"   ➡️ 已成功将工单移交活文档工程师 (阶段: DOC_SYNC)。")
            except Exception as e:
                print(f"❌ 质检通过但阶段流转失败: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            veto_type = meta.get("veto_type", "QR")
            print(f"🚫 [质检小组一票否决] [AUDIT VETO #{veto_type}] {msg}", file=sys.stderr)
            try:
                task = sm.reject_task(args.id, "qa_board", veto_type, msg, target_stage="REVISE")
                print(f"   工单已自动变更为 REVISE 整改状态 (打回计数: {len(task['rejections'])}/3 次)。")
                if task["stage"] == "BLOCKED":
                    print(f"🚨 [三振出局硬熔断] 工单累计打回达到 3 次，已锁定为 BLOCKED 状态，休眠 CTO 已唤醒并生成诊断！")
            except Exception as e:
                print(f"   打回状态记录失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "arbitrate":
        try:
            report_path = sm.generate_cto_arbitration_report(args.id)
            print(f"⚖️ [CTO 熔断仲裁诊断完成] [ARBITRATION PASS]")
            print(f"   诊断报告已生成: {report_path}")
            task = sm.get_task(args.id)
            if task.get("arbitration_report"):
                print("\n" + task["arbitration_report"])
        except Exception as e:
            print(f"❌ CTO 仲裁诊断失败: {e}", file=sys.stderr)
            sys.exit(1)


    elif args.command == "lint":
        passed, errors = gk.fast_lint(args.target)
        if passed:
            print(f"✅ [AST语法快筛通过] [LINT PASS] Fast AST syntax check passed on '{args.target}'. 零语法错误。")
        else:
            print(f"❌ [AST语法快筛未通过] [LINT FAIL] Fast AST syntax check failed with {len(errors)} error(s):")
            for err in errors:
                print(f"   - {err}")
            sys.exit(1)

    elif args.command == "repomap":
        map_path = hygiene.generate_repo_map()
        print(f"🗺️  代码架构地图已成功刷新 (AST Repo Map refreshed: {map_path})")

    elif args.command == "rollback":
        try:
            snapshot = sm.rollback_to_checkpoint(args.id, args.stage)
            print(f"⏪ [时光倒流安全回退] [TIME-TRAVEL] Task {args.id} restored to checkpoint [{args.stage}] by CTO.")
        except Exception as e:
            print(f"❌ 回滚操作执行失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "hygiene":
        if args.fix:
            hygiene.init_scaffolding()
        res = hygiene.run_full_scan()
        if res["passed"]:
            print("✅ [仓库整洁度核验通过] [HYGIENE PASS] Repository clean. 根目录零污染，测试镜像 1:1 一致。")
        else:
            print(f"⚠️ [仓库整洁度违规] [HYGIENE WARNING] 发现 {res['total_violations']} 项违规:")
            for v in res["root_violations"] + res["test_violations"] + res["depth_violations"]:
                print(f"   - {v}")
            sys.exit(1)

    elif args.command == "accept":
        if not args.yes:
            # 人类物理交互保障：严禁脚本或 Agent 在非交互 TTY 下自动验收
            if not sys.stdin.isatty():
                print("❌ [安全一票否决] 检测到非交互式环境！'accept' 终审验收必须由人类在真实终端控制台物理操作。", file=sys.stderr)
                sys.exit(1)
            confirm = input(f"👤 人类操作员物理终审：确认对工单 {args.id} 进行最终业务验收并封板？[y/N]: ")
            if confirm.strip().lower() != "y":
                print("操作已被操作员手动取消。")
                sys.exit(0)

        try:
            task = sm.accept_task(args.id, accepted_by=args.by, note=args.note)
            print(f"🎉 [终审验收通过] [ACCEPTED] Task {args.id} successfully accepted and locked by {args.by}!")
        except Exception as e:
            print(f"❌ 终审验收执行失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "status":
        try:
            task = sm.get_task(args.id)
            print("======================================================================")
            print(f" 📋 工单编号:    {task['id']} [{task['priority']}] (分级网关: Tier {task.get('tier', 2)})")
            print(f" 🏷️ 需求标题:    {task['title']}")
            print(f" 📍 当前阶段:    [{task['stage']}] | 当前负责人: {task.get('assignee', '未指派')}")
            print(f" ⏱️ 预估工时:    {task.get('est_hours', 4.0)}h | 研发耗时: {task.get('lead_time_seconds', 'N/A')}秒")
            print(f" 🚫 累计打回:    {len(task.get('rejections', []))} / 3 次")
            for r in task.get("rejections", []):
                print(f"    - 【{r.get('tag')}】 由 {r.get('rejected_by')} 否决 ({r.get('type')}): {r.get('reason')}")
            print("----------------------------------------------------------------------")
            print(" 🛡️ 六重确定性质量门禁状态:")
            for gk_name, val in task.get("gate_status", {}).items():
                status_str = "✅ 已通过 (PASSED)" if val else "⏳ 待核验 (PENDING)"
                print(f"    - {gk_name}: {status_str}")
            print("----------------------------------------------------------------------")
            print(" 📜 审计履历追踪 (最近 5 次流转):")
            for h in task.get("history", [])[-5:]:
                print(f"    [{h.get('timestamp')[:19]}] {h.get('action')} -> [{h.get('stage')}] 操作人: {h.get('role')}: {h.get('note', '')[:60]}")
            print("======================================================================")
        except Exception as e:
            print(f"❌ 获取任务状态失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "web":
        from tools.kanban_server import run_server
        run_server(args.port)

    elif args.command == "detect":
        sniffer = StackSniffer()
        profile_path = sniffer.save_profile()
        profile = sniffer.sniff()
        print(f"🔍 [技术栈画像快筛完成] [DETECT PASS] Tech-stack profiling completed:")
        print(f"   工程名称:     {profile['project_name']}")
        print(f"   主力研发语言: {profile['primary_language']}")
        print(f"   识别语言清单: {', '.join(profile['detected_languages'])}")
        print(f"   推荐测试命令: {profile['default_test_command']}")
        print(f"   推荐快筛命令: {profile['default_lint_command']}")
        print(f"   画像落盘路径: {profile_path}")

    elif args.command == "hook":
        hook_mgr = GitHookManager()
        if args.action == "install":
            ok, msg = hook_mgr.install_hook()
            print(("✅ " if ok else "❌ ") + msg)
            if not ok:
                sys.exit(1)
        elif args.action == "uninstall":
            ok, msg = hook_mgr.uninstall_hook()
            print(("✅ " if ok else "❌ ") + msg)
            if not ok:
                sys.exit(1)
        elif args.action == "verify":
            ok, msg = hook_mgr.verify_pre_commit(sm, hygiene)
            if ok:
                print(f"✅ [物理门禁放行] [HOOK PASS] {msg}")
            else:
                print(f"🚫 [物理门禁拦截] [HOOK REJECTED]\n{msg}", file=sys.stderr)
                sys.exit(1)

    elif args.command == "heartbeat":
        hb = StudioHeartbeat(stale_threshold_hours=args.stale_hours)
        hb.print_heartbeat_report()

    elif args.command == "reset":
        if not args.confirm:
            print("⚠️ 请附带 --confirm 参数以确认重置全部看板工单与运行时收据 (例: python tools/vc_cli.py reset --confirm)。")
            sys.exit(1)
        sm.data = {
            "version": "3.0.0",
            "framework": "AegisFlow",
            "created_at": sm.data.get("created_at"),
            "updated_at": sm.data.get("updated_at"),
            "tasks": {},
            "checkpoints": {},
            "metrics": {
                "total_created": 0,
                "total_accepted": 0,
                "total_rejections": 0,
                "circuit_breakers_triggered": 0
            }
        }
        sm._save()
        if sm.event_stream_path.exists():
            with open(sm.event_stream_path, "w", encoding="utf-8") as f:
                f.write("")
        receipts_dir = sm.root_dir / ".agents" / "receipts"
        if receipts_dir.exists():
            for r in receipts_dir.glob("REC-*.json"):
                try:
                    r.unlink()
                except Exception:
                    pass
            (receipts_dir / ".gitkeep").touch()
        print("✨ [纯净重置成功] AegisFlow 看板、密码学收据与事件流已彻底恢复开源纯净状态 (0 工单)。")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


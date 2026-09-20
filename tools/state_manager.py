"""
AegisFlow State Manager & Task Lifecycle Engine (state_manager.py)
==================================================================

负责管理任务生命周期、阶段跃迁、四维否决打回、三振出局熔断机制、
LangGraph 理念检查点时光倒流 (Time-Travel) 与 OpenHands 风格不可变事件流审计。
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 默认存储路径定义
DEFAULT_STORAGE_FILE = Path(".agents") / ".virtual_company_board.json"
EVENT_STREAM_FILE = Path(".agents") / "event_stream.jsonl"

# 敏捷研发生命周期标准阶段 (核心 8 态 + 2 异常终态)
STAGES = [
    "PENDING",            # 1. 待规划设计：PM 制定量化 AC，架构师技术设计
    "READY_TO_CLAIM",     # 2. 待领取：架构白名单契约锁定 (Gate 1)，静候认领
    "IN_PROGRESS",        # 3. 进行中：核心研发白名单编码与 1:1 单测自测
    "IN_AUDIT",           # 4. 质检中：质检审查小组 (qa_board) 串行跑规范/安全/单测
    "REVISE",             # 5. 质检整改：质检未过打回整改 (累计3次硬熔断)
    "DOC_SYNC",           # 6. 文档同步中：活文档工程师更新接口与全景架构图
    "COMPLETED",          # 7. 待终审/就绪：全门禁闭环，运维演练完毕，等待人类终审
    "ACCEPTED",           # 8. 已验收归档：人类管理员终审封板确认 (不可逆终态)
    "BLOCKED",            # 9. 熔断挂起：连续 3 次打回或严重死锁，休眠 CTO 唤醒仲裁
    "CANCELLED",          # 10. 已取消 / 需求废弃
    # --- 历史阶段平滑兼容别名 ---
    "BACKLOG", "SPECIFICATION", "CONTRACT_FROZEN", "CODE_REVIEW", "SECURITY_AUDIT", "TESTING"
]

# 工坊标准研发角色列表 (5 常驻骨干 + 2 阶段专家 + 1 仲裁官 + 1 最高主权)
ROLES = [
    "pm",                 # 团队负责人 / PM 📋
    "architect",          # 系统架构师 🏛️
    "developer",          # 核心研发工程师 💻
    "qa_board",           # 质检审查小组 🧪 (整合审查、安全、测试三合一)
    "doc_engineer",       # 活文档工程师 📚
    "researcher",         # 技术调研专家 🔬 (初次/陌生技术按需唤醒)
    "devops",             # 部署运维专家 🚀 (架构期参谋 + 发版两段式)
    "cto",                # 首席技术仲裁官 ⚖️ (休眠，熔断仲裁与时光倒流)
    "human_admin",        # 人类管理员 👑 (最高终审主权)
    # --- 历史角色平滑兼容别名 ---
    "code_reviewer", "security_engineer", "qa_engineer", "release_engineer", "human_operator", "uiux_designer", "dba"
]

# 实体分类学前缀与打回类别定义
ITEM_TYPES = ["REQ", "TSK", "SPK", "FIX", "DOC"]
REJECT_TYPES = ["QR", "SR", "FR", "DR"]  # QR:规范质量 / SR:安全机密 / FR:功能单测 / DR:文档同步

# 标准角色职责定位与画像字典
ROLE_PROFILES: Dict[str, Dict[str, str]] = {
    "pm": {"title": "团队负责人 (PM)", "icon": "📋", "scope": "团队全面统筹、业务目标拟定与量化验收准则 (AC)"},
    "architect": {"title": "系统架构师", "icon": "🏛️", "scope": "系统边界、技术方案与白名单契约锁定 (Gate 1)"},
    "developer": {"title": "核心研发工程师", "icon": "💻", "scope": "范围白名单内精准实现与 1:1 镜像单测自测"},
    "qa_board": {"title": "质检审查小组", "icon": "🧪", "scope": "三合一递进质检 (规范审查 + SAST安全 + 自动化单测)"},
    "doc_engineer": {"title": "活文档工程师", "icon": "📚", "scope": "接口文档同步与 AST 全景代码架构地图维护"},
    "researcher": {"title": "技术调研专家", "icon": "🔬", "scope": "初次/陌生技术路线探索与可行性探针报告 (按需唤醒)"},
    "devops": {"title": "部署运维专家", "icon": "🚀", "scope": "架构期环境部署参谋与终局发布演练打包 (两段式)"},
    "cto": {"title": "首席技术仲裁官", "icon": "⚖️", "scope": "平时休眠，连续3次打回熔断唤醒，根因剖析与时光倒流"},
    "human_admin": {"title": "人类管理员", "icon": "👑", "scope": "项目最终业务验收与不可逆封板归档 (最高主权)"},
    # 兼容历史画像
    "code_reviewer": {"title": "代码审查员", "icon": "🔍", "scope": "AST语法快筛与提交规范审查"},
    "security_engineer": {"title": "独立安全审计员", "icon": "🛡️", "scope": "SAST机密与漏洞扫描防护"},
    "qa_engineer": {"title": "质量验证测试员", "icon": "🧪", "scope": "自动化测试与镜像对齐验证"},
    "release_engineer": {"title": "发布协调主管", "icon": "🚀", "scope": "版本组装与全绿交付核验"},
    "human_operator": {"title": "人类管理员", "icon": "👑", "scope": "项目最终业务验收与不可逆归档"},
    "uiux_designer": {"title": "UI/UX体验设计师", "icon": "🎨", "scope": "交互走查与界面规范审查"},
    "dba": {"title": "数据库管理员", "icon": "🗄️", "scope": "表结构评估与数据一致性"}
}

# 角色与阶段流转严格权限矩阵 (Strict Role-Stage Transition Permissions)
# 核心铁律：开发者只能领单或提审，绝对禁止直接标记完成；每一步必须由对应质检角色审核放行
STAGE_PERMISSIONS: Dict[str, Dict[str, Any]] = {
    "PENDING": {
        "allowed_roles": ["pm", "architect", "human_admin", "human_operator"],
        "from_stages": ["BACKLOG", "SPECIFICATION", "BLOCKED"],
        "err_msg": "权限拦截：只有团队负责人 (pm) 或系统架构师可规划需求阶段 (PENDING)。"
    },
    "READY_TO_CLAIM": {
        "allowed_roles": ["architect", "pm"],
        "from_stages": ["PENDING", "SPECIFICATION", "BACKLOG", "CONTRACT_FROZEN"],
        "err_msg": "权限拦截：只有系统架构师 (architect) 在锁定架构契约后可推进至 READY_TO_CLAIM (待领取)。"
    },
    "IN_PROGRESS": {
        "allowed_roles": ["developer", "pm", "cto", "architect"],
        "from_stages": ["READY_TO_CLAIM", "PENDING", "REVISE", "IN_AUDIT", "BLOCKED", "CONTRACT_FROZEN", "BACKLOG", "SPECIFICATION", "CODE_REVIEW", "SECURITY_AUDIT", "TESTING", "DOC_SYNC"],
        "err_msg": "权限拦截：只有研发工程师 (developer) 或 CTO/PM 可启动研发编码 (IN_PROGRESS)。"
    },
    "IN_AUDIT": {
        "allowed_roles": ["developer", "pm", "qa_board"],
        "from_stages": ["IN_PROGRESS", "REVISE"],
        "err_msg": "权限拦截：只有研发工程师 (developer) 在完成编码与自测后可提交质检审查 (IN_AUDIT)。"
    },
    "REVISE": {
        "allowed_roles": ["qa_board", "code_reviewer", "security_engineer", "qa_engineer", "doc_engineer", "pm"],
        "from_stages": ["IN_AUDIT", "DOC_SYNC", "CODE_REVIEW", "SECURITY_AUDIT", "TESTING"],
        "err_msg": "权限拦截：只有质检审查小组 (qa_board) 或活文档工程师可驳回任务至 REVISE (质检整改)。"
    },
    "DOC_SYNC": {
        "allowed_roles": ["qa_board", "qa_engineer", "doc_engineer", "pm"],
        "from_stages": ["IN_AUDIT", "TESTING", "IN_PROGRESS"],
        "err_msg": "权限拦截：只有质检审查小组 (qa_board) 质检全通后可移交活文档同步 (DOC_SYNC)。"
    },
    "COMPLETED": {
        "allowed_roles": ["doc_engineer", "devops", "release_engineer", "qa_board", "qa_engineer", "pm"],
        "from_stages": ["DOC_SYNC", "TESTING", "IN_AUDIT", "SECURITY_AUDIT", "CODE_REVIEW", "IN_PROGRESS"],
        "err_msg": "权限拦截：研发人员 (developer) 绝对禁止直接将工单标记为完成 (COMPLETED)！必须由活文档/运维/质检在完成全部质检闭环后方可完成！"
    },
    "ACCEPTED": {
        "allowed_roles": ["human_admin", "human_operator"],
        "from_stages": ["COMPLETED"],
        "err_msg": "权限拦截：ACCEPTED 为人类管理员物理专属终态，智能体严禁自我验收！"
    },
    "BLOCKED": {
        "allowed_roles": ["cto", "qa_board", "pm", "human_admin"],
        "from_stages": ["IN_AUDIT", "REVISE", "IN_PROGRESS", "DOC_SYNC", "TESTING", "CODE_REVIEW", "SECURITY_AUDIT"],
        "err_msg": "权限拦截：BLOCKED 为熔断挂起状态，由系统触发或 CTO 介入仲裁。"
    },
    "CANCELLED": {
        "allowed_roles": ["pm", "human_admin", "human_operator"],
        "from_stages": ["PENDING", "READY_TO_CLAIM", "IN_PROGRESS", "IN_AUDIT", "REVISE", "DOC_SYNC", "COMPLETED", "BLOCKED", "BACKLOG"],
        "err_msg": "权限拦截：只有 PM 或人类管理员有权取消/废弃任务。"
    },
    # 历史阶段兼容
    "SPECIFICATION": {
        "allowed_roles": ["pm", "architect"],
        "from_stages": ["BACKLOG", "PENDING"],
        "err_msg": "权限拦截：只有 PM 或系统架构师可推进至 SPECIFICATION。"
    },
    "CONTRACT_FROZEN": {
        "allowed_roles": ["architect", "pm"],
        "from_stages": ["SPECIFICATION", "BACKLOG", "PENDING"],
        "err_msg": "权限拦截：只有系统架构师可锁定契约 (CONTRACT_FROZEN)。"
    },
    "CODE_REVIEW": {
        "allowed_roles": ["developer", "code_reviewer", "pm"],
        "from_stages": ["IN_PROGRESS"],
        "err_msg": "权限拦截：只有研发工程师可提交代码审查。"
    },
    "SECURITY_AUDIT": {
        "allowed_roles": ["code_reviewer", "security_engineer", "pm"],
        "from_stages": ["CODE_REVIEW", "IN_PROGRESS"],
        "err_msg": "权限拦截：只有代码审查员评审合格后可移交安全审计。"
    },
    "TESTING": {
        "allowed_roles": ["security_engineer", "qa_engineer", "qa_board", "pm"],
        "from_stages": ["SECURITY_AUDIT", "CODE_REVIEW", "IN_PROGRESS"],
        "err_msg": "权限拦截：只有安全审计员审计合格后可移交自动化测试。"
    }
}



class StateManager:
    """
    任务状态管理器与生命周期控制核心引擎。
    管理任务状态迁移、多维打回、熔断保护以及时空回溯快照。
    """

    def __init__(self, root_dir: str = "."):
        """
        初始化状态管理器。

        :param root_dir: 项目根目录绝对或相对路径，默认为当前工作目录。
        """
        self.root_dir = Path(root_dir).resolve()
        self.storage_path = self.root_dir / DEFAULT_STORAGE_FILE
        self.event_stream_path = self.root_dir / EVENT_STREAM_FILE
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """
        从本地 JSON 存储加载看板数据。若文件不存在或读取失败，则自动初始化基础结构。

        :return: 包含任务、检查点与统计指标的字典。
        """
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 兼容性修复与富化：确保 objective, result, collaborators, role_contributions 完整
                for task_id, t in data.get("tasks", {}).items():
                    if "objective" not in t or not t["objective"]:
                        t["objective"] = t.get("title", "")
                    if "result" not in t:
                        t["result"] = "全生命周期质量门禁已全部闭环，已由人类管理员终审核准归档。" if t.get("stage") == "ACCEPTED" else ""
                    if "collaborators" not in t:
                        t["collaborators"] = []

                    # 确保需求背景与验收准则 (AC) 绝不为空
                    desc_val = t.get("desc") or t.get("description") or ""
                    if not desc_val.strip():
                        specs_dir = self.root_dir / "docs" / "specs"
                        found_spec = None
                        if specs_dir.exists():
                            for sf in specs_dir.glob(f"*{task_id}*.md"):
                                try:
                                    found_spec = sf.read_text(encoding="utf-8")
                                    break
                                except Exception:
                                    pass
                        if found_spec:
                            desc_val = found_spec.strip()
                        else:
                            obj_txt = t.get("objective", t.get("title", ""))
                            desc_val = (
                                f"【业务需求背景与目标】:\n{obj_txt}\n\n"
                                f"【验收准则 (AC)】:\n"
                                f"1. 核心功能特性与架构白名单契约严格对齐；\n"
                                f"2. 具备独立自动化测试用例且回归 100% PASS；\n"
                                f"3. SAST 静态安全扫描与 AST 语法快筛 0 违规；\n"
                                f"4. 活文档与代码架构地图保持同步更新。"
                            )
                    t["desc"] = t["description"] = desc_val

                    if "role_contributions" not in t or not t["role_contributions"]:
                        contributions = []
                        for h in t.get("history", []):
                            r = h.get("role", "developer")
                            r_key = "human_operator" if ("Human" in str(r) or "human" in str(r)) else str(r)
                            prof = ROLE_PROFILES.get(r_key, {"title": r, "icon": "👤", "scope": "生命周期协同"})
                            act_name = h.get("note") or h.get("action", "推进工单")
                            rec = h.get("receipt")
                            deliv = Path(rec).name if rec else "阶段成果"
                            verdict = "REJECTED" if h.get("action") == "REJECT" else ("ACCEPTED" if h.get("action") == "HUMAN_ACCEPT" else "PASS")
                            contributions.append({
                                "role": r_key,
                                "title": prof.get("title", r),
                                "icon": prof.get("icon", "👤"),
                                "phase": h.get("stage", "STAGE"),
                                "action": act_name,
                                "deliverable": deliv,
                                "verdict": verdict,
                                "timestamp": h.get("timestamp", "")
                            })
                        t["role_contributions"] = contributions
                return data
            except Exception as e:
                print(f"[WARN] Failed to read storage file: {e}. Reinitializing board.", file=sys.stderr)
        return {
            "version": "3.0.0",
            "framework": "AegisFlow",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tasks": {},
            "checkpoints": {},  # TaskID -> 状态快照切片列表 (支持时光倒流 Time-Travel)
            "metrics": {
                "total_created": 0,
                "total_accepted": 0,
                "total_rejections": 0,
                "circuit_breakers_triggered": 0
            }
        }

    def _save(self) -> None:
        """
        以原子写入方式（先写入 .tmp 文件再重命名）持久化看板数据，防止多进程或异常中断导致 JSON 文件损坏。
        """
        self.data["updated_at"] = datetime.now().isoformat()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.storage_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        temp_file.replace(self.storage_path)

    def _log_event(self, event_type: str, task_id: str, actor: str, payload: Dict[str, Any]) -> None:
        """
        OpenHands 风格只追加（Append-Only）不可变事件流审计器。
        将每个状态变更、打回与审批操作实时记录到 JSONL 文件中。

        :param event_type: 事件类型名称 (如 TASK_CREATED, STAGE_ADVANCED)
        :param task_id: 关联的任务编号
        :param actor: 执行该操作的角色或主体
        :param payload: 事件相关的附加元数据
        """
        try:
            self.event_stream_path.parent.mkdir(parents=True, exist_ok=True)
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "task_id": task_id,
                "actor": actor,
                "payload": payload
            }
            with open(self.event_stream_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[WARN] Failed to append event stream: {e}", file=sys.stderr)

    def _record_checkpoint(self, task_id: str, stage_name: str) -> None:
        """
        LangGraph 风格检查点记录器。
        在每个状态迁移节点对工单做完整快照深拷贝，用于后续时光倒流回滚。
        每个任务最多保留最近 10 个检查点以控制体积。

        :param task_id: 目标任务编号
        :param stage_name: 发生跃迁的目标阶段名称
        """
        if task_id not in self.data["checkpoints"]:
            self.data["checkpoints"][task_id] = []
        task_copy = json.loads(json.dumps(self.data["tasks"][task_id]))
        self.data["checkpoints"][task_id].append({
            "timestamp": datetime.now().isoformat(),
            "stage": stage_name,
            "snapshot": task_copy
        })
        # 维持滑动窗口，最多保存 10 个历史快照
        if len(self.data["checkpoints"][task_id]) > 10:
            self.data["checkpoints"][task_id].pop(0)

    def create_task(
        self,
        task_id: str,
        title: str,
        desc: str = "",
        tier: int = 2,
        item_type: str = "TSK",
        priority: str = "HIGH",
        assignee: str = "pm",
        est_hours: float = 4.0,
        objective: str = "",
        collaborators: Optional[List[str]] = None,
        result: str = "",
        depends_on: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建新的需求或任务卡片。

        业务规则约束：
        1. 严格校验编号格式：REQ/TSK/SPK/FIX/DOC-xxxx(-xx)。
        2. 反洗牌铁律：已存在的任务严禁重复创建，杜绝通过重建卡片抹杀历史。
        3. 单一职责原则 (SRP)：Tier 2/3 单卡预估工时不得超过 8.0h，超出必须拆分为子任务。

        :param task_id: 工单编号 (如 TSK-1001, FIX-001)
        :param title: 工单简明标题
        :param desc: 工单详细说明
        :param tier: 分级网关级别 (0-3)
        :param item_type: 实体类型 (REQ, TSK, SPK, FIX, DOC)
        :param priority: 优先级 (CRIT, HIGH, MEDIUM, LOW)
        :param assignee: 初始指派角色 (默认 pm)
        :param est_hours: 预估工时 (小时数)
        :param objective: 明确立项目标
        :param collaborators: 协同参与专业角色列表
        :param result: 最终交付成果 (初始为空)
        :return: 创建成功的任务对象字典
        """
        task_id = task_id.strip()
        if not re.match(r"^(REQ|TSK|SPK|FIX|DOC)-\d{3,5}(-\d{2})?$", task_id):
            raise ValueError(f"Invalid Task ID format: '{task_id}'. Must match REQ/TSK/SPK/FIX/DOC-xxxx.")

        if task_id in self.data["tasks"]:
            raise ValueError(f"Task '{task_id}' already exists. Anti-escape rule: never recreate existing card.")

        # 核心研发卡片强制执行单一职责原则 (SRP)
        if tier in [2, 3] and est_hours > 8.0:
            raise ValueError(
                f"SRP Violation: Estimated hours ({est_hours}h) exceeds 8.0h threshold. "
                "Must decompose into multiple atomic tasks (e.g. TSK-xxxx-01, TSK-xxxx-02)."
            )

        obj = objective.strip() if objective else title
        desc_val = desc.strip() if desc else ""
        if not desc_val or len(desc_val) < 5:
            desc_val = (
                f"【业务需求背景与目标】:\n{obj}\n\n"
                f"【验收准则 (AC)】:\n"
                f"1. 核心功能特性与架构白名单契约严格对齐，禁止越权改动；\n"
                f"2. 具备独立自动化测试用例且回归全绿 (100% PASS)；\n"
                f"3. SAST 静态安全扫描与 AST 语法快筛 0 违规；\n"
                f"4. 活文档与代码架构地图保持同步更新。"
            )

        collabs = list(collaborators) if collaborators else []
        prof = ROLE_PROFILES.get(assignee, {"title": assignee, "icon": "📋", "scope": "需求定义"})
        now_str = datetime.now().isoformat()
        initial_contributions = [
            {
                "role": assignee,
                "title": prof.get("title", assignee),
                "icon": prof.get("icon", "📋"),
                "phase": "需求规划",
                "action": f"团队统筹立项，确立业务目标与交付基准，预估工时 {est_hours}h",
                "deliverable": f"{item_type} 规格契约卡片",
                "verdict": "CONFIRMED",
                "timestamp": now_str
            }
        ]
        for c in collabs:
            c_prof = ROLE_PROFILES.get(c, {"title": c, "icon": "👥", "scope": "专业协同"})
            initial_contributions.append({
                "role": c,
                "title": c_prof.get("title", c),
                "icon": c_prof.get("icon", "👥"),
                "phase": "协同立项",
                "action": f"联动参与协同：{c_prof.get('scope', '专项协同')}",
                "deliverable": "协同就绪",
                "verdict": "READY",
                "timestamp": now_str
            })

        task = {
            "id": task_id,
            "title": title,
            "objective": obj,
            "result": result,
            "description": desc_val,
            "desc": desc_val,
            "tier": tier,
            "type": item_type,
            "priority": priority,
            "stage": "BACKLOG",
            "assignee": assignee,
            "collaborators": collabs,
            "depends_on": list(depends_on) if depends_on else [],
            "role_contributions": initial_contributions,
            "est_hours": est_hours,
            "contract_checksum": None,
            "created_at": now_str,
            "started_at": None,
            "completed_at": None,
            "accepted_at": None,
            "lead_time_seconds": None,
            "deliverables": {
                "specs": [],
                "adr": [],
                "contracts": [],
                "source_files": [],
                "test_files": [],
                "reviews": [],
                "security_reports": [],
                "qa_reports": [],
                "receipts": []
            },
            "gate_status": {
                "gate_1_contract": False,
                "gate_2_review": False,
                "gate_3_security": False,
                "gate_4_testing": False,
                "gate_5_doc_sync": False,
                "gate_6_human_accept": False
            },
            "rejections": [],
            "history": [
                {
                    "timestamp": now_str,
                    "action": "CREATE",
                    "stage": "BACKLOG",
                    "role": assignee,
                    "note": f"Task created: {title} (Tier {tier}, {est_hours}h)"
                }
            ]
        }

        self.data["tasks"][task_id] = task
        self.data["metrics"]["total_created"] += 1
        self._record_checkpoint(task_id, "BACKLOG")
        self._log_event("TASK_CREATED", task_id, assignee, {"title": title, "tier": tier})
        self._save()
        return task

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        获取指定 ID 的任务对象。

        :param task_id: 工单编号
        :return: 任务数据字典
        :raises KeyError: 当工单不存在时抛出
        """
        if task_id not in self.data["tasks"]:
            raise KeyError(f"Task '{task_id}' does not exist on the board.")
        return self.data["tasks"][task_id]

    def start_task(self, task_id: str, role: str = "developer") -> Dict[str, Any]:
        """
        开始执行任务 / 认领工单 (Claim Work Order)，记录真实开始时间戳。

        领单核心物理硬门禁：
        1. 终态防篡改：已处于 ACCEPTED 或 CANCELLED 的工单严禁重新打开。
        2. 状态准入硬锁：工单必须处于可领取状态 (READY_TO_CLAIM, PENDING, CONTRACT_FROZEN, BACKLOG, REVISE)。
        3. 角色授权硬锁：只有 developer (或 pm/cto 特权) 可以认领。
        4. WIP 在制品并发硬锁：单开发者同一时刻只能持有一张 IN_PROGRESS 活跃工单 (WIP Limit = 1)。
        5. 前置依赖拓扑检查：若工单声明了 depends_on 前置依赖，依赖必须处于 ACCEPTED。

        :param task_id: 工单编号
        :param role: 领单角色 (通常为 developer)
        :return: 更新后的任务对象
        """
        task = self.get_task(task_id)
        if task["stage"] in ["ACCEPTED", "CANCELLED"]:
            raise ValueError(f"Task '{task_id}' is in terminal state '{task['stage']}'. Reopening forbidden.")

        # 1. 状态准入硬锁
        allowed_claim_stages = ["READY_TO_CLAIM", "PENDING", "CONTRACT_FROZEN", "BACKLOG", "REVISE"]
        if task["stage"] not in allowed_claim_stages:
            raise ValueError(
                f"工单领单拦截: 任务 '{task_id}' 当前处于 [{task['stage']}]，并非待领取状态 (允许阶段: {allowed_claim_stages})！"
            )

        # 2. 角色授权硬锁
        if role not in ["developer", "pm", "cto", "architect"]:
            raise PermissionError(
                f"工单领单拦截: 角色 '{role}' 无权认领研发工单，必须由核心研发工程师 (developer) 认领！"
            )

        # 3. WIP 在制品并发硬锁 (一人一单限制)
        if role == "developer":
            active_tasks = [
                t for tid, t in self.data["tasks"].items()
                if t.get("assignee") == role and t.get("stage") == "IN_PROGRESS" and tid != task_id
            ]
            if active_tasks:
                conflict_id = active_tasks[0]["id"]
                raise PermissionError(
                    f"WIP 在制品限制拦截: 开发者 '{role}' 当前已持有进行中工单 [{conflict_id}]！"
                    f"在单人单任务敏捷原则下，必须先交付或退单当前任务，方可认领新工单 (WIP Limit = 1)。"
                )

        # 4. 前置依赖拓扑检查
        for dep_id in task.get("depends_on", []):
            if dep_id in self.data["tasks"]:
                dep_task = self.data["tasks"][dep_id]
                if dep_task.get("stage") != "ACCEPTED":
                    raise ValueError(
                        f"前置依赖拦截: 依赖的前置工单 [{dep_id}] 尚未验收归档 (当前状态: [{dep_task.get('stage')}])，"
                        f"工单 [{task_id}] 物理锁定，严禁提前认领！"
                    )

        now_iso = datetime.now().isoformat()
        task["started_at"] = now_iso
        task["stage"] = "IN_PROGRESS"
        task["assignee"] = role
        task["history"].append({
            "timestamp": now_iso,
            "action": "START_WORK",
            "stage": "IN_PROGRESS",
            "role": role,
            "note": "Work order claimed and locked. Timestamp recorded for lead-time audit."
        })
        self._record_checkpoint(task_id, "IN_PROGRESS")
        self._log_event("TASK_STARTED", task_id, role, {"stage": "IN_PROGRESS"})
        self._save()
        return task

    def claim_task(self, task_id: str, role: str = "developer") -> Dict[str, Any]:
        """
        认领工单别名方法，与 start_task 等价。
        """
        return self.start_task(task_id, role)

    def surrender_task(self, task_id: str, role: str, reason: str) -> Dict[str, Any]:
        """
        主动退还工单 (Surrender Work Order)：
        当开发者评估因不可抗力或技术阻碍无法完成时，允许将工单退回待领池 (READY_TO_CLAIM)，
        清除独占锁定并记录原因，供其他开发者认领或由架构师重新梳理。

        :param task_id: 工单编号
        :param role: 操作角色 (必须是当前工单责任人)
        :param reason: 退单具体原因与技术障碍说明
        :return: 更新后的工单对象
        """
        task = self.get_task(task_id)
        if task["stage"] != "IN_PROGRESS":
            raise ValueError(f"退单拦截: 工单 [{task_id}] 当前处于 [{task['stage']}]，只有 [IN_PROGRESS] 状态方可退单。")
        if task.get("assignee") != role:
            raise PermissionError(f"退单拦截: 只有当前持单责任人 [{task.get('assignee')}] 有权退单，角色 [{role}] 无权操作。")

        now_iso = datetime.now().isoformat()
        task["stage"] = "READY_TO_CLAIM"
        task["assignee"] = None  # 释放持单责任人锁定，回归公海待领池
        task["started_at"] = None  # 重置开工时间戳
        task["history"].append({
            "timestamp": now_iso,
            "action": "SURRENDER_TASK",
            "stage": "READY_TO_CLAIM",
            "role": role,
            "note": f"Work order surrendered by {role}. Reason: {reason}"
        })
        self._record_checkpoint(task_id, "READY_TO_CLAIM")
        self._log_event("TASK_SURRENDERED", task_id, role, {"reason": reason})
        self._save()
        return task

    def advance_stage(
        self,
        task_id: str,
        target_stage: str,
        role: str,
        note: str = "",
        receipt_path: Optional[str] = None,
        result: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        推进任务至目标生命周期阶段。

        关键防作弊逻辑：
        1. Agent 严禁直接将任务设置为 'ACCEPTED'（该阶段只能由人类操作员在交互终端通过 vc-cli accept 赋予）。
        2. 防“秒冲刷”检测：从开始到完成不足 1 秒的操作将被标记为可疑盲目交付并在审计日志中告警。

        :param task_id: 工单编号
        :param target_stage: 目标阶段名称
        :param role: 推进该操作的执行角色
        :param note: 阶段流转附注说明
        :param receipt_path: 伴随的门禁凭证收据路径 (可选)
        :param result: 阶段产出或最终结论 (可选)
        :return: 更新后的任务对象
        """
        task = self.get_task(task_id)
        if target_stage not in STAGES:
            raise ValueError(f"Invalid target stage '{target_stage}'. Must be one of: {STAGES}")

        # 人类专属终态屏障：杜绝 Agent 擅自宣布验收成功
        if target_stage == "ACCEPTED":
            raise PermissionError(
                "Agent Forbidden: 'ACCEPTED' is a human-exclusive terminal stage. "
                "Use 'vc-cli accept' in an interactive terminal to verify and accept."
            )

        # 防“秒冲刷”审查：防止无脑点赞与未测试直接交单
        if target_stage == "COMPLETED":
            if task.get("started_at"):
                start_dt = datetime.fromisoformat(task["started_at"])
                duration = (datetime.now() - start_dt).total_seconds()
                task["lead_time_seconds"] = duration
                if duration < 1.0:
                    print(
                        f"[SECURITY ALERT] Second-rush detected for task {task_id} (duration: {duration:.2f}s)! "
                        "Flagged in audit log.", file=sys.stderr
                    )
            task["completed_at"] = datetime.now().isoformat()

        old_stage = task["stage"]

        # 1. 物理级角色权限与阶段跃迁硬校验
        perm = STAGE_PERMISSIONS.get(target_stage)
        if perm:
            if old_stage not in perm["from_stages"]:
                raise ValueError(
                    f"Invalid Stage Transition: Cannot advance task '{task_id}' from '{old_stage}' to '{target_stage}'. "
                    f"Allowed from stages: {perm['from_stages']}"
                )
            if role not in perm["allowed_roles"]:
                raise PermissionError(
                    f"Role Permission Denied: Role '{role}' cannot advance task to '{target_stage}'. "
                    f"{perm['err_msg']} (Allowed roles: {perm['allowed_roles']})"
                )

        # 2. 物理交付物与前置因果硬校验 (严格防止 AI 虚假宣称完成)
        # (a) 推进至 READY_TO_CLAIM (待领取 / 契约冻结)
        if target_stage in ["READY_TO_CLAIM", "CONTRACT_FROZEN"]:
            if not task.get("desc") or len(str(task.get("desc")).strip()) < 10:
                raise ValueError(
                    f"Precondition Failed: Task '{task_id}' has empty or insufficient Acceptance Criteria (AC). "
                    "PM must provide detailed AC before contract can be frozen."
                )
            specs_dir = self.root_dir / "docs" / "specs"
            if specs_dir.exists():
                found_spec = list(specs_dir.glob(f"*{task_id}*.md"))
                if not found_spec:
                    raise FileNotFoundError(
                        f"Missing Mandatory Deliverable: Architecture contract 'docs/specs/SPEC-{task_id}.md' not found! "
                        "Architect MUST freeze specification and scope whitelist before task is READY_TO_CLAIM."
                    )

        # (b) 推进至 SECURITY_AUDIT
        if target_stage == "SECURITY_AUDIT":
            rev_dir = self.root_dir / "docs" / "reviews"
            if rev_dir.exists():
                found_rev = list(rev_dir.glob(f"*{task_id}*.md"))
                if not found_rev:
                    raise FileNotFoundError(
                        f"Missing Mandatory Deliverable: Review report 'docs/reviews/REV-{task_id}.md' does not exist! "
                        "Code reviewer MUST write review findings before advancing to SECURITY_AUDIT."
                    )
        # (c) 推进至 TESTING
        elif target_stage == "TESTING":
            sec_dir = self.root_dir / "docs" / "security"
            if sec_dir.exists():
                found_sec = list(sec_dir.glob(f"*{task_id}*.md"))
                if not found_sec:
                    raise FileNotFoundError(
                        f"Missing Mandatory Deliverable: Security report 'docs/security/SEC-{task_id}.md' does not exist! "
                        "Security engineer MUST write security report before advancing to TESTING."
                    )
        # (d) 推进至 DOC_SYNC (质检小组三合一通关)
        elif target_stage == "DOC_SYNC":
            qa_dir = self.root_dir / "docs" / "qa"
            if qa_dir.exists():
                found_qa = list(qa_dir.glob(f"*{task_id}*.md"))
                if not found_qa:
                    raise FileNotFoundError(
                        f"Missing Mandatory Deliverable: QA report 'docs/qa/VERIFY-{task_id}.md' or 'QA-{task_id}.md' does not exist! "
                        "QA Board MUST run unified audit and write comprehensive verification report before advancing to DOC_SYNC."
                    )
                report_content = found_qa[0].read_text(encoding="utf-8")
                if "PASS" not in report_content and "通过" not in report_content and "100%" not in report_content:
                    raise ValueError(
                        f"Audit Failed: QA report '{found_qa[0].name}' does NOT indicate a PASS outcome! "
                        "Cannot advance to DOC_SYNC with failing tests or unverified status."
                    )
        # (e) 推进至 COMPLETED (活文档同步完成，待终审)
        elif target_stage == "COMPLETED":
            if role == "developer":
                raise PermissionError(
                    f"Permission Denied: Role 'developer' is strictly FORBIDDEN from setting task to 'COMPLETED'. "
                    "Only doc_engineer, devops, or qa_board can mark task as COMPLETED."
                )
            docs_dir = self.root_dir / "docs"
            if docs_dir.exists():
                proj_map = docs_dir / "PROJECT_STRUCTURE.md"
                if not proj_map.exists():
                    raise FileNotFoundError(
                        "Missing Mandatory Deliverable: AST Codebase Architecture Map 'docs/PROJECT_STRUCTURE.md' does not exist! "
                        "Doc Engineer MUST sync architecture map before completing task."
                    )

        task["stage"] = target_stage
        task["assignee"] = role
        if receipt_path and receipt_path not in task["deliverables"]["receipts"]:
            task["deliverables"]["receipts"].append(receipt_path)

        now_iso = datetime.now().isoformat()
        profile = ROLE_PROFILES.get(role, {"title": role, "icon": "👤", "scope": "阶段推进"})
        deliv = Path(receipt_path).name if receipt_path else f"{target_stage} 阶段验收成果"
        task.setdefault("role_contributions", []).append({
            "role": role,
            "title": profile.get("title", role),
            "icon": profile.get("icon", "👤"),
            "phase": target_stage,
            "action": note or f"推进工单阶段至 {target_stage}",
            "deliverable": deliv,
            "verdict": "PASS",
            "timestamp": now_iso
        })
        if result:
            task["result"] = result

        task["history"].append({
            "timestamp": now_iso,
            "action": "STAGE_ADVANCE",
            "from_stage": old_stage,
            "stage": target_stage,
            "role": role,
            "receipt": receipt_path,
            "note": note
        })
        self._record_checkpoint(task_id, target_stage)
        self._log_event("STAGE_ADVANCED", task_id, role, {"from": old_stage, "to": target_stage, "receipt": receipt_path})
        self._save()
        return task

    def generate_cto_arbitration_report(self, task_id: str, reason: str = "") -> str:
        """
        休眠 CTO 被唤醒：当任务因连续 3 次打回触发三阶硬熔断或陷入死锁时，
        调取全量不可变事件流与打回缺陷历史，进行根因深度剖析，输出仲裁诊断书并呈报人类管理员。

        :param task_id: 工单编号
        :param reason: 触发熔断的具体原因
        :return: 生成的仲裁报告相对路径
        """
        task = self.get_task(task_id)
        arb_dir = self.root_dir / "docs" / "arbitrations"
        arb_dir.mkdir(parents=True, exist_ok=True)
        arb_file = arb_dir / f"ARB-{task_id}.md"

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"# 【AegisFlow 首席技术官 (CTO) 仲裁诊断与风险通报书】",
            f"> **工单编号**: `{task_id}` | **生成时间**: `{now_str}` | **状态**: `BLOCKED (硬熔断挂起)`",
            "",
            "---",
            "",
            "## 1. 熔断态势与基本信息",
            f"- **任务标题**: {task.get('title', '')}",
            f"- **立项目标**: {task.get('objective', '')}",
            f"- **当前责任人**: `cto` (接管自 `{task.get('assignee', '')}`)",
            f"- **累计打回次数**: `{len(task.get('rejections', []))}` 次 (已触达三振出局硬熔断阈值)",
            "",
            "## 2. 缺陷打回轨迹深度复盘 (Defect Ledger)",
        ]

        for idx, rej in enumerate(task.get("rejections", []), start=1):
            lines.append(f"### 第 {idx} 次打回 · 标签: `{rej.get('tag', '')}`")
            lines.append(f"- **否决守卫**: `{rej.get('rejected_by', '')}` (类型: `#{rej.get('type', '')}`)")
            lines.append(f"- **打回原因**: {rej.get('reason', '')}")
            lines.append(f"- **回退流转**: `{rej.get('from_stage', '')}` ➔ `{rej.get('target_stage', '')}`")
            lines.append("")

        lines.extend([
            "## 3. CTO 根因深度剖析 (Root Cause Analysis)",
            "经 CTO 自动化审计调取执行日志与代码差异，本次研发陷入死锁的根本原因研判如下：",
            "1. **契约与实现偏差**: 研发代码实现可能偏离了最初架构师锁定的 `docs/specs/` 范围白名单或接口定义；",
            "2. **测试断言冲突**: 单元测试用例对边界条件的断言可能过于严苛，或测试代码与生产逻辑未同步更新；",
            "3. **AI 认知死锁**: 核心研发 Agent 陷入同一技术难点的循环尝试，未能有效吸收质检审查意见。",
            "",
            "## 4. 呈报人类管理员建议裁决方案 (Human Decision Required)",
            "为破除死锁，CTO 建议人类管理员在 Web 决策大盘采取以下措施：",
            f"- **方案 A (推荐 - 无损时光倒流)**: 执行 `python tools/vc_cli.py rollback --id {task_id} --stage READY_TO_CLAIM`，清除污染并由架构师重新调整方案；",
            "- **方案 B (人工降级核准)**: 人类管理员直接审阅当前代码，确认可容忍偏差后在 Web 界面执行终审验收；",
            f"- **方案 C (终止废弃)**: 若该需求技术路线已被证明不可行，执行 `python tools/vc_cli.py advance --id {task_id} --stage CANCELLED` 关单。",
            "",
            "---",
            "*报告签发: AegisFlow 首席技术官 (CTO) 仲裁委员会*"
        ])

        report_content = "\n".join(lines)
        with open(arb_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        task["arbitration_report"] = report_content
        task["arbitration_report_path"] = str(arb_file.relative_to(self.root_dir))
        return str(arb_file.relative_to(self.root_dir))

    def reject_task(
        self,
        task_id: str,
        role: str,
        reject_type: str,
        reason: str,
        target_stage: str = "IN_PROGRESS"
    ) -> Dict[str, Any]:
        """
        执行专业制衡打回（行使一票否决权）。

        打回核心机制：
        1. 打回继承原工单编号：生成例如 TSK-1001#QR-1 的全局唯一打回标签。
        2. 三振出局熔断机制 (Circuit Breaker)：累计打回达到 3 次时，任务自动锁定为 'BLOCKED'，
           并强制指派给 CTO 深度诊断生成报告，呈报人类仲裁官处理，彻底杜绝死循环。

        :param task_id: 工单编号
        :param role: 否决角色 (qa_board, code_reviewer, security_engineer, qa_engineer, doc_engineer)
        :param reject_type: 否决类别 (QR:质量, SR:安全, FR:功能, DR:文档)
        :param reason: 详细否决原因与整改要求
        :param target_stage: 打回回滚的目标阶段 (默认为 IN_PROGRESS)
        :return: 更新后的任务对象
        """
        task = self.get_task(task_id)
        if reject_type not in REJECT_TYPES:
            raise ValueError(f"Invalid reject type '{reject_type}'. Must be one of: {REJECT_TYPES} (QR/SR/FR/DR)")

        rejection_idx = len(task["rejections"]) + 1
        reject_tag = f"{task_id}#{reject_type}-{rejection_idx}"
        
        now_iso = datetime.now().isoformat()
        rejection_entry = {
            "tag": reject_tag,
            "timestamp": now_iso,
            "rejected_by": role,
            "type": reject_type,
            "iteration": rejection_idx,
            "from_stage": task["stage"],
            "target_stage": target_stage,
            "reason": reason
        }
        task["rejections"].append(rejection_entry)
        self.data["metrics"]["total_rejections"] += 1

        profile = ROLE_PROFILES.get(role, {"title": role, "icon": "🛡️", "scope": "质量制衡"})
        task.setdefault("role_contributions", []).append({
            "role": role,
            "title": profile.get("title", role),
            "icon": profile.get("icon", "🛡️"),
            "phase": f"#{reject_type} 质检否决",
            "action": f"行使一票否决权打回：{reason}",
            "deliverable": f"驳回整改单 {reject_tag}",
            "verdict": "REJECTED",
            "timestamp": now_iso
        })

        # 三振出局熔断协议：累计 3 次驳回触发强锁定并唤醒 CTO 诊断
        if len(task["rejections"]) >= 3:
            task["stage"] = "BLOCKED"
            task["assignee"] = "cto"
            self.data["metrics"]["circuit_breakers_triggered"] += 1
            # 自动唤醒 CTO 生成诊断报告
            arb_path = self.generate_cto_arbitration_report(task_id, reason)
            action_note = (
                f"CIRCUIT BREAKER TRIGGERED ({len(task['rejections'])} rejections)! "
                f"Task locked as BLOCKED. CTO awakened and generated arbitration diagnosis: {arb_path}"
            )
        else:
            task["stage"] = target_stage
            task["assignee"] = "developer"
            action_note = f"Rejection {reject_tag} by {role} ({reject_type}): {reason} -> Rollback to {target_stage}"

        task["history"].append({
            "timestamp": now_iso,
            "action": "REJECT",
            "tag": reject_tag,
            "stage": task["stage"],
            "role": role,
            "note": action_note
        })
        self._record_checkpoint(task_id, task["stage"])
        self._log_event("TASK_REJECTED", task_id, role, {"tag": reject_tag, "reason": reason, "stage": task["stage"]})
        self._save()
        return task

    def rollback_to_checkpoint(self, task_id: str, target_stage: str) -> Dict[str, Any]:
        """
        LangGraph 风格时光倒流 (Time-Travel)：
        将工单状态精准回滚到历史上匹配 target_stage 的最近一个安全检查点。

        :param task_id: 工单编号
        :param target_stage: 回滚目标阶段
        :return: 恢复后的任务快照对象
        """
        task = self.get_task(task_id)
        checkpoints = self.data.get("checkpoints", {}).get(task_id, [])
        if not checkpoints:
            raise ValueError(f"No checkpoints found for task '{task_id}'.")

        matched = None
        for cp in reversed(checkpoints):
            if cp["stage"] == target_stage:
                matched = cp
                break

        if not matched:
            raise ValueError(f"No checkpoint found matching stage '{target_stage}'.")

        snapshot = json.loads(json.dumps(matched["snapshot"]))
        snapshot["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "TIME_TRAVEL_ROLLBACK",
            "stage": target_stage,
            "role": "cto",
            "note": f"Time-travel rollback restored task to checkpoint at [{target_stage}]"
        })
        self.data["tasks"][task_id] = snapshot
        self._log_event("TIME_TRAVEL_ROLLBACK", task_id, "cto", {"target_stage": target_stage})
        self._save()
        return snapshot

    def accept_task(
        self,
        task_id: str,
        accepted_by: str = "HUMAN_OPERATOR",
        note: str = "",
        result: str = ""
    ) -> Dict[str, Any]:
        """
        Gate 6 人类终审验收方法。
        仅允许针对处于 'COMPLETED' 状态的工单生效，赋予不可逆终态 'ACCEPTED'。

        :param task_id: 工单编号
        :param accepted_by: 人类操作员标识
        :param note: 最终验收评语
        :param result: 最终交付成果总结 (可选)
        :return: 终态锁定的任务对象
        """
        task = self.get_task(task_id)
        if task["stage"] != "COMPLETED":
            raise ValueError(
                f"Task '{task_id}' cannot be accepted: current stage is '{task['stage']}'. "
                "Must be in 'COMPLETED' stage."
            )

        now_iso = datetime.now().isoformat()
        task["stage"] = "ACCEPTED"
        task["accepted_at"] = now_iso
        task["gate_status"]["gate_6_human_accept"] = True
        self.data["metrics"]["total_accepted"] += 1

        final_res = result or note or "全生命周期质量门禁全绿通过，人类管理员终审核准放行并归档。"
        task["result"] = final_res
        task.setdefault("role_contributions", []).append({
            "role": "human_operator",
            "title": "人类管理员",
            "icon": "👑",
            "phase": "终审归档",
            "action": f"行使人类主权终审放行：{final_res}",
            "deliverable": "项目全量封板归档",
            "verdict": "ACCEPTED",
            "timestamp": now_iso
        })

        task["history"].append({
            "timestamp": now_iso,
            "action": "HUMAN_ACCEPT",
            "stage": "ACCEPTED",
            "role": accepted_by,
            "note": note or "Final business acceptance granted by Human Operator."
        })
        self._record_checkpoint(task_id, "ACCEPTED")
        self._log_event("TASK_ACCEPTED", task_id, accepted_by, {"note": note, "result": final_res})
        self._save()
        return task

    def list_tasks(
        self,
        stage: Optional[str] = None,
        active_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        列出任务看板中的工单，支持按阶段筛选、活跃过滤及数量截断。

        :param stage: 指定阶段筛选 (可选)
        :param active_only: 为 True 时仅返回非终态工单 (排除 ACCEPTED 和 CANCELLED)
        :param limit: 最大返回条数 (可选)
        :return: 任务列表，按更新时间倒序排序
        """
        tasks = list(self.data["tasks"].values())
        if stage:
            tasks = [t for t in tasks if t["stage"] == stage]
        if active_only:
            tasks = [t for t in tasks if t["stage"] not in ["ACCEPTED", "CANCELLED"]]

        tasks.sort(key=lambda t: t.get("updated_at", t.get("created_at", "")), reverse=True)
        if limit:
            tasks = tasks[:limit]
        return tasks

    def get_top5_active(self) -> List[Dict[str, Any]]:
        """
        防 Token 膨胀 (Anti-Token Bleed) Top-5 原则：
        仅返回最近活跃的最多 5 个任务，专供终端和 Agent 上下文消费。

        :return: 最多 5 条活跃工单
        """
        return self.list_tasks(active_only=True, limit=5)

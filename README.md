<div align="center">

# 🛡️ AegisFlow · 神盾微内核
### 专为多 Agent 智能体工程打造的确定性研发治理与物理门禁微内核
**Deterministic Governance, Anti-Collusion Physical Gates & Cryptographic Receipts for Multi-Agent Software Engineering**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-48%2F48%20passed%20(100%25)-success.svg?style=flat-square)](tests/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20external%20(std%20library%20only)-orange.svg?style=flat-square)](tools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![Governance](https://img.shields.io/badge/Architecture-Deterministic%20Microkernel-purple.svg?style=flat-square)](#)

<p align="center">
  <b>“绝不轻信 AI 的提示词，用操作系统级物理硬隔离与密码学收据治理智能体”</b><br>
  <i>"Don't trust Agent prompts. Restrain them with OS-level physical sandboxes, deterministic state machines, and cryptographic receipts."</i>
</p>

</div>

---

## 📖 目录 (Table of Contents)

- [🔥 为什么需要 AegisFlow？(痛点与行业现实)](#-为什么需要-aegisflow痛点与行业现实)
- [⚔️ 架构对比：AegisFlow vs 传统 Multi-Agent 框架](#️-架构对比aegisflow-vs-传统-multi-agent-框架)
- [🏛️ 核心架构与底层哲学](#️-核心架构与底层哲学)
- [🛡️ 六重确定性质量门禁 (Gate 1 - Gate 6)](#️-六重确定性质量门禁-gate-1---gate-6)
- [👥 11 大标准角色协同矩阵 (常驻骨干 + 触发式切面)](#-11-大标准角色协同矩阵-常驻骨干--触发式切面)
- [🖥️ 面向人类管理者的 Web 离线敏捷大盘](#️-面向人类管理者的-web-离线敏捷大盘)
- [🚀 快速开始 (Quick Start)](#-快速开始-quick-start)
- [🛠️ CLI 工具链命令行矩阵 (`vc_cli.py`)](#️-cli-工具链命令行矩阵-vc_clipy)
- [📁 模块目录结构规范](#-模块目录结构规范)
- [📜 开源许可证 (License)](#-开源许可证-license)

---

## 🔥 为什么需要 AegisFlow？(痛点与行业现实)

当前以 MetaGPT、ChatDev、CrewAI 为代表的传统 Multi-Agent 框架，在复杂严肃的软件工程落地中普遍遭遇了**三大致命软肋**：

1. **群体合谋与谄媚 (Groupthink & Collusion)**：
   让多个 Agent 互相 Review 代码，Agent 之间极易陷入“秒级互相吹捧”——审查员不看代码直接回复 *“LGTM! 代码优雅无缺陷”*，导致严重漏洞与死循环直接带入生产环境。
2. **AI 提示词不可信与测试作弊 (Prompt Untrustworthiness & Anti-Cheating)**：
   **提示词是软弱无力的。** 在 Prompt 里写 *“请不要修改测试用例”* 根本无法阻止 Agent。当单元测试报错时，大模型最常见的作弊手段就是**直接去改 `tests/` 目录下的断言，甚至改成 `assert True` 蒙混过关**。
3. **Token 灾难与虚拟办公室幻觉 (Token Bleed & Conference Hallucination)**：
   传统框架喜欢让 5~10 个角色在线拉群开会，无论需求多小都在互相客套、长篇大论，消耗数十万 Token，却写不出一行健壮的代码。

**AegisFlow 彻底打破“拟人化办公过家家”的伪需求**，将系统重构为一个**确定性代码合规守门人与密码学审计流水线**。

---

## ⚔️ 架构对比：AegisFlow vs 传统 Multi-Agent 框架

| 治理维度 | 传统 Multi-Agent 框架 (MetaGPT/ChatDev等) | AegisFlow 神盾代码治理微内核 |
| :--- | :--- | :--- |
| **底层约束** | 脆弱的 Prompt 自然语言约定 (容易幻觉与越权) | **操作系统级物理沙盒与路径隔离 (OS-Level Hard Block)** |
| **测试真实性** | LLM 在上下文内“心算”或“脑补”测试结果 | **真实独立 Subprocess 子进程拉起测试套件，核验 Exit Code** |
| **权限防作弊** | 角色全目录读写，开发者经常篡改测试断言 | **开发者物理只读 `tests/`；QA 物理只读 `src/`；越权直接抛异常** |
| **质量依据** | 聊天文本中的 “Pass/LGTM” 字符串 | **签发不可篡改的密码学凭据 (`REC-*.json`，含 SHA256 摘要)** |
| **容错机制** | 无限轮次聊天重试，直到 Token 耗尽或报错 | **三振出局硬熔断 (Circuit Breaker) + LangGraph 时光倒流** |
| **人类在环** | 旁观聊天记录，缺乏真实物理确认节点 | **真实控制台 TTY 物理锁 (Gate 6) + 现代化 Web 终审放行** |
| **依赖与开销** | 依赖庞大复杂的 SDK、第三方框架与在线环境 | **Python 标准库 0 外部依赖，离线断网 100% 完整可用** |

---

## 🏛️ 核心架构与底层哲学

```
                    ┌──────────────────────────────────────────────┐
                    │          用户请求 (自然语言指令 / 业务需求)     │
                    └──────────────────────┬───────────────────────┘
                                           │
                                  [三维风险网关分流]
                                           │
               ┌───────────────────────────┼───────────────────────────┐
               ▼                           ▼                           ▼
        【L0: 无状态分析】           【L1: 微修与探针】           【L2/L3: 核心特性/架构】
        只读问答/架构解释            单文件修复/调研探针          跨文件研发/核心重构/DB
        [0工单 0门禁 0延迟]         [免契约 / G2+G4直通]         [全量六重确定性门禁]
                                                                       │
┌──────────────────────────────────────────────────────────────────────┴───────────────────────────────────┐
│                                   AegisFlow 六重确定性质量门禁流水线                                      │
│                                                                                                          │
│  [Gate 1: 契约锁定] ──► [Gate 2: 规范快筛] ──► [Gate 3: 安全防护] ──► [Gate 4: 动态回归] ──► [Gate 5/6: 文档&人类] │
│   SHA256边界锁定          AST毫秒快筛+提交规范      SAST扫描+密钥零泄露      1:1镜像单测100%全通      RepoMap同步+人类终审 │
│   签发: REC-G1收据        签发: REC-G2收据          签发: REC-G3收据        签发: REC-G4收据        签发: REC-G5/G6收据   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ 六重确定性质量门禁 (Gate 1 - Gate 6)

每个门禁均为可独立执行、机器自动判定的确定性检查器，验证通过后签发包含时间戳与哈希凭据的不可篡改收据（`REC-*.json`）：

1. **Gate 1: 架构契约与语义边界锁定 (Contract Lock)**
   - 提取任务目标范围与白名单（`in_scope`），计算 SHA-256 签名冻结契约。严禁 Agent 在白名单外肆意修改无关文件。
2. **Gate 2: AST 语法快筛与中文提交规范 (Static Verification)**
   - 毫秒级遍历 Python 抽象语法树（AST），拦截语法断裂与缩进错位；
   - 强制 Conventional Commits 中文规范校验（如 `feat(auth): ...`）。
3. **Gate 3: 独立安全审计与敏感词筛查 (Security Hardening)**
   - SAST 扫描硬编码 API 密钥、数据库明文口令、RSA 私钥及危险代码执行（`eval/exec`）；
   - 安全审计员拥有一票否决权（`#SR`），高危漏洞直接挂起流水线。
4. **Gate 4: 自动化测试闭环与镜像一致性 (Dynamic Regression)**
   - 在独立操作系统子进程中运行测试套件（`pytest` / `unittest`），必须 100% 全绿通过；
   - 强制核验 `src/` 与 `tests/` 1:1 镜像对齐。QA 拥有功能一票否决权（`#FR`）。
5. **Gate 5: 活文档与代码结构地图同步 (Knowledge Sync)**
   - 基于 AST 解析动态刷新 Aider 风格代码架构地图（`docs/PROJECT_STRUCTURE.md`）；
   - 活文档工程师拥有一票否决权（`#DR`），拒绝“代码已改、文档过时”。
6. **Gate 6: 人类物理终审主权 (Human Authority Gate)**
   - 物理级检测真实控制台交互终端（`sys.stdin.isatty()`）；
   - 必须由人类操作员在键盘敲击确认或在 Web 界面签署，工单方可封板归档为不可逆的 `ACCEPTED` 状态。

---

## 👥 11 大标准角色协同矩阵 (常驻骨干 + 触发式切面)

AegisFlow 拒绝让 11 个角色排队开会。角色被设计为**常驻核心骨干**与**触发式切面守卫**，实现极致的 Token 节约：

| 角色标识 | 角色全称 | 核心定位与职责边界 | 生命周期触达阶段 | 核心交付产物与防线 |
| :--- | :--- | :--- | :--- | :--- |
| **pm** | **团队负责人 / 产品主理人 📋** | **团队全面统筹**、业务立项目标拟定、全生命周期管控与验收指标（AC）细化 | `BACKLOG` ➔ `SPECIFICATION` | 业务需求清单、验收准则边界 |
| **architect** | 系统架构师 🏛️ | 语义边界白名单圈定、SHA256 契约签名计算与 G1 门禁锁定 | `SPECIFICATION` ➔ `CONTRACT_FROZEN` | G1 架构契约收据、文件白名单 |
| **uiux_designer** | UI/UX体验设计师 🎨 | *(切面激活)* 界面视觉走查、深色磨砂材质对齐、去原生控件、防溢出审查 | `CONTRACT_FROZEN` ➔ `IN_PROGRESS` | 前端组件规范、设计走查报告 |
| **dba** | 数据库管理员 🗄️ | *(切面激活)* 数据模式演进审查、迁移脚本合规性评估、可逆 DDL 验证 | `IN_PROGRESS` (涉及数据库时) | DDL 脚本审计意见、回滚方案 |
| **developer** | 核心研发工程师 💻 | 范围白名单内精准实现、单元测试自编写、中文提交规范 | `IN_PROGRESS` ➔ `CODE_REVIEW` | 业务源码、单测代码、Git Commit |
| **code_reviewer** | 代码审查员 🔍 | AST 抽象语法树遍历快筛、Conventional Commits 校验（拥有 `#QR` 否决权） | `CODE_REVIEW` ➔ `SECURITY_AUDIT` | G2 语法评审收据、`#QR` 审查意见 |
| **security_engineer** | 独立安全审计员 🛡️ | SAST 静态机密扫描、SQL 拼接与 OWASP 漏洞排查（拥有 `#SR` 否决权） | `SECURITY_AUDIT` ➔ `TESTING` | G3 安全审计收据、`#SR` 漏洞拦截单 |
| **qa_engineer** | 质量验证测试员 🧪 | 1:1 镜像测试环境自适应执行、全量断言通过率核验（拥有 `#FR` 否决权） | `TESTING` ➔ `DOC_SYNC` | G4 动态测试收据、`#FR` 缺陷打回单 |
| **doc_engineer** | 活文档工程师 📚 | Aider 风格 AST 代码架构地图维护、API 与实现同步审查（拥有 `#DR` 否决权） | `DOC_SYNC` ➔ `COMPLETED` | G5 活文档同步收据、`#DR` 差异记录 |
| **release_engineer** | 发布协调主管 🚀 | 全绿工单版本集成打包、跨角色交付物一致性核查与上线准备 | `COMPLETED` 封包 | 待发布版本包、全流程履职汇总单 |
| **cto** | 首席技术仲裁官 ⚖️ | *(切面激活)* 三振出局硬熔断介入仲裁、时空快照时光倒流与架构冲突裁决 | `BLOCKED` 状态唤醒 | 熔断仲裁决策书、时光倒流指令 |
| **human_operator** | 人类管理员 👑 | 物理真实控制台终审（Gate 6）、业务目标最终验收、不可逆封板归档 | `ACCEPTED` (终态) | 人类物理签字收据、项目封板档案 |

---

## 🖥️ 面向人类管理者的 Web 离线敏捷大盘

AegisFlow 内置了基于 Python 原生 `http.server` 的**零外部依赖离线 Web 看板**（监听本地 `8848` 端口）：

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  TSK-1001 · 实现JWT用户鉴权服务   [HIGH]  [已验收归档]                             ✕  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  🎯 业务立项目标 (Target Objective)        │  🏁 交付成果与最终结论 (Result & Impact)      │
│  为全站提供高可用非对称加密JWT鉴权，杜绝硬编码... │  六重质量门禁已全部闭环，已由人类终审放行归档。  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  🚩 研发生命周期全流程管控 (5-Stage Visual Stepper)                                     │
│  (✓) 契约锁定  ➔  (✓) 编码实现  ➔  (✓) 规范与安全  ➔  (✓) 单测文档  ➔  (✓) 人类终审      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  👥 全角色协同履职矩阵 (Role Responsibility & Action Matrix)                           │
│  [📋 团队负责人 PM]  [🏛️ 系统架构师]  [💻 核心研发]  [🔍 代码审查]  [🛡️ 安全审计]  [🧪 QA测试]   │
│  • 16:21 [需求规划] 团队负责人: 团队统筹立项，确立业务目标，设定预估工时 4.0h            │
│  • 16:22 [架构契约] 系统架构师: 签署 SHA256 契约锁定文件白名单                          │
│  • 16:23 [自动化测] 质量测试员: 执行单测套件 100% 全绿通过 (签发 REC-G4 收据)             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  📑 人类可读质检通关报告书 (拒绝技术乱码 JSON，通俗指标直达管理层)                        │
│  [G1: 架构契约范围] ✅ 已通关    [G2: AST语法快筛] ✅ 已通关    [G3: 密钥安全审计] ✅ 0 泄露   │
│  [G4: 自动化单测回归] ✅ 100%通关  [G5: 架构文档对齐] ✅ 已同步    [G6: 人类管理员终审] ✅ 已封板 │
│  └─ [▶ 展开底层机器密码学凭证 (JSON) 用于技术审计]                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  🚫 质检打回与历史缺陷档案 (保留缺陷基因，三阶熔断风控)                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  工单状态：已验收归档                                            [关闭详情]            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **960px 宽度大气居中模态弹窗**，彻底杜绝横向滚动条；
- **纯原生自适应深色磨砂材质**，剔除所有操作系统白底默认下拉与输入框；
- **业务目标与交付结论一等公民置顶**，人类管理者无需敲代码，专注于进度监督与验收决策。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备
**零外部三方 pip 依赖**，标准 Python 3.10+ 原生驱动：

```bash
# 1. 克隆代码仓库
git clone https://github.com/your-username/aegisflow.git
cd aegisflow

# 2. 执行全量单元测试套件 (48 项全绿通过)
python -m unittest discover tests
```

### 2. 安装物理 Git Pre-commit 防作弊门禁
```bash
# 安装物理钩子 (无工单禁止提交、根目录散落文件物理阻断)
python tools/vc_cli.py hook install
python tools/vc_cli.py hook verify
```

### 3. 启动离线管理大盘
```bash
# 启动本地零依赖看板服务 (默认端口 8848)
python tools/vc_cli.py web --port 8848

# 浏览器访问：http://localhost:8848/
```

---

## 🛠️ CLI 工具链命令行矩阵 (`vc_cli.py`)

AegisFlow 提供了 17 个高内聚管理子命令：

```bash
# 1. 自适应技术栈嗅探 (自动识别 Python/Node/Go/Rust/Java 并持久化配置)
python tools/vc_cli.py detect

# 2. 物理 Pre-commit 钩子管理
python tools/vc_cli.py hook install
python tools/vc_cli.py hook verify

# 3. 运行健康巡检大盘 (停滞任务预警与熔断风险评估)
python tools/vc_cli.py heartbeat

# 4. 终端敏捷看板 (Top-5 防 Token 膨胀保护)
python tools/vc_cli.py board

# 5. 团队负责人 (PM) 创建新工单
python tools/vc_cli.py create --id TSK-1001 --title "实现JWT鉴权" --tier 2 --hours 4.0 --assignee pm

# 6. 开发者领单开工
python tools/vc_cli.py start --id TSK-1001 --role developer

# 7. 毫秒级 AST 语法快筛
python tools/vc_cli.py lint --target src

# 8. 六重确定性质量门禁核验 (签发密码学收据 REC-*.json)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_2_review --commit-msg "feat(auth): 实现JWT鉴权"
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_3_security
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_4_testing
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_5_doc_sync

# 9. 行使一票否决打回 (QR/SR/FR/DR)
python tools/vc_cli.py reject --id TSK-1001 --role security_engineer --type SR --reason "发现硬编码Token密钥"

# 10. 时光倒流回滚 (恢复到历史检查点)
python tools/vc_cli.py rollback --id TSK-1001 --stage IN_PROGRESS

# 11. 仓库纯洁度与 1:1 测试镜像体检
python tools/vc_cli.py hygiene

# 12. 人类专属物理终审验收 (Gate 6 - 真实 TTY 交互)
python tools/vc_cli.py accept --id TSK-1001 --by "人类管理员"
```

---

## 📁 模块目录结构规范

```text
├── docs/                       # 架构、契约、规格与活文档目录
│   ├── adr/                    # 架构决策记录 (ADR-xxxx.md)
│   ├── contracts/              # 机器可读 JSON Schema 契约 (SPEC-xxxx.json)
│   ├── specs/                  # 需求规范与 AC (REQ-xxxx.md)
│   └── PROJECT_STRUCTURE.md    # Aider 风格 AST 代码结构地图
├── src/                        # 业务生产代码 (开发者主控，架构/测试严禁写入)
├── tests/                      # 自动化测试用例 (QA 独立主控，开发者严禁篡改)
├── tools/                      # AegisFlow 微内核与工具链
│   ├── vc_cli.py               # 统一 17 个子命令 CLI 交互入口
│   ├── state_manager.py        # 状态机、熔断器、检查点快照与履职矩阵
│   ├── gatekeeper.py           # 质量门禁执行器与密码学收据引擎
│   ├── repo_hygiene.py         # 零污染检查器与 AST RepoMap 生成器
│   ├── git_hook.py             # 操作系统级物理 Git 钩子管理
│   ├── heartbeat.py            # 工坊运行健康监视与风险巡检器
│   ├── stack_sniffer.py        # 多语言技术栈自动快筛嗅探器
│   ├── board_renderer.py       # 终端 ANSI Top-5 看板渲染器
│   ├── kanban_server.py        # 零依赖本地 Web 服务器
│   └── web/                    # 离线单文件现代化 Web 看板 (index.html)
└── .agents/                    # 治理与审计数据 (系统内部状态)
    ├── skills/virtual-company/ # Antigravity Skill 技能定义包
    │   ├── SKILL.md            # 技能元数据、响应分流协议与履职矩阵
    │   ├── core_config.yaml    # 熔断阈值与风控准则
    │   ├── manifests/          # 7 大守卫声明清单
    │   ├── doctrines/          # 代码合规法典与人类终审主权协议
    │   └── roles/              # 11 大角色职责定义
    ├── receipts/               # 门禁不可篡改收据 (REC-*.json)
    ├── event_stream.jsonl      # OpenHands 风格不可变事件流
    └── .virtual_company_board.json # 看板持久化状态与检查点
```

---

## 📜 开源许可证 (License)

本项目遵循 [MIT 许可证](LICENSE)。
欢迎提交 Issue 与 Pull Request，共同构建更具确定性与工程纪律的 Agent 研发基础设施！

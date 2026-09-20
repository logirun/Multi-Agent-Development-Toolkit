---
name: virtual-company
description: AegisFlow 神盾代码治理与多Agent确定性门禁系统。提供包含六重确定性质量门禁（Gate 1-6）、四维独立制衡否决（#QR/#SR/#FR/#DR）、密码学收据链（REC-*.json）、时空快照时光倒流与三阶硬熔断的完整研发治理微内核。
---

# AegisFlow · 神盾代码治理与多Agent确定性门禁系统 (AegisFlow Kernel)

## 1. 系统定位与核心架构
AegisFlow 是面向先进智能体软件工程的**确定性研发治理微内核（Deterministic Governance Microkernel）**。
与传统模拟“软件外包公司/办公室角色扮演”的流程框架截然不同，AegisFlow 不搞拟人化的人际汇报与形式主义流转，而是以**“代码即契约，门禁即法度，收据即真相”**为底层哲学，将系统打造为一个**代码合规守门人与密码学审计流水线**。

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

## 2. 三维风险网关 (Risk-Weighted Gate Matrix)

根据代码变更对系统的潜在破坏性与范围，将任务划分为四个客观风险级别：

| 风险级别 | 适用特征与场景 | 工单形态 | 门禁准入要求 | 核心产出凭证 |
| :--- | :--- | :--- | :--- | :--- |
| **L0 (Probe 探针级)** | 静态代码分析、文件阅读、架构咨询、排查定位 | **免建工单** | 无门禁阻断，秒级直答 | 纯分析结论 |
| **L1 (Patch 微修级)** | 单文件轻量缺陷修复、依赖版本微调、文档修饰 (< 2.0h) | `FIX-xxxx` | **Gate 2** (语法快筛) + **Gate 4** (单测回归) | 源码 + 测试用例 |
| **L2 (Feature 标准级)**| 跨模块业务特性研发、多文件重构 (2.0h - 8.0h) | `TSK-xxxx` | **Gate 1 至 Gate 6 全量闭环** | 全套代码 + 六重密码学收据 |
| **L3 (Critical 核心级)**| 数据库 DDL 迁移、鉴权加固、底层微内核升级 | `TSK-xxxx` | **全量门禁 + 强制编写 ADR 架构决策** | ADR + 可逆 DDL + 密码学收据 |

### 2.1 交互分流声明协议 (Mandatory Response Header)
在每一次对话响应的首部，Agent 必须以统一规范输出响应层级与协同矩阵，向人类直观汇报当前响应的定位：
```markdown
【AegisFlow 响应分流: LX - 分流名称】
- 判定依据: <为什么判定为此层级>
- 牵头角色: <本轮主要执行角色与图标>
- 协同角色: <参与本次任务的协同角色列表>
- 立项目标: <本次任务的核心业务/技术目标>
- 交付结果: <本轮交付的具体产物或分析结论>
```

---

## 3. 六重确定性质量门禁引擎 (Deterministic Gates)

每个门禁均为可独立执行、机器判定的确定性检查器，验证通过即签发不可篡改的密码学收据（`REC-*.json`）：

1. **Gate 1: 架构契约与语义边界锁定 (Contract Lock)**
   - 提取任务目标范围与验收标准，计算 SHA-256 签名，锁定开发人员修改白名单（`in_scope`）。
   - 签发凭证：`REC-<TaskID>-GATE_1_CONTRACT-PASS.json`。
2. **Gate 2: AST 语法快筛与中文提交规范 (Static Verification)**
   - 毫秒级遍历 Python 抽象语法树（AST），拦截括号断裂与缩进错位；
   - 校验中文 Conventional Commits 提交格式（如 `feat(模块): 描述`）。
   - 签发凭证：`REC-<TaskID>-GATE_2_REVIEW-PASS.json`。
3. **Gate 3: 独立安全审计与敏感词筛查 (Security Hardening)**
   - 自动执行 SAST 静态分析，扫描硬编码 API 密钥、数据库明文口令、RSA 私钥及 SQL 拼接注入。
   - 独立安全审计员拥有一票否决权（`#SR`），高危漏洞直接挂起流水线。
   - 签发凭证：`REC-<TaskID>-GATE_3_SECURITY-PASS.json`。
4. **Gate 4: 自动化测试闭环与镜像一致性 (Dynamic Regression)**
   - 自适应嗅探多语言测试运行器（`pytest`, `unittest`, `jest`, `go test`, `cargo test`）；
   - 强制核验 `src/` 与 `tests/` 1:1 镜像对齐，测试用例必须 100% 全绿通过。
   - 签发凭证：`REC-<TaskID>-GATE_4_TESTING-PASS.json`。
5. **Gate 5: 活文档与代码结构地图同步 (Knowledge Sync)**
   - 基于 AST 解析自动刷新 Aider 风格代码架构地图（`docs/PROJECT_STRUCTURE.md`）；
   - 校验接口文档与生产代码修改时间戳一致性，拒绝“代码已改、文档过时”。
   - 签发凭证：`REC-<TaskID>-GATE_5_DOC_SYNC-PASS.json`。
6. **Gate 6: 人类物理终审主权 (Human Authority Gate)**
   - 系统物理级检测真实控制台交互终端（`sys.stdin.isatty()`）；
   - 必须由人类操作员在键盘上输入 `y` 最终确认，工单封板转入不可逆的 `ACCEPTED` 状态。

---

## 4. 微内核容错与防御体系

1. **四维正交一票否决权**：
   - 规范与架构制衡（`#QR`）、安全合规制衡（`#SR`）、功能回归制衡（`#FR`）、活文档同步制衡（`#DR`）。
   - 任何否决均在原工单追溯链上追加记录（如 `TSK-1001#QR-1`），严禁新建工单抹杀历史。
2. **三阶硬熔断 (Circuit Breaker)**：
   - 累计打回达到 3 次，工单底层自动锁定为 `BLOCKED`，剥夺智能体修改权限，挂起等待 CTO / 人类介入仲裁。
3. **时空快照与时光倒流 (Time-Travel Rollback)**：
   - 借鉴 LangGraph 检查点思想，状态迁移自动深拷贝工单全量快照，遇灾难性偏差时可一键时间旅行回退至历史健康节点。
4. **物理 Pre-commit 门禁**：
   - 仓库级物理拦截：无活跃工单直接阻断 `git commit`；根目录下存在散落游离文件直接阻断 `git commit`。

---

## 5. 核心管理 CLI 命令行矩阵 (`tools/vc_cli.py`)

```bash
# 1. 自适应技术栈嗅探 (自动识别主语言、推荐测试命令并持久化画像)
python tools/vc_cli.py detect

# 2. 物理 Pre-commit 钩子管理 (安装/核验无工单与仓储纯洁门禁)
python tools/vc_cli.py hook install
python tools/vc_cli.py hook verify

# 3. 工坊运行健康监视 (巡检停滞超期任务、2/3 接近熔断任务与健康综合评分)
python tools/vc_cli.py heartbeat

# 4. 终端敏捷看板 (Top-5 防 Token 膨胀保护)
python tools/vc_cli.py board

# 5. 创建任务卡片
python tools/vc_cli.py create --id TSK-1001 --title "实现JWT鉴权" --tier 2 --hours 4.0 --assignee pm

# 6. 领单开工 (Claim Work Order，自动执行 WIP 检查与依赖拓扑核验)
python tools/vc_cli.py claim --id TSK-1001 --role developer

# 7. 主动退单 (Surrender Work Order，遇到不可抗力释放锁定回归待领池)
python tools/vc_cli.py surrender --id TSK-1001 --role developer --reason "遇到上游接口阻塞"

# 8. 毫秒级 AST 语法快筛
python tools/vc_cli.py lint --target src

# 9. 质检审查小组统一质检流水线 (AST/规范 -> SAST安全 -> 自动化单测，签发 VERIFY-*.md)
python tools/vc_cli.py audit --id TSK-1001 --commit-msg "feat(auth): add jwt support"

# 10. 六重确定性质量门禁细粒度核验 (签发密码学收据 REC-*.json)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_2_review --commit-msg "feat(用户鉴权): 实现基于 RSA-256 的 JWT 令牌"
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_3_security
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_4_testing
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_5_doc_sync

# 11. 行使一票否决打回 (QR/SR/FR/DR)
python tools/vc_cli.py reject --id TSK-1001 --role qa_board --type QR --reason "圈复杂度超标且缺少边界用例"

# 12. CTO 架构仲裁诊断 (硬熔断唤醒或人工诊断)
python tools/vc_cli.py arbitrate --id TSK-1001

# 13. 时光倒流无损回滚 (恢复到历史干净检查点)
python tools/vc_cli.py rollback --id TSK-1001 --stage READY_TO_CLAIM

# 14. 仓库整洁度与测试镜像体检
python tools/vc_cli.py hygiene

# 15. 人类专属物理终审验收 (Gate 6 - 真实 TTY 交互)
python tools/vc_cli.py accept --id TSK-1001 --by "系统架构负责人"

# 16. 离线零依赖 Web 敏捷大盘启动 (本地 8848 端口)
python tools/vc_cli.py web
```

---

## 6. 微内核治理资产索引体系

AegisFlow 建立了层次分明、高度内聚且 100% 原创的工程资产矩阵：

- **核心治理配置**: [`core_config.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/core_config.yaml)（风控工时、熔断阈值、L0-L3 网关与六重门禁准则）
- **门禁守卫清单 (`manifests/`)**:
  - [`01-architect_gate.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/01-architect_gate.yaml): G1 契约锁定与顶层解耦守卫
  - [`02-syntax_reviewer.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/02-syntax_reviewer.yaml): G2 静态语法快筛与提交规范守卫
  - [`03-security_auditor.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/03-security_auditor.yaml): G3 独立安全审计与机密防护守卫
  - [`04-qa_validator.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/04-qa_validator.yaml): G4 自动化回归与测试镜像对齐守卫
  - [`05-doc_sync_guard.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/05-doc_sync_guard.yaml): G5 架构地图与活文档同步守卫
  - [`06-pipeline_orchestrator.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/06-pipeline_orchestrator.yaml): 流水线编排与 WBS 拆解调度器
  - [`07-arbitration_court.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/manifests/07-arbitration_court.yaml): 三阶硬熔断仲裁与时空快照法庭
- **工程治理法典 (`doctrines/`)**:
  - [`code_governance_doctrine.md`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/doctrines/code_governance_doctrine.md): 确定性代码合规与仓储治理六大律
  - [`human_sovereignty_protocol.md`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/doctrines/human_sovereignty_protocol.md): 人类终审主权与人机协同边界公约
- **工程规范参考 (`standards/`)**:
  - [`conventional_commits_zh.md`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/standards/conventional_commits_zh.md): 中文 Conventional Commits 提交格式规范
  - [`ast_repomap_standard.md`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/standards/ast_repomap_standard.md): Aider 风格 AST 代码架构地图标准
- **契约与收据模式 (`schemas/`)**:
  - [`contract_manifest.schema.yaml`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/schemas/contract_manifest.schema.yaml): G1 任务契约声明模式（范围白名单约束）
  - [`cryptographic_receipt.schema.json`](file:///d:/Codex/Projects/%E5%A4%9AAgent%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7/.agents/skills/virtual-company/schemas/cryptographic_receipt.schema.json): G1-G6 密码学收据不可篡改标准 JSON Schema

---

## 7. 精益角色生态与物理门禁矩阵 (Lean Role Ecosystem & Physical Gates)

AegisFlow 将原本冗余的 11 角色重构收敛为**“5 大常驻骨干 + 2 大阶段专家 + 1 位休眠仲裁官 + 1 位最高主权管理员” (5+2+1+1 体系)**，并实行绝对的**以工单为中心 (Work-Order-Centric)** 与 **物理硬门禁 (Physical Hard Enforcements)**：

### 7.1 角色全景编排 (5+2+1+1)

| 角色类别 | 角色标识 | 角色全称 | 核心定位与职责边界 | 生命周期介入阶段 | 核心交付产物与防线 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **5 大常驻骨干** | **pm** | 团队负责人 / 产品主理人 📋 | 需求全面统筹、业务目标确立、拆解细化可测试验收准则 (AC) | `BACKLOG` ➔ `SPEC_REVIEW` | 需求卡片、明确业务目标、AC 契约清单 |
| | **architect** | 系统架构师 🏛️ | 核心技术选型、设计 SPEC 与文件白名单、SHA256 契约签名锁定 (Gate 1)、按需决策是否调用 researcher 预研 | `SPEC_REVIEW` ➔ `READY_TO_CLAIM` | `docs/specs/SPEC-*.md`、范围白名单、G1 契约收据 |
| | **developer** | 核心研发工程师 💻 | 认领工单 (Claim)、开发者并发工单上限 (WIP Limit = 3)、白名单内精准实现、单元测试自编写、主动退单 (Surrender) | `READY_TO_CLAIM` ➔ `IN_PROGRESS` ➔ `IN_AUDIT` | 业务源码、单测代码、Conventional Commits |
| | **qa_board** | 质检审查小组 🛡️ | 审查、安全、测试三合一闭环流水线（内部串行 AST 快筛 ➔ SAST 安全审计 ➔ 100% 动态回归），行使 `#QR/#SR/#FR` 一票否决 | `IN_AUDIT` ➔ `DOC_SYNC` (或驳回 `REVISE`) | 《综合质检审查报告》(VERIFY-*.md)、综合质检收据 |
| | **doc_engineer** | 活文档工程师 📚 | Aider 风格 AST 代码架构地图与目录维护、接口与文档一致性核验 (Gate 5)、行使 `#DR` 一票否决 | `DOC_SYNC` ➔ `RELEASE_PREP` | `docs/PROJECT_STRUCTURE.md`、接口同步收据 |
| **2 大阶段专家** | **researcher** | 技术预研专家 🔬 | **按需休眠/唤醒**：仅在初次立项、新技术路线或高风险架构抉择时由架构师调用，输出技术调研报告 | 按需在 `BACKLOG` / `SPEC_REVIEW` 唤醒 | `docs/research/RES-*.md` 技术预研评估报告 |
| | **devops** | 运维部署与发布专家 🚀 | **阶段参与**：架构设计期提供部署与运行时建议；发版阶段把关版本发布、交付物封装与终审移交 | 架构期参谋 ➔ 终局 `RELEASE_PREP` ➔ `COMPLETED` | 部署清单、发布校验报告、发版封包 |
| **1 位休眠仲裁官**| **cto** | 首席技术仲裁官 ⚖️ | **平时常态休眠**：当工单遭遇连续 3 次打回触发硬熔断时自动被系统唤醒，深度复盘死锁根因，输出技术仲裁诊断呈报人类 | `BLOCKED` 硬熔断唤醒 | 《CTO 技术仲裁诊断报告书》(ARB-*.md) |
| **1 位最高主权** | **human_admin** | 人类最高管理员 👑 | 系统最高主权所有者，物理真实终端交互终审 (Gate 6)，不可逆封板归档 | `COMPLETED` ➔ `ACCEPTED` (终态) | 人类操作员物理终审收据、归档档案 |

---

### 7.2 任务与工单全生命周期 9 大标准状态

```
 [BACKLOG] (立项需求池)
    │  (pm: 细化 AC 准则)
    ▼
 [SPEC_REVIEW] (架构白名单锁定)
    │  (architect: 编写 SPEC-*.md，签发 G1 契约收据)
    ▼
 [READY_TO_CLAIM] (公海待领工单池)
    │  (developer: 认领 claim_task，检查 WIP<=3 & 前置 depends_on)
    ├───────────────────────────────────────────────────────┐
    ▼                                                       ▼
 [IN_PROGRESS] (编码实装) ──(主动退单 surrender)──► [READY_TO_CLAIM]
    │  (developer: 提测进审查，严禁直标完成)
    ▼
 [IN_AUDIT] (质检审查小组审核)
    ├─► [REVISE] (质检打回，原单追加 #QR/#SR/#FR 轨迹) ──► (打回累计3次: 唤醒 CTO 熔断锁死为 [BLOCKED])
    │  (qa_board: 规范 -> 安全 -> 单测全绿，签发 VERIFY-*.md)
    ▼
 [DOC_SYNC] (活文档与架构地图同步)
    │  (doc_engineer: 更新 PROJECT_STRUCTURE.md & 接口文档)
    ▼
 [RELEASE_PREP] (发版与交付打包)
    │  (devops: 部署校验与发布准备完毕)
    ▼
 [COMPLETED] (待终审验收)
    │  (human_admin: 人类物理终审 Gate 6，输入 y 确认)
    ▼
 [ACCEPTED] (终态封板，密码学收据全链固化)
```

---

### 7.3 全量“禁止可能”物理硬门禁矩阵 (Physical Hard Prohibitions)

系统绝不依赖 Prompt 口头承诺，所有禁止规则均在 Python 状态机、磁盘文件与 Git 钩子中强制写死：

| 违规动作 / 越权企图 | 拦截机制与物理表现 | 责任角色 / 触发源 |
| :--- | :--- | :--- |
| **无工单私自编写代码** | Git `pre-commit` 物理拦截退出码 1，阻断提交 | 任意开发者 / Agent |
| **工单未锁定 SPEC 抢先待领** | 状态机强校验：缺少 `docs/specs/SPEC-*.md` 抛出 `ValueError` | `architect` |
| **开发持单超出并发上限 (3个)** | 状态机 `WIP Limit = 3` 物理锁定：已有 3 项进行中工单认领新单抛出 `PermissionError` | `developer` |
| **前置依赖未验收提前开工** | 拓扑依赖强阻断：`depends_on` 未处于 `ACCEPTED` 状态时认领抛出 `ValueError` | `developer` |
| **非持单人越权代为退单** | 权限强校验：非当前责任人执行退单抛出 `PermissionError` | 任意非法介入者 |
| **研发工程师擅自宣布完成** | 状态机权限白名单：`developer` 推进至 `COMPLETED` 抛出 `PermissionError` | `developer` |
| **跳过质检直接同步文档** | 前置文件与收据强校验：缺少 `VERIFY-*.md` 且非 PASS 抛出 `ValueError` | 企图跳步者 |
| **代码变动但未更新活文档** | Gate 5 活文档同步校验器一票否决 (`#DR`) | `doc_engineer` |
| **智能体自我终审验收工单** | 状态机物理检测：`ACCEPTED` 仅限 `human_admin` 且校验 TTY 终端 | 任何 AI 智能体 |
| **连续打回企图新建工单洗牌** | 状态机反洗牌铁律：禁止创建已存在 ID；打回达到 3 次强制熔断锁为 `BLOCKED` 并唤醒 CTO | 违规避责行为 |



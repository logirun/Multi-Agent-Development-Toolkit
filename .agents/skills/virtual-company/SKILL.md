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
python tools/vc_cli.py create --id TSK-1001 --title "实现JWT鉴权" --tier 2 --hours 4.0 --assignee developer

# 6. 领单开工
python tools/vc_cli.py start --id TSK-1001 --role developer

# 7. 毫秒级 AST 语法快筛
python tools/vc_cli.py lint --target src

# 8. 六重确定性质量门禁核验 (签发密码学收据 REC-*.json)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_2_review --commit-msg "feat(用户鉴权): 实现基于 RSA-256 的 JWT 令牌"
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_3_security
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_4_testing
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_5_doc_sync

# 9. 行使一票否决打回 (QR/SR/FR/DR)
python tools/vc_cli.py reject --id TSK-1001 --role reviewer --type QR --reason "圈复杂度超标且缺少边界用例"

# 10. 时光倒流无损回滚 (恢复到历史干净检查点)
python tools/vc_cli.py rollback --id TSK-1001 --stage IN_PROGRESS

# 11. 仓库整洁度与测试镜像体检
python tools/vc_cli.py hygiene

# 12. 人类专属物理终审验收 (Gate 6 - 真实 TTY 交互)
python tools/vc_cli.py accept --id TSK-1001 --by "系统架构负责人"

# 13. 离线零依赖 Web 大盘启动 (本地 8848 端口)
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

## 7. 全角色协同履职矩阵 (Multi-Role Action Matrix)

AegisFlow 彻底打破“挂名式”角色设定，将 11 大标准角色全面盘活并深度编织进研发治理生命周期：

| 角色标识 | 角色全称 | 核心定位与职责边界 | 生命周期触达阶段 | 核心交付产物与防线 |
| :--- | :--- | :--- | :--- | :--- |
| **pm** | 团队负责人 / 产品主理人 📋 | 团队全面统筹、业务立项目标拟定、全生命周期管控与验收指标（AC）细化 | `BACKLOG` ➔ `SPECIFICATION` | 业务需求清单、验收准则边界 |
| **architect** | 系统架构师 🏛️ | 语义边界白名单圈定、SHA256 契约签名计算与 G1 门禁锁定 | `SPECIFICATION` ➔ `CONTRACT_FROZEN` | G1 架构契约收据、文件白名单 |
| **uiux_designer** | UI/UX体验设计师 🎨 | 界面视觉走查、深色磨砂材质对齐、去原生控件、防溢出审查 | `CONTRACT_FROZEN` ➔ `IN_PROGRESS` | 前端组件规范、设计走查报告 |
| **dba** | 数据库管理员 🗄️ | 数据模式演进审查、迁移脚本合规性评估、可逆 DDL 验证 | `IN_PROGRESS` (涉及数据库时) | DDL 脚本审计意见、回滚方案 |
| **developer** | 核心研发工程师 💻 | 范围白名单内精准实现、单元测试自编写、中文提交规范 | `IN_PROGRESS` ➔ `CODE_REVIEW` | 业务源码、单测代码、Git Commit |
| **code_reviewer** | 代码审查员 🔍 | AST 抽象语法树遍历快筛、Conventional Commits 校验（拥有 `#QR` 否决权） | `CODE_REVIEW` ➔ `SECURITY_AUDIT` | G2 语法评审收据、`#QR` 审查意见 |
| **security_engineer** | 独立安全审计员 🛡️ | SAST 静态机密扫描、SQL 拼接与 OWASP 漏洞排查（拥有 `#SR` 否决权） | `SECURITY_AUDIT` ➔ `TESTING` | G3 安全审计收据、`#SR` 漏洞拦截单 |
| **qa_engineer** | 质量验证测试员 🧪 | 1:1 镜像测试环境自适应执行、全量断言通过率核验（拥有 `#FR` 否决权） | `TESTING` ➔ `DOC_SYNC` | G4 动态测试收据、`#FR` 缺陷打回单 |
| **doc_engineer** | 活文档工程师 📚 | Aider 风格 AST 代码架构地图维护、API 与实现同步审查（拥有 `#DR` 否决权） | `DOC_SYNC` ➔ `COMPLETED` | G5 活文档同步收据、`#DR` 差异记录 |
| **release_engineer** | 发布协调主管 🚀 | 全绿工单版本集成打包、跨角色交付物一致性核查与上线准备 | `COMPLETED` 封包 | 待发布版本包、全流程履职汇总单 |
| **cto** | 首席技术仲裁官 ⚖️ | 三振出局硬熔断介入仲裁、时空快照时光倒流与架构冲突裁决 | `BLOCKED` 状态唤醒 | 熔断仲裁决策书、时光倒流指令 |
| **human_operator** | 人类管理员 👑 | 物理真实控制台终审（Gate 6）、业务目标最终验收、不可逆封板归档 | `ACCEPTED` (终态) | 人类物理签字收据、项目封板档案 |


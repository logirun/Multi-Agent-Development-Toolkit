# AegisFlow · 神盾协同微内核 (Virtual Software Studio)

> **“代码即契约，门禁即法度，收据即真相”**  
> 专为先进智能体工程打造的高确定性、防合谋、密码学闭环的多 Agent 协同与制衡虚拟软件工坊。


---

## 🌟 核心哲学与特性

在传统的多 Agent 自动化开发中，Agent 之间极易陷入盲从与群体谄媚（Groupthink）——互相秒级点赞、放行未经审查的代码，导致幻觉与隐蔽 Bug 泛滥。
**AegisFlow** 引入了机器级确定性质量门禁与权力制衡架构，在多 Agent 协同体系中构建起高信任、高透明的工程防线：

1. **组织分工与权限物理隔离 (Cline-inspired Lockdown)**:
   - 9 大专属角色：PMO、架构师、UI/UX 设计师、DBA、全栈开发矩阵、代码评审员、安全审计员、QA 测试员、活文档工程师、CTO 仲裁官。
   - 架构师禁止在 `src/` 编码；开发人员物理只读 `tests/`（杜绝篡改用例作弊）；QA 物理只读 `src/`。
2. **四维独立一票否决权 (Veto Powers)**:
   - 代码评审员 (`#QR`)、安全审计员 (`#SR`)、QA 测试员 (`#FR`)、文档专家 (`#DR`) 均拥有一票否决权。
   - 任何打回均继承原工单编号（如 `TSK-1001#SR-1`），保留完整审计追溯，严禁重新建卡洗白。
3. **三振出局熔断机制 (Circuit Breaker)**:
   - 累计打回达到 3 次，工单状态自动锁定为 `BLOCKED`，由 CTO 介入技术仲裁或使用时光倒流回滚。
4. **六重确定性质量门禁 (Deterministic Quality Gates)**:
   - **Gate 1**: 接口契约与 ADR 冻结（SHA256 签名锁定）。
   - **Gate 2**: Conventional Commits v1.0.0 与 SWE-agent 级快速 AST 语法快筛。
   - **Gate 3**: OWASP 漏洞与硬编码密钥扫描（安全一票否决）。
   - **Gate 4**: 独立干净环境全量自动化回归测试（QA 一票否决）。
   - **Gate 5**: Living Documentation 活文档与代码同步校验（文档一票否决）。
   - **Gate 6**: 人类物理终端交互验收（严禁 Agent 冒充人类）。
5. **双引擎敏捷看板与防 Token 膨胀 (Anti-Token Bleed)**:
   - **终端 ANSI 看板**: 默认仅展示 Top-5 活跃卡片，保护 LLM 上下文窗口。
   - **本地 Web 看板**: 基于 Python 标准库 `http.server` 的零依赖现代化离线看板（端口 8848）。
6. **SOTA 开源生态吸纳**:
   - **Aider**: 自动提取 AST 符号树生成 `docs/PROJECT_STRUCTURE.md` 代码地图。
   - **LangGraph**: 状态迁移自动打标快照，支持无损时光倒流（Time-Travel Rollback）。
   - **OpenHands**: 不可篡改的只追加 EventStream 审计事件流（`.agents/event_stream.jsonl`）。

---

## 🚀 快速启动

### 1. 运行环境与安装
无需安装繁重的第三方依赖，仅需标准 Python 3.10+：

```bash
# 克隆仓库并进入目录
git clone <repo_url>
cd 多Agent开发工具

# 运行全量单元测试（34项自测覆盖）
python -m unittest discover tests
```

### 2. 命令行工具链 (vc-cli)

```bash
# 初始化工程脚手架与代码地图
python tools/vc_cli.py init

# 启动终端高亮敏捷看板 (Top-5 保护)
python tools/vc_cli.py board

# 启动本地零依赖 Web 仪表盘 (访问 http://localhost:8848)
python tools/vc_cli.py web --port 8848

# 检查代码库零污染规范
python tools/vc_cli.py hygiene
```

### 3. 标准功能研发闭环示例

```bash
# 1. PM 建单 (遵循 SRP 8.0h 上限)
python tools/vc_cli.py create --id TSK-1001 --title "实现JWT用户鉴权" --tier 2 --hours 4.0 --assignee pm

# 2. 架构师冻结契约 (Gate 1)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_1_contract --file docs/contracts/SPEC-0001-auth-contract.json
python tools/vc_cli.py advance --id TSK-1001 --stage CONTRACT_FROZEN --role architect

# 3. 开发者领单与快速语法快筛
python tools/vc_cli.py start --id TSK-1001 --role developer
python tools/vc_cli.py lint --target src/auth.py
python tools/vc_cli.py advance --id TSK-1001 --stage CODE_REVIEW --role developer

# 4. 代码评审与提交规范 (Gate 2)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_2_review --commit-msg "feat(auth): implement jwt token auth"
python tools/vc_cli.py advance --id TSK-1001 --stage SECURITY_AUDIT --role code_reviewer

# 5. 安全审计与一票否决打回 (Gate 3)
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_3_security
# 若需行使一票否决：
# python tools/vc_cli.py reject --id TSK-1001 --role security_engineer --type SR --reason "发现硬编码Token"

# 6. 独立自动化测试回归 (Gate 4)
python tools/vc_cli.py advance --id TSK-1001 --stage TESTING --role security_engineer
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_4_testing

# 7. 活文档同步与封装 (Gate 5)
python tools/vc_cli.py advance --id TSK-1001 --stage DOC_SYNC --role qa_engineer
python tools/vc_cli.py gate-check --id TSK-1001 --gate gate_5_doc_sync
python tools/vc_cli.py advance --id TSK-1001 --stage COMPLETED --role release_engineer

# 8. 人类专属最终验收 (Gate 6)
python tools/vc_cli.py accept --id TSK-1001
```

---

## 📁 目录结构规范

```text
├── docs/                       # 架构、契约、规格与活文档目录
│   ├── adr/                    # 架构决策记录 (ADR-xxxx.md)
│   ├── contracts/              # 机器可读 JSON Schema 契约 (SPEC-xxxx.json)
│   ├── specs/                  # 需求规范与 AC (REQ-xxxx.md)
│   └── PROJECT_STRUCTURE.md    # Aider 风格 AST 代码结构地图
├── src/                        # 生产业务代码 (开发者主控，架构/测试严禁写入)
├── tests/                      # 自动化测试用例 (QA 独立主控，开发者严禁篡改)
├── tools/                      # AegisFlow 微内核与工具链
│   ├── vc_cli.py               # 统一命令行交互入口
│   ├── state_manager.py        # 状态机、熔断器与 EventStream
│   ├── gatekeeper.py           # 质量门禁执行器与密码学收据引擎
│   ├── repo_hygiene.py         # 零污染检查器与 AST Repo Map 生成器
│   ├── board_renderer.py       # 终端 ANSI Top-5 看板渲染器
│   ├── kanban_server.py        # 零依赖本地 Web 服务器
│   └── web/                    # 离线单文件现代化 Web 看板
└── .agents/                    # 治理与审计数据 (系统内部状态)
    ├── skills/virtual-company/ # Antigravity Skill 技能定义包
    │   ├── SKILL.md            # 技能元数据与网关调度
    │   ├── roles/              # 11 大角色 Prompt 规范
    │   ├── templates/          # REQ, ADR, SPEC, Commit 模板
    │   └── workflows/          # Feature, Hotfix, Arbitration SOP
    ├── receipts/               # 门禁不可篡改收据 (REC-xxxx.json)
    ├── event_stream.jsonl      # OpenHands 风格不可变事件流
    └── .virtual_company_board.json # 看板持久化状态与检查点
```

---

## 📜 许可规范
本项目遵循 MIT 协议。

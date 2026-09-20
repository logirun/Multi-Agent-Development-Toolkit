# Standard Operating Procedure: 快速补丁与技术探针 (Hotfix & Spike SOP)

本 SOP 适用于 Tier 1 (PATCH / SPIKE) 级别的快速轻量研发流程。

---

## 流程特性
- **跳过阶段**: 免除 PM PRD 拆解与 Gate 1 架构契约冻结。
- **保留门禁**: 必须跑通 Gate 2 (提交规范) 与 Gate 4 (自动化回归测试)。
- **命名规范**: 使用 `FIX-xxxx` (缺陷修复) 或 `SPK-xxxx` (技术探针)。

---

## 执行步骤

### 1. 快速建单
```bash
python tools/vc_cli.py create --id FIX-0101 --title "修复登录重试偶发空指针" --tier 1 --type FIX --hours 1.0 --assignee developer
```

### 2. 领单研发
```bash
python tools/vc_cli.py start --id FIX-0101 --role developer
# 编码后执行快速语法检测
python tools/vc_cli.py lint --target src/
```

### 3. 快速审查与回归
```bash
python tools/vc_cli.py advance --id FIX-0101 --stage CODE_REVIEW --role developer
python tools/vc_cli.py gate-check --id FIX-0101 --gate gate_2_review --commit-msg "fix(auth): prevent null pointer on retry"

python tools/vc_cli.py advance --id FIX-0101 --stage TESTING --role code_reviewer
python tools/vc_cli.py gate-check --id FIX-0101 --gate gate_4_testing
```

### 4. 封装与验收
```bash
python tools/vc_cli.py advance --id FIX-0101 --stage COMPLETED --role release_engineer
python tools/vc_cli.py accept --id FIX-0101 --note "紧急补丁快速验证通过"
```

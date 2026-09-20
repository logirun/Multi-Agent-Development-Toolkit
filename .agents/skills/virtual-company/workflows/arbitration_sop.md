# Standard Operating Procedure: 熔断仲裁与时光倒流回滚 (Arbitration SOP)

本 SOP 适用于工单因多次打回进入 `BLOCKED` 状态、或架构出现灾难性偏差时的紧急干预流程。

---

## 1. 三振出局熔断机制 (Circuit Breaker)
当任意工单在 `#QR`、`#SR`、`#FR`、`#DR` 质检过程中**累计被打回 3 次**：
1. 状态机自动阻断后续状态跃迁。
2. 工单 stage 锁定为 `BLOCKED`，指派人强制变更为 `cto`。
3. 任何非 CTO 角色尝试推进该工单均会被系统拦截。

---

## 2. 仲裁处理流程

### 步骤 1: 审查打回审计记录
```bash
python tools/vc_cli.py status --id <TaskID>
```
查看 3 次打回的具体 tag（如 `#QR-1`, `#SR-2`, `#FR-3`）及各专业角色的打回意见。

### 步骤 2: 召开虚拟技术仲裁会 (CTO Arbiter)
CTO 分析以下三种可能性：
- **方案 A (需求不合理)**: 需求定义脱离实际或工时低估。打回 PMO 重新拆解。
- **方案 B (契约存在缺陷)**: 架构师制定的契约缺少边界处理。回滚至 SPECIFICATION。
- **方案 C (实现代码走入死胡同)**: 开发人员陷入上下文混乱。执行时光倒流回滚。

### 步骤 3: 执行时光倒流回滚 (Time-Travel Rollback)
AegisFlow 支持基于历史快照恢复工单状态：
```bash
# 回滚至未被污染的规范制定阶段
python tools/vc_cli.py rollback --id <TaskID> --stage SPECIFICATION

# 或回滚至重新编码阶段
python tools/vc_cli.py rollback --id <TaskID> --stage IN_PROGRESS
```
回滚后，工单解除 `BLOCKED` 锁定，开发矩阵可根据仲裁意见重新编码。

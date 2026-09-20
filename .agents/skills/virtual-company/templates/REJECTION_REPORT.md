# REJECTION REPORT: {{TASK_ID}}#{{REJECT_TYPE}}-{{ITERATION}}

| 属性 | 内容 |
| :--- | :--- |
| **工单编号** | `{{TASK_ID}}` |
| **打回标识** | `{{TASK_ID}}#{{REJECT_TYPE}}-{{ITERATION}}` |
| **否决角色** | `{{ROLE}}` |
| **否决类别** | `{{REJECT_TYPE}}` (QR:质量 / SR:安全 / FR:功能测试 / DR:文档) |
| **触发时间** | {{TIMESTAMP}} |
| **回滚目标** | `{{TARGET_STAGE}}` |

---

## 1. 否决原因与违规详情 (Veto Justification)
{{REASON}}

---

## 2. 问题定位与证据 (Evidence & Locations)
- **文件**: `{{FILE_PATH}}`
- **代码行**: Line {{LINE_NUMBER}}
- **复现代码 / 截图 / 输出**:
```
{{SNIPPET_OR_ERROR}}
```

---

## 3. 整改要求与修复建议 (Remediation Actions)
1. {{ACTION_ITEM_1}}
2. {{ACTION_ITEM_2}}

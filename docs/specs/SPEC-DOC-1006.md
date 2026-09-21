# 【活文档架构契约 SPEC-DOC-1006】
## 任务目标
基于 Python 原生 AST 模块重新解析代码库所有核心类与方法签名，刷新 `docs/PROJECT_STRUCTURE.md`。

## 验收准则 (AC)
1. 准确解析 classes, functions, docstrings；
2. 生成 Markdown 层级树状图并验证零死链；
3. 由人类操作员核验并封板归档。

# Conventional Commits Template for AegisFlow

## 格式规范
```text
<type>(<scope>): <short summary>

[optional body: detailed explanation of the change and architectural rationale]

Task: <TSK-xxxx|FIX-xxxx|SPK-xxxx>
Co-authored-by: VirtualStudio[bot] <bot@aegisflow.local>
```

## 类型限制
- `feat`: 新增业务功能
- `fix`: 修复已知 Bug
- `sec`: 安全补丁与漏洞修复
- `docs`: 文档变动
- `style`: 代码格式优化（不影响逻辑）
- `refactor`: 重构（非新增特性且非修复 bug）
- `perf`: 性能调优
- `test`: 增加或修改测试套件（仅限 QA 工程师）
- `build`: 构建系统或外部依赖变更
- `ci`: CI/CD 配置文件与脚本改动
- `chore`: 其他不修改生产代码的琐事

## 示例
```text
feat(auth): implement JWT token pair generation and refresh endpoint

Implement RS256 token signing with 15-minute access token and 7-day
refresh token rotation mechanism. Strictly aligned with SPEC-0001.

Task: TSK-1001
Co-authored-by: VirtualStudio[bot] <bot@aegisflow.local>
```

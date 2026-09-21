# 【需求规格契约 SPEC-REQ-1003】
## 业务目标
为全站 SaaS 平台提供企业级租户 Schema 物理隔离与动态连接池路由，杜绝跨租户数据越权访问。

## 范围白名单 (Scope Whitelist)
- `src/tenant/router.py`
- `src/tenant/context.py`
- `tests/test_tenant_router.py`

## 验收准则 (AC)
1. 拦截所有缺失 `Tenant-ID` 请求头的请求；
2. 动态路由到租户独立的 PostgreSQL Schema；
3. 单元测试覆盖率 > 95%。

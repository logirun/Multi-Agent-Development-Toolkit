"""
AegisFlow Production Source Package (src/)
===========================================

本目录存放工坊产出的生产业务逻辑代码。
权限铁律 (Cline-inspired Lockdown)：
- 本目录由全栈开发工程师 (developer) 主控并编写。
- 架构师 (architect) 严禁在底层业务代码中编码（只读权限）。
- 测试工程师 (qa_engineer) 严禁修改业务代码（只读权限），发现 Bug 必须通过打回 (#FR) 由开发修复。
"""

__all__ = ["auth"]

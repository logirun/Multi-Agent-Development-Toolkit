"""
AegisFlow (神盾协同微内核) - 数字化软件工作室配套工程工具链
============================================================

本包提供多 Agent 协同与制衡体系的核心运行时支持：
- state_manager: 任务状态机、SRP 工时管控、四维打回、熔断器与时光倒流。
- gatekeeper: 六重确定性质量门禁、Conventional Commits 校验、AST 快筛与密码学收据。
- repo_hygiene: 仓库零污染白名单检查、测试镜像一致性检测与 AST Repo Map 提取。
- board_renderer: 终端 ANSI 看板渲染（Top-5 防 Token 膨胀保护）。
- kanban_server: 零依赖本地 Web 仪表盘服务器（http.server）。
- vc_cli: 统一管理交互命令行入口。
"""

__version__ = "3.0.0"
__author__ = "AegisFlow Virtual Studio Team"
__all__ = [
    "state_manager",
    "gatekeeper",
    "repo_hygiene",
    "board_renderer",
    "kanban_server",
]

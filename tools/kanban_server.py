"""
AegisFlow Zero-Dependency Local Kanban Server (kanban_server.py)
================================================================

基于 Python 原生 http.server 标准库实现的零依赖本地看板与敏捷工作台后端。
特性：
- 零外部三方依赖，标准库原生驱动
- 提供 GET /api/board 接口，向前端实时返回任务数据、审计指标与时空快照
- 提供 GET /api/heartbeat 接口，返回工坊健康度评分与停滞巡检
- 提供 GET /api/receipt 接口，在线读取密码学门禁收据 JSON 内容
- 提供 POST /api/task/create 接口，支持从 Web 前端快捷创建新工单
- 提供 POST /api/task/advance 接口，支持 Web 前端推进工单研发阶段
- 提供 POST /api/task/reject 接口，支持 Web 前端行使四维制衡一票否决
- 静态托管 tools/web/index.html 离线多维大盘页面，默认监听端口 8848
"""

import sys
import json
import re
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# 确保在 Windows 控制台环境下使用 UTF-8 输出
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 确保项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tools.state_manager import StateManager
from tools.heartbeat import StudioHeartbeat

DEFAULT_PORT = 8848
BOARD_FILE = (_PROJECT_ROOT / ".agents" / ".virtual_company_board.json").resolve()
WEB_INDEX = (_PROJECT_ROOT / "tools" / "web" / "index.html").resolve()


class KanbanHandler(BaseHTTPRequestHandler):
    """
    轻量级 HTTP 请求处理器，提供 Web 界面静态文件托管与敏捷生命周期管理 JSON API。
    """

    def log_message(self, format, *args):
        """静默常规静态资源请求日志，保持终端整洁"""
        return

    def _send_json(self, status_code: int, data: dict):
        """统一发送 JSON 响应工具函数"""
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """
        处理 GET 请求路由：
        - /api/board: 读取工单数据库全量数据
        - /api/heartbeat: 运行工坊巡检并返回综合健康指标
        - /api/receipt?path=...: 在线读取单张密码学收据内容
        - / 或 /index.html: 托管渲染单文件 HTML 仪表盘
        """
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/board":
            try:
                sm = StateManager(str(_PROJECT_ROOT))
                self._send_json(200, sm.data)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        elif path == "/api/heartbeat":
            try:
                hb = StudioHeartbeat(root_dir=_PROJECT_ROOT)
                report = hb.run_inspection()
                self._send_json(200, report)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        elif path == "/api/receipt":
            receipt_path_raw = query.get("path", [""])[0]
            if not receipt_path_raw:
                self._send_json(400, {"error": "Missing 'path' query parameter"})
                return

            safe_target = Path(receipt_path_raw).resolve()
            allowed_root = (_PROJECT_ROOT / ".agents" / "receipts").resolve()
            if not str(safe_target).startswith(str(allowed_root)) and not safe_target.exists():
                safe_target = (_PROJECT_ROOT / receipt_path_raw.lstrip("/\\")).resolve()

            if safe_target.exists() and safe_target.is_file():
                try:
                    with open(safe_target, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._send_json(200, {"path": str(safe_target.name), "content": data})
                    return
                except Exception as e:
                    self._send_json(500, {"error": f"Failed to read receipt: {e}"})
                    return
            else:
                self._send_json(404, {"error": f"Receipt not found: {receipt_path_raw}"})
                return

        elif path == "/" or path == "/index.html":
            if WEB_INDEX.exists():
                with open(WEB_INDEX, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                msg = b"<h1>AegisFlow Web Dashboard: index.html not found</h1>"
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
            return

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """
        处理 POST 请求路由：
        - /api/task/create: 快捷创建工单
        - /api/task/advance: 推进工单阶段
        - /api/task/reject: 一票否决打回
        """
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        sm = StateManager(str(_PROJECT_ROOT))

        if path == "/api/task/create":
            try:
                task_id = body.get("id", "").strip()
                item_type = body.get("type", "TSK").strip().upper()
                if not task_id:
                    existing = [
                        int(re.search(r"\d+", k).group())
                        for k in sm.data["tasks"].keys()
                        if re.search(r"\d+", k)
                    ]
                    next_num = max(existing) + 1 if existing else 1001
                    task_id = f"{item_type}-{next_num}"

                title = body.get("title", "未命名工单").strip()
                desc = body.get("desc", "").strip()
                objective = body.get("objective", "").strip() or title
                collaborators = body.get("collaborators", [])
                priority = body.get("priority", "HIGH").strip().upper()
                assignee = body.get("assignee", "pm").strip()
                est_hours = float(body.get("est_hours", 4.0))

                tier_map = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
                tier = tier_map.get(priority, 2)

                task = sm.create_task(
                    task_id=task_id,
                    title=title,
                    desc=desc,
                    tier=tier,
                    item_type=item_type,
                    priority=priority,
                    assignee=assignee,
                    est_hours=est_hours,
                    objective=objective,
                    collaborators=collaborators
                )
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == "/api/task/advance":
            try:
                task_id = body.get("id")
                target_stage = body.get("stage")
                role = body.get("role", "developer")
                note = body.get("note", "通过 Web 界面推进阶段")
                receipt = body.get("receipt", None)
                result = body.get("result", None)

                task = sm.advance_stage(task_id, target_stage, role, note, receipt, result=result)
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == "/api/task/reject":
            try:
                task_id = body.get("id")
                role = body.get("role", "security_engineer")
                rej_type = body.get("type", "SR")
                reason = body.get("reason", "通过 Web 界面行使一票否决权")
                target_stage = body.get("target_stage", "IN_PROGRESS")

                task = sm.reject_task(task_id, role, rej_type, reason, target_stage)
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == "/api/task/accept":
            try:
                task_id = body.get("id")
                role = body.get("role", "human_admin")
                note = body.get("note", "人类管理员终审验收通过并归档")
                result = body.get("result", "全生命周期质量门禁全绿通过，人类管理员终审核准放行并归档。")
                task = sm.accept_task(task_id, accepted_by=role, note=note, result=result)
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == "/api/task/claim":
            try:
                task_id = body.get("id")
                role = body.get("role", "developer")
                task = sm.start_task(task_id, role=role)
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == "/api/task/surrender":
            try:
                task_id = body.get("id")
                role = body.get("role", "developer")
                reason = body.get("reason", "通过 Web 界面主动退还工单")
                task = sm.surrender_task(task_id, role=role, reason=reason)
                self._send_json(200, {"success": True, "task": task})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        else:
            self.send_response(404)
            self.end_headers()


def run_server(port: int = DEFAULT_PORT):
    """
    启动本地 Web 敏捷看板与微内核 API 服务。

    :param port: 监听端口号，默认为 8848
    """
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    server_address = ("", port)
    httpd = HTTPServer(server_address, KanbanHandler)
    print("======================================================================")
    print(" [神盾大盘] AegisFlow 离线原生 Web 看板服务已启动 (零依赖/全功能 API)")
    print(f" [访问地址] 本地访问地址: http://localhost:{port}/")
    print(" [数据同步] 实时同步: .agents/.virtual_company_board.json")
    print(" [终止服务] 按 Ctrl+C 终止大盘服务")
    print("======================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] 看板服务已安全关闭。")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AegisFlow Web Kanban Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default: 8848)")
    args = parser.parse_args()
    run_server(args.port)

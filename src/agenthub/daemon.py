"""
AgentHub Daemon - 守护进程

参考 gstack 的守护进程设计
"""

import os
import time
import json
import uuid
import signal
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from .state import StateManager
from .refs import RefRegistry, AGENT, TASK, SKILL, TAG, CATEGORY
from .logger import LogBuffer, log_system, log_error, log_warn


class AgentHubDaemon:
    """AgentHub 守护进程"""

    def __init__(
        self,
        port: int = None,
        state_db: str = None,
        log_dir: str = None,
        timeout: int = 3600,  # 1小时空闲超时
    ):
        self.port = port or 10000 + (hash("agenthub") % 50000)
        self.timeout = timeout
        self.state_db = state_db or "~/.agenthub/state.db"
        self.log_dir = log_dir or "~/.agenthub/logs"

        # 初始化组件
        self.state_manager = StateManager(self.state_db)
        self.ref_registry = RefRegistry()
        self.log_buffer = LogBuffer.get_instance()
        self.session_token = str(uuid.uuid4())

        # 状态
        self.start_time = time.time()
        self.last_active = time.time()
        self.is_running = False

        # 进程
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[Thread] = None

    def start(self):
        """启动守护进程"""
        if self.is_running:
            log_warn("守护进程已在运行")
            return False

        log_system(f"启动 AgentHub 守护进程 (端口 {self.port})")

        # 保存状态文件
        self._save_state_file()

        # 启动 HTTP 服务器
        self.server = AgentHubHTTPServer(
            daemon=self,
            token=self.session_token,
            port=self.port,
        )
        self.server_thread = Thread(
            target=self.server.serve_forever,
            name="AgentHubDaemon",
            daemon=True,
        )

        self.server_thread.start()
        self.is_running = True

        log_system(f"守护进程已启动，PID: {os.getpid()}")
        return True

    def stop(self):
        """停止守护进程"""
        if not self.is_running:
            log_warn("守护进程未运行")
            return False

        log_system("停止守护进程...")

        if self.server:
            self.server.shutdown()

        self.is_running = False

        log_system("守护进程已停止")

    def keep_alive(self):
        """保持活跃（由定时器调用）"""
        self.last_active = time.time()

        # 检查空闲超时
        idle_time = time.time() - self.last_active
        if idle_time > self.timeout:
            log_warn(f"空闲超时 ({idle_time:.0f}s)，停止守护进程")
            self.stop()

    def get_stats(self) -> Dict[str, Any]:
        """获取守护进程统计"""
        uptime = time.time() - self.start_time
        idle = time.time() - self.last_active

        return {
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime": uptime,
            "idle_time": idle,
            "last_active": self.last_active,
            "port": self.port,
            "session_token": self.session_token,
            "process_id": os.getpid(),
        }

    def _save_state_file(self):
        """保存状态文件"""
        state_file = Path("~/.agenthub/daemon.json").expanduser()

        state_data = {
            "pid": os.getpid(),
            "port": self.port,
            "token": self.session_token,
            "start_time": self.start_time,
            "last_active": self.last_active,
            "is_running": self.is_running,
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            log_error(f"保存状态文件失败: {e}")

    def _load_state_file(self) -> bool:
        """加载状态文件"""
        state_file = Path("~/.agenthub/daemon.json").expanduser()

        if not state_file.exists():
            return False

        try:
            with open(state_file, "r") as f:
                state_data = json.load(f)

            # 验证 Token
            if state_data.get("token") != self.session_token:
                log_error("状态文件中的 Token 不匹配，忽略")
                return False

            self.session_token = state_data.get("token")
            self.start_time = state_data.get("start_time", time.time())
            self.last_active = state_data.get("last_active", time.time())
            self.is_running = state_data.get("is_running", False)

            return True
        except Exception as e:
            log_error(f"加载状态文件失败: {e}")
            return False


class AgentHubHTTPServer(BaseHTTPRequestHandler):
    """AgentHub HTTP 服务器"""

    def __init__(self, daemon: AgentHubDaemon, token: str, port: int):
        self.daemon = daemon
        self.token = token
        self.port = port

    def log_request(self, path: str, client_host: str, user_agent: str):
        """记录请求日志"""
        log_network(f"收到请求: {path} from {client_host}")

    def do_GET(self):
        """处理 GET 请求"""
        path = self.path
        token = self.headers.get("Authorization", "").replace("Bearer ", "")

        # Token 验证
        if token != self.token:
            return self.send_response(401, "Unauthorized")

        # 解析路径
        parts = path.strip("/").split("/")
        if len(parts) == 0 or parts[0] == "":
            # 根路径，返回统计信息
            stats = self.daemon.get_stats()
            return self.send_response(200, json.dumps(stats, indent=2))

        elif parts[0] == "health":
            # 健康检查
            return self.send_response(200, "OK")

        elif parts[0] == "refs":
            # 获取引用列表
            refs = self.daemon.ref_registry.get_all_refs()
            return self.send_response(200, json.dumps([r.to_dict() for r in refs], indent=2))

        elif parts[0] == "stats":
            # 获取统计信息
            stats = self.daemon.get_stats()
            return self.send_response(200, json.dumps(stats, indent=2))

        elif parts[0] == "flush":
            # 刷新日志
            flushed = self.daemon.log_buffer.flush(force=True)
            return self.send_response(200, json.dumps(flushed, indent=2))

        elif parts[0] == "state":
            # 获取状态
            state = {
                "is_running": self.daemon.is_running,
                "uptime": time.time() - self.daemon.start_time,
                "idle_time": time.time() - self.daemon.last_active,
                "ref_count": self.daemon.ref_registry.get_ref_count(),
            }
            return self.send_response(200, json.dumps(state, indent=2))

        elif parts[0] == "logs":
            # 获取日志
            level = self.args.get("level")
            limit = int(self.args.get("limit", "100"))
            logs = self.daemon.log_buffer.get_recent_logs(level, limit)
            return self.send_response(200, json.dumps(logs, indent=2))

        else:
            return self.send_response(404, "Not Found")

    def do_POST(self):
        """处理 POST 请求"""
        path = self.path.strip("/")
        token = self.headers.get("Authorization", "").replace("Bearer ", "")

        # Token 验证
        if token != self.token:
            return self.send_response(401, "Unauthorized")

        parts = path.strip("/").split("/")

        try:
            # 解析请求体
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(post_data)
            else:
                return self.send_response(400, "Bad Request")

            # 处理不同的 POST 请求
            if parts[0] == "register_agent":
                result = self._handle_register_agent(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "get_agent":
                result = self._handle_get_agent(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "get_task":
                result = self._handle_get_task(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "get_all_agents":
                result = self._handle_get_all_agents(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "get_all_tasks":
                result = self._handle_get_all_tasks(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "publish_task":
                result = self._handle_publish_task(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "bid_task":
                result = self._handle_bid_task(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "complete_task":
                result = self._handle_complete_task(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "get_refs":
                result = self._handle_get_refs(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "register_ref":
                result = self._handle_register_ref(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "resolve_ref":
                result = self._handle_resolve_ref(data)
                return self.send_response(200, json.dumps(result, indent=2))

            elif parts[0] == "keep_alive":
                self.daemon.keep_alive()
                return self.send_response(200, "OK")

            else:
                return self.send_response(404, "Not Found")

        except json.JSONDecodeError as e:
            return self.send_response(400, f"Invalid JSON: {e}")
        except Exception as e:
            return self.send_response(500, f"Internal Error: {e}")

    def _handle_register_agent(self, data: Dict) -> Dict:
        """处理注册 Agent"""
        name = data.get("name")
        skills = data.get("skills", [])
        capabilities = data.get("capabilities", {})

        if not name:
            return {"error": "缺少 name 参数"}

        from .hub import AgentHub

        hub = AgentHub()
        agent = hub.register_agent(
            name=name,
            skills=skills,
            capabilities=capabilities,
            registered_by="daemon",
        )

        self.daemon.state_manager.save_agent(agent.to_dict())

        return {"success": True, "agent_id": agent.id}

    def _handle_get_agent(self, data: Dict) -> Dict:
        """处理获取 Agent"""
        agent_id = data.get("agent_id")

        if not agent_id:
            return {"error": "缺少 agent_id 参数"}

        agent = self.daemon.state_manager.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} 不存在"}

        return {"success": True, "agent": agent}

    def _handle_get_task(self, data: Dict) -> Dict:
        """处理获取 Task"""
        task_id = data.get("task_id")

        if not task_id:
            return {"error": "缺少 task_id 参数"}

        task = self.daemon.state_manager.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} 不存在"}

        return {"success": True, "task": task}

    def _handle_get_all_agents(self, data: Dict) -> Dict:
        """处理获取所有 Agent"""
        agents = self.daemon.state_manager.get_all_agents()
        return {"success": True, "agents": agents}

    def _handle_get_all_tasks(self, data: Dict) -> Dict:
        """处理获取所有 Task"""
        tasks = self.daemon.state_manager.get_all_tasks()
        return {"success": True, "tasks": tasks}

    def _handle_publish_task(self, data: Dict) -> Dict:
        """处理发布任务"""
        title = data.get("title")
        description = data.get("description", "")
        skill_needed = data.get("skill_needed")
        reward = data.get("reward")
        posted_by = data.get("posted_by")

        if not title or not skill_needed or not reward or not posted_by:
            return {"error": "缺少必要参数"}

        from .hub import AgentHub

        hub = AgentHub()
        task = hub.publish_task(
            title=title,
            description=description,
            skill_needed=skill_needed,
            reward=reward,
            posted_by=posted_by,
        )

        self.daemon.state_manager.save_task(task.to_dict())

        return {"success": True, "task_id": task.id}

    def _handle_bid_task(self, data: Dict) -> Dict:
        """处理竞拍任务"""
        task_id = data.get("task_id")
        agent_id = data.get("agent_id")
        bid_amount = data.get("bid_amount")

        if not task_id or not agent_id:
            return {"error": "缺少 task_id 或 agent_id 参数"}

        from .hub import AgentHub

        hub = AgentHub()

        try:
            if bid_amount:
                hub.bid_task(task_id, agent_id, bid_amount)
            else:
                hub.auction_task(task_id)
        except Exception as e:
            return {"error": f"竞拍失败: {str(e)}"}

        task = hub.get_task(task_id)
        agent = hub.get_agent(agent_id)

        return {"success": True, "task": task, "agent": agent}

    def _handle_complete_task(self, data: Dict) -> Dict:
        """处理完成任务"""
        task_id = data.get("task_id")
        agent_id = data.get("agent_id")
        result = data.get("result")
        rating = data.get("rating")

        if not task_id or not agent_id or not result:
            return {"error": "缺少必要参数"}

        from .hub import AgentHub

        hub = AgentHub()
        completion = hub.complete_task(
            task_id=task_id,
            agent_id=agent_id,
            result=result,
            rating=rating,
        )

        return {
            "success": True,
            "task": hub.get_task(task_id),
            "agent": hub.get_agent(agent_id),
            **completion,
        }

    def _handle_get_refs(self, data: Dict) -> Dict:
        """处理获取引用"""
        agent_id = data.get("agent_id")
        task_id = data.get("task_id")

        if not agent_id and not task_id:
            refs = self.daemon.ref_registry.get_all_refs()
            return {"success": True, "refs": [r.to_dict() for r in refs]}

        if agent_id:
            refs = self.daemon.ref_registry.get_agent_refs(agent_id)
        elif task_id:
            refs = self.daemon.ref_registry.get_task_refs(task_id)
        else:
            return {"error": "缺少 agent_id 或 task_id 参数"}

        return {"success": True, "refs": [r.to_dict() for r in refs]}

    def _handle_register_ref(self, data: Dict) -> Dict:
        """处理注册引用"""
        ref_type = data.get("type")
        agent_id = data.get("agent_id")
        element_key = data.get("element_key")

        if not ref_type or not element_key:
            return {"error": "缺少 type 或 element_key 参数"}

        from .refs import RefType

        if ref_type == "agent":
            if not agent_id:
                return {"error": "Agent 引用需要 agent_id 参数"}
            ref = self.daemon.ref_registry.register_agent_ref(element_key, agent_id)
        elif ref_type == "task":
            if not element_key:
                return {"error": "Task 引用需要 element_key 参数"}
            ref = self.daemon.ref_registry.register_task_ref(element_key, data.get("task_id"))
        elif ref_type == "skill":
            if not agent_id:
                return {"error": "Skill 引用需要 agent_id 参数"}
            ref = self.daemon.ref_registry.register_skill_ref(element_key, agent_id)
        elif ref_type == "tag":
            ref = self.daemon.ref_registry.register_tag_ref(element_key)
        else:
            return {"error": f"未知的引用类型: {ref_type}"}

        return {"success": True, "ref": ref.to_dict()}

    def _handle_resolve_ref(self, data: Dict) -> Dict:
        """处理解析引用"""
        ref = data.get("ref")

        if not ref:
            return {"error": "缺少 ref 参数"}

        agent_id, task_id = self.daemon.ref_registry.resolve_ref(ref)

        result = {}
        if agent_id:
            agent = self.daemon.state_manager.get_agent(agent_id)
            result["agent"] = agent
        if task_id:
            task = self.daemon.state_manager.get_task(task_id)
            result["task"] = task

        return {"success": True, **result}

    def log_error(self, message: str):
        """记录错误日志"""
        self.daemon.log_buffer.add_error(message)

    def send_response(self, code: int, message: str):
        """发送响应"""
        self.send_response(code, {"error": message}, content_type="application/json")

    def do_PUT(self):
        """处理 PUT 请求"""
        return self.send_response(405, "Method Not Allowed")

    def do_DELETE(self):
        """处理 DELETE 请求"""
        return self.send_response(405, "Method Not Allowed")

    def end_headers(self):
        """结束响应头"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_header(self, name: str, value: str):
        """发送响应头"""
        self.send_header(name, f"{name}: {value}")

    def send_response(self, code: int, body: str, content_type: str = "text/plain"):
        """发送响应"""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

        self.wfile.write(f"HTTP/1.1 {code}\r\n\r\n")
        self.wfile.write(body)
        self.wfile.write("\n")
        self.wclose()


def start_daemon(
    port: int = None,
    state_db: str = None,
    log_dir: str = None,
    timeout: int = 3600,
) -> AgentHubDaemon:
    """启动守护进程"""
    daemon = AgentHubDaemon(
        port=port,
        state_db=state_db,
        log_dir=log_dir,
        timeout=timeout,
    )
    daemon.start()
    return daemon


def stop_daemon():
    """停止守护进程"""
    state_file = Path("~/.agenthub/daemon.json").expanduser()

    if not state_file.exists():
        print("守护进程未运行")
        return

    try:
        with open(state_file, "r") as f:
            state_data = json.load(f)
            pid = state_data.get("pid")

        if pid:
            import os
            os.kill(pid, 15)  # SIGTERM
            print(f"已发送停止信号给进程 {pid}")

        # 删除状态文件
        state_file.unlink()

        print("守护进程已停止")
    except ProcessLookupError:
        print("守护进程已停止（进程不存在）")
    except Exception as e:
        print(f"停止失败: {e}")

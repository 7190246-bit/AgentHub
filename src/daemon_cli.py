"""
AgentHub 守护进程 - 后台运行版本
参考 gstack 的守护进程设计
"""

import os
import sys
import json
import time
import signal
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agenthub import AgentHub


class AgentHubDaemon:
    """AgentHub 守护进程"""

    VERSION = "0.1.0"
    STATE_FILE = Path("~/.agenthub/daemon.json").expanduser()
    PORT_RANGE = (10000, 60000)

    def __init__(self, port: int = None):
        self.port = port or self._find_available_port()
        self.pid = os.getpid()
        self.started_at = datetime.utcnow().isoformat()
        self.token = self._generate_token()
        self.hub = AgentHub()

    def _find_available_port(self) -> int:
        """找到可用端口"""
        import random
        for _ in range(100):
            port = random.randint(*self.PORT_RANGE)
            if self._is_port_available(port):
                return port
        raise RuntimeError("找不到可用端口")

    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    def _generate_token(self) -> str:
        """生成认证 Token"""
        import uuid
        return str(uuid.uuid4())

    def save_state(self):
        """保存状态文件"""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "pid": self.pid,
            "port": self.port,
            "token": self.token,
            "started_at": self.started_at,
            "version": self.VERSION,
        }
        with open(self.STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> dict:
        """加载状态文件"""
        if not self.STATE_FILE.exists():
            return None
        with open(self.STATE_FILE, "r") as f:
            return json.load(f)

    def is_running(self) -> bool:
        """检查是否已运行"""
        state = self.load_state()
        if not state:
            return False
        # 检查进程是否存活
        try:
            os.kill(state["pid"], 0)
            return True
        except OSError:
            return False

    def start(self):
        """启动守护进程"""
        if self.is_running():
            print(f"⚠️  守护进程已在运行 (PID: {self.load_state()['pid']})")
            return False

        self.save_state()
        print(f"✅ AgentHub 守护进程启动成功!")
        print(f"   PID: {self.pid}")
        print(f"   Port: {self.port}")
        print(f"   Token: {self.token[:8]}...")
        print(f"   Version: {self.VERSION}")

        # 启动 HTTP 服务器
        self._start_server()
        return True

    def _start_server(self):
        """启动 HTTP 服务器"""
        server_address = ('127.0.0.1', self.port)
        httpd = HTTPServer(server_address, AgentHubHandler)
        httpd.daemon = self
        print(f"🌐 HTTP 服务器启动: http://127.0.0.1:{self.port}")
        httpd.serve_forever()

    def stop(self):
        """停止守护进程"""
        state = self.load_state()
        if state:
            try:
                os.kill(state["pid"], signal.SIGTERM)
                print("🛑 守护进程已停止")
            except OSError:
                print("⚠️ 进程不存在")
        if self.STATE_FILE.exists():
            self.STATE_FILE.unlink()

    def get_status(self) -> dict:
        """获取状态"""
        return {
            "pid": self.pid,
            "port": self.port,
            "token": self.token[:8] + "...",
            "started_at": self.started_at,
            "version": self.VERSION,
        }


class AgentHubHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理"""

    def do_GET(self):
        """处理 GET 请求"""
        daemon = self.server.daemon

        if self.path == "/health":
            self._respond({"status": "ok"})
        elif self.path == "/status":
            self._respond(daemon.get_status())
        elif self.path == "/stats":
            self._respond(daemon.hub.get_stats())
        else:
            self._respond({"error": "Not found"}, status=404)

    def do_POST(self):
        """处理 POST 请求"""
        daemon = self.server.daemon
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self._respond({"error": "Invalid JSON"}, status=400)
            return

        # 路由
        if self.path == "/register":
            result = self._register(data)
            self._respond(result)
        elif self.path == "/task":
            result = self._create_task(data)
            self._respond(result)
        else:
            self._respond({"error": "Not found"}, status=404)

    def _register(self, data: dict) -> dict:
        """注册 Agent"""
        name = data.get("name")
        skills = data.get("skills", [])

        if not name:
            return {"error": "缺少 name 参数"}

        agent = daemon.hub.register_agent(name=name, skills=skills)
        return {"success": True, "agent": agent.to_dict()}

    def _create_task(self, data: dict) -> dict:
        """创建任务"""
        title = data.get("title")
        description = data.get("description", "")
        skill_needed = data.get("skill_needed")
        reward = data.get("reward")
        posted_by = data.get("posted_by")

        if not all([title, skill_needed, reward, posted_by]):
            return {"error": "缺少必要参数"}

        task = daemon.hub.publish_task(
            title=title,
            description=description,
            skill_needed=skill_needed,
            reward=reward,
            posted_by=posted_by,
        )
        return {"success": True, "task": task.to_dict()}

    def _respond(self, data: dict, status: int = 200):
        """发送响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AgentHub 守护进程")
    parser.add_argument("command", choices=["start", "stop", "status"], help="命令")
    parser.add_argument("--port", type=int, help="指定端口")

    args = parser.parse_args()

    daemon = AgentHubDaemon(port=args.port)

    if args.command == "start":
        daemon.start()
    elif args.command == "stop":
        daemon.stop()
    elif args.command == "status":
        state = daemon.load_state()
        if state:
            print(f"PID: {state['pid']}")
            print(f"Port: {state['port']}")
            print(f"Started: {state['started_at']}")
        else:
            print("守护进程未运行")


if __name__ == "__main__":
    main()

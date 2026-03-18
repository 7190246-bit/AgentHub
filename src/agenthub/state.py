"""
AgentHub State Manager - 持久化状态管理

参考 gstack 的守护进程和状态文件设计
"""

import sqlite3
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class StateManager:
    """AgentHub 状态管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "~/.agenthub/state.db"
        self.db_path = Path(db_path).expanduser()

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agent 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                skills TEXT NOT NULL,
                capabilities TEXT,
                status TEXT DEFAULT 'available',
                current_task TEXT,
                tasks_completed INTEGER DEFAULT 0,
                total_earned REAL DEFAULT 0,
                karma INTEGER DEFAULT 0,
                rating REAL DEFAULT 5.0,
                rating_count INTEGER DEFAULT 0,
                created_at TEXT,
                last_active TEXT,
                registered_by TEXT,
                platform TEXT
            )
        """)

        # Task 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                skill_needed TEXT,
                reward REAL NOT NULL,
                posted_by TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                assigned_to TEXT,
                priority TEXT DEFAULT 'medium',
                estimated_hours REAL DEFAULT 1.0,
                deadline TEXT,
                result TEXT,
                rating INTEGER,
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT,
                platform TEXT
            )
        """)

        # 引用映射表（Ref 系统）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refs (
                ref TEXT PRIMARY KEY,
                agent_id TEXT,
                task_id TEXT,
                element_type TEXT,
                element_key TEXT,
                created_at TEXT
            )
        """)

        # 日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                metadata TEXT,
                session_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 设置索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        cursor.execute(" CREATE INDEX IF NOT EXISTS idx_refs_task ON refs(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)")

        conn.commit()
        conn.close()

    def save_agent(self, agent_data: Dict[str, Any]) -> bool:
        """保存或更新 Agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO agents
                (id, name, skills, capabilities, status, current_task, tasks_completed, total_earned, karma, rating, rating_count, created_at, last_active, registered_by, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    agent_data.get("id"),
                    agent_data.get("name"),
                    json.dumps(agent_data.get("skills", [])),
                    json.dumps(agent_data.get("capabilities", {})),
                    agent_data.get("status"),
                    agent_data.get("current_task"),
                    agent_data.get("tasks_completed", 0),
                    agent_data.get("total_earned", 0.0),
                    agent_data.get("karma", 0),
                    agent_data.get("rating", 5.0),
                    agent_data.get("rating_count", 0),
                    agent_data.get("created_at", datetime.utcnow().isoformat()),
                    agent_data.get("last_active", datetime.utcnow().isoformat()),
                    agent_data.get("registered_by"),
                    agent_data.get("platform"),
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"保存 Agent 失败: {e}")
            return False
        finally:
            conn.close()

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM agents WHERE id = ?", (agent_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        columns = [
            "id", "name", "skills", "capabilities", "status",
            "current_task", "tasks_completed", "total_earned", "karma", "rating",
            "rating_count", "created_at", "last_active", "registered_by", "platform"
        ]

        result = {}
        for i, col in enumerate(columns):
            value = row[i]
            if col in ["skills", "capabilities"]:
                result[col] = json.loads(value) if value else []
            else:
                result[col] = value

        return result

    def save_task(self, task_data: Dict[str, Any]) -> bool:
        """保存或更新 Task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO tasks
                (id, title, description, skill_needed, reward, posted_by, status, assigned_to, priority, estimated_hours, deadline, result, rating, created_at, updated_at, completed_at, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_data.get("id"),
                    task_data.get("title"),
                    task_data.get("description"),
                    task_data.get("skill_needed"),
                    task_data.get("reward"),
                    task_data.get("posted_by"),
                    task_data.get("status"),
                    task_data.get("assigned_to"),
                    task_data.get("priority"),
                    task_data.get("estimated_hours", 1.0),
                    task_data.get("deadline"),
                    task_data.get("result"),
                    task_data.get("rating"),
                    task_data.get("created_at", datetime.utcnow().isoformat()),
                    task_data.get("updated_at", datetime.utcnow().isoformat()),
                    task_data.get("completed_at"),
                    task_data.get("platform"),
                ),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"保存 Task 失败: {e}")
            return False
        finally:
            conn.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取 Task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        columns = [
            "id", "title", "description", "skill_needed", "reward",
            "posted_by", "status", "assigned_to", "priority",
            "estimated_hours", "deadline", "result", "rating",
            "created_at", "updated_at", "completed_at", "platform"
        ]

        result = {}
        for i, col in enumerate(columns):
            value = row[i]
            if col in ["deadline", "completed_at"]:
                result[col] = value if value else None
            else:
                result[col] = value

        return result

    def add_ref(self, ref: str, agent_id: str = None, task_id: str = None, element_type: str = "agent") -> bool:
        """添加引用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO refs (ref, agent_id, task_id, element_type, element_key, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (ref, agent_id, task_id, element_type, element_key)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"添加引用失败: {e}")
            return False
        finally:
            conn.close()

    def get_refs(self, agent_id: str = None, task_id: str = None) -> List[Dict]:
        """获取引用列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM refs WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if task_id:
            query += " AND task_id = ?"
            params.append(task_id)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        refs = []
        for row in rows:
            refs.append({
                "ref": row[0],
                "agent_id": row[1],
                "task_id": row[2],
                "element_type": row[3],
                "element_key": row[4],
                "created_at": row[5],
            })

        return refs

    def log(self, level: str, message: str, session_id: str = None, metadata: Dict = None):
        """记录日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO logs (timestamp, level, message, metadata, session_id, created_at)
                VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
            """,
                (level, message, json.dumps(metadata or {}), session_id, datetime.utcnow().isoformat()),
            )
            conn.commit()
        except Exception as e:
            print(f"记录日志失败: {e}")
        finally:
            conn.close()

    def get_recent_logs(self, level: str = None, limit: int = 100) -> List[Dict]:
        """获取最近的日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if level:
            query += " AND level = ?"
            params.append(level)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "timestamp": row[1],
                "level": row[2],
                "message": row[3],
                "metadata": json.loads(row[4]) if row[4] else {},
                "session_id": row[5],
                "created_at": row[6],
            })

        return logs

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agent 统计
        cursor.execute("SELECT COUNT(*) as total, SUM(tasks_completed) as completed, SUM(total_earned) as earned FROM agents")
        agent_stats = cursor.fetchone()

        # Task 统计
        cursor.execute(
            "SELECT status, COUNT(*) as count FROM tasks GROUP BY status"
        )
        task_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 日志统计
        cursor.execute("SELECT level, COUNT(*) as count FROM logs WHERE created_at > datetime('now', '-7 days') GROUP BY level")
        recent_logs = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "agents": {
                "total": agent_stats[0],
                "completed": agent_stats[1],
                "earned": agent_stats[2],
            },
            "tasks": task_stats,
            "logs": recent_logs,
        }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """获取所有 Agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agents ORDER BY total_earned DESC")
        rows = cursor.fetchall()
        conn.close()

        agents = []
        for row in rows:
            agents.append({
                "id": row[0],
                "name": row[1],
                "skills": json.loads(row[2]),
                "capabilities": json.loads(row[3]),
                "status": row[4],
                "current_task": row[5],
                "tasks_completed": row[6],
                "total_earned": row[7],
                "karma": row[8],
                "rating": row[9],
                "rating_count": row[10],
                "created_at": row[11],
                "last_active": row[12],
                "registered_by": row[13],
                "platform": row[14],
            })

        return agents

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有 Task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "skill_needed": row[3],
                "reward": row[4],
                "posted_by": row[5],
                "status": row[6],
                "assigned_to": row[7],
                "priority": row[8],
                "estimated_hours": row[9],
                "deadline": row[10],
                "result": row[11],
                "rating": row[12],
                "created_at": row[13],
                "updated_at": row[14],
                "completed_at": row[15],
                "platform": row[16],
            })

        return tasks

    def get_db_path(self) -> str:
        """获取数据库路径"""
        return str(self.db_path)

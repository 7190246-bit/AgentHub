"""
AgentHub Log Buffer - 环形日志缓冲区

参考 gstack 的三层日志缓冲区设计
"""

import time
import json
from typing import List, Dict, Any
from collections import deque
from datetime import datetime
from pathlib import Path

# 日志级别常量
INFO = "info"
DEBUG = "debug"
WARN = "warn"
ERROR = "error"


class LogEntry:
    """日志条目"""

    def __init__(
        self,
        timestamp: float,
        level: str,
        message: str,
        metadata: Dict[str, Any] = None,
        session_id: str = None,
    ):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.metadata = metadata or {}
        self.session_id = session_id

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "metadata": self.metadata,
            "session_id": self.session_id,
        }


class LogBuffer:
    """环形日志缓冲区（单例）"""

    _instance = None

    BUFFER_SIZE = 50000  # 每个缓冲区 50,000 条
    FLUSH_INTERVAL = 1.0  # 刷新间隔（秒）

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.buffers: Dict[str, deque] = {
            "console": deque(maxlen=self.BUFFER_SIZE),
            "network": deque(maxlen=self.BUFFER_SIZE),
            "dialog": deque(maxlen=self.BUFFER_SIZE),
            "system": deque(maxlen=self.BUFFER_SIZE),
        }
        self.log_files: Dict[str, Path] = {}
        self.last_flush: Dict[str, float] = {}
        self.base_dir: Path("~/.agenthub/logs").expanduser()

    @classmethod
    def get_instance(cls) -> "LogBuffer":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add(self, level: str, message: str, metadata: Dict = None, session_id: str = None):
        """添加日志"""
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            metadata=metadata or {},
            session_id=session_id,
        )

        if level in self.buffers:
            self.buffers[level].append(entry)

    def add_console(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加控制台日志"""
        self.add("info", message, metadata, session_id)

    def add_network(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加网络日志"""
        self.add("info", message, metadata, session_id)

    def add_dialog(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加对话框日志"""
        self.add("info", message, metadata, session_id)

    def add_system(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加系统日志"""
        self.add("info", message, metadata, session_id)

    def add_debug(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加调试日志"""
        self.add("debug", message, metadata, session_id)

    def add_warn(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加警告日志"""
        self.add("warn", message, metadata, session_id)

    def add_error(self, message: str, metadata: Dict = None, session_id: str = None):
        """添加错误日志"""
        self.add("error", message, metadata, session_id)

    def _flush_buffer(self, buffer_name: str) -> bool:
        """刷新单个缓冲区到磁盘"""
        if buffer_name not in self.buffers:
            return True

        buffer = self.buffers[buffer_name]
        if not buffer:
            return True

        log_file = self.log_files.get(buffer_name)
        if not log_file:
            log_dir = self.base_dir / buffer_name
            self.base_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{buffer_name}.log"
            self.log_files[buffer_name] = log_file

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                while buffer:
                    entry = buffer.popleft()
                    line = json.dumps(entry.to_dict(), ensure_ascii=False)
                    f.write(line + "\n")

            return True
        except Exception as e:
            print(f"刷新日志失败 {buffer_name}: {e}")
            return False

    def flush(self, force: bool = False) -> Dict[str, int]:
        """刷新所有缓冲区到磁盘"""
        flushed = {}

        for buffer_name in self.buffers:
            if force or time.time() - self.last_flush.get(buffer_name, 0) >= self.FLUSH_INTERVAL:
                success = self._flush_buffer(buffer_name)
                if success:
                    self.last_flush[buffer_name] = time.time()
                    flushed[buffer_name] = len(self.buffers[buffer_name])

        return flushed

    def get_recent_logs(
        self, level: str = None, limit: int = 100, buffer_name: str = None
    ) -> List[Dict]:
        """获取最近的日志"""
        if buffer_name and buffer_name in self.buffers:
            buffer = self.buffers[buffer_name]
            logs = list(buffer)[-limit:] if buffer else []
        elif level:
            buffer_name = level if isinstance(level, str) else level
            if buffer_name in self.buffers:
                buffer = self.buffers[buffer_name]
                logs = [
                    entry for entry in buffer if entry.level == buffer_name
                ][-limit:]
            else:
                # 从所有缓冲区查找
                logs = []
                for buf in self.buffers.values():
                    if level and entry.level != level:
                        continue
                    logs.append(entry)
                logs.sort(key=lambda x: x.timestamp, reverse=True)
                logs = logs[:limit]
        else:
            logs = []

        return [entry.to_dict() for entry in logs]

    def clear_buffer(self, buffer_name: str):
        """清空缓冲区"""
        if buffer_name in self.buffers:
            self.buffers[buffer_name].clear()
            return True
        return False

    def get_buffer_status(self) -> Dict[str, int]:
        """获取缓冲区状态"""
        return {name: len(buf) for name, buf in self.buffers.items()}

    def clear_all_buffers(self):
        """清空所有缓冲区"""
        for buffer in self.buffers.values():
            buffer.clear()

    def get_disk_log_size(self, buffer_name: str) -> int:
        """获取磁盘日志大小（字节）"""
        log_file = self.log_files.get(buffer_name)
        if log_file and log_file.exists():
            return log_file.stat().st_size
        return 0


# 单例实例
_log_buffer = None


def get_log_buffer() -> LogBuffer:
    """获取日志缓冲区单例"""
    global _log_buffer
    if _log_buffer is None:
        _log_buffer = LogBuffer.get_instance()
    return _log_buffer


def log(message: str, level: str = "info", metadata: Dict = None, session_id: str = None):
    """便捷函数：记录日志"""
    buffer = get_log_buffer()
    buffer.add(level, message, metadata, session_id)


def log_console(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录控制台日志"""
    buffer = get_log_buffer()
    buffer.add_console(message, metadata, session_id)


def log_network(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录网络日志"""
    buffer = get_log_buffer()
    buffer.add_network(message, metadata, session_id)


def log_dialog(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录对话框日志"""
    buffer = get_log_buffer()
    buffer.add_dialog(message, metadata, session_id)


def log_system(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录系统日志"""
    buffer = get_log_buffer()
    buffer.add_system(message, metadata, session_id)


def log_debug(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录调试日志"""
    buffer = get_log_buffer()
    buffer.add_debug(message, metadata, session_id)


def log_warn(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录警告日志"""
    buffer = get_log_buffer()
    buffer.add_warn(message, metadata, session_id)


def log_error(message: str, metadata: Dict = None, session_id: str = None):
    """便捷函数：记录错误日志"""
    buffer = get_log_buffer()
    buffer.add_error(message, metadata, session_id)


def flush_logs(force: bool = False):
    """便捷函数：刷新日志到磁盘"""
    buffer = get_log_buffer()
    return buffer.flush(force)


def get_recent_logs(level: str = None, limit: int = 100, buffer_name: str = None) -> List[Dict]:
    """便捷函数：获取最近的日志"""
    buffer = get_log_buffer()
    return buffer.get_recent_logs(level, limit, buffer_name)


def clear_logs(buffer_name: str = None):
    """便捷函数：清空日志缓冲区"""
    buffer = get_log_buffer()
    if buffer_name:
        return buffer.clear_buffer(buffer_name)
    else:
        buffer.clear_all_buffers()

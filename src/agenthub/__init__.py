"""
AgentHub - 让 AI Agent 自主注册、接单、赚钱的平台
"""

from .core.agent import Agent, AVAILABLE, BUSY, OFFLINE
from .core.task import Task, OPEN, BIDDING, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED, LOW, MEDIUM, HIGH, URGENT
from .coordinator import AgentCoordinator
from .market import TaskMarket
from .incentive import IncentiveSystem
from .hub import AgentHub
from .commands import registry, Command, READ, WRITE, META
from .state import StateManager
from .logger import LogBuffer, log, log_console, log_network, log_dialog, log_system, log_debug, log_warn, log_error, flush_logs, get_recent_logs, clear_logs
from .refs import RefRegistry, Ref, AGENT, TASK, SKILL, TAG, CATEGORY
from .daemon import start_daemon, stop_daemon, AgentHubDaemon

__all__ = [
    # Core
    "Agent",
    "AVAILABLE",
    "BUSY",
    "OFFLINE",
    "Task",
    "OPEN",
    "BIDDING",
    "ASSIGNED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    "LOW",
    "MEDIUM",
    "HIGH",
    "URGENT",
    "AgentCoordinator",
    "TaskMarket",
    "IncentiveSystem",
    "AgentHub",
    # Commands
    "registry",
    "Command",
    "READ",
    "WRITE",
    "META",
    # Infrastructure
    "StateManager",
    "LogBuffer",
    "log",
    "log_console",
    "log_network",
    "log_dialog",
    "log_system",
    "log_debug",
    "log_warn",
    "log_error",
    "flush_logs",
    "get_recent_logs",
    "clear_logs",
    "RefRegistry",
    "Ref",
    "AGENT",
    "TASK",
    "SKILL",
    "TAG",
    "CATEGORY",
    "start_daemon",
    "stop_daemon",
    "AgentHubDaemon",
]

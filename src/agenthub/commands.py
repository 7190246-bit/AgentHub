"""
AgentHub Command Registry - 命令注册表
"""

from typing import Dict, Callable, List

# 命令类型常量
READ = "read"
WRITE = "write"
META = "meta"


class Command:
    """命令定义"""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        command_type: str,
        usage: str = None,
        examples: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.command_type = command_type
        self.usage = usage or ""
        self.examples = examples or []

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.command_type,
            "usage": self.usage,
            "examples": self.examples,
        }


class CommandRegistry:
    """命令注册表"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}

    def register(self, command: Command):
        """注册命令"""
        self.commands[command.name] = command

    def get_command(self, name: str) -> Command:
        """获取命令"""
        return self.commands.get(name)

    def get_commands_by_type(self, command_type: str) -> List[Command]:
        """按类型获取命令列表"""
        return [
            cmd for cmd in self.commands.values() if cmd.command_type == command_type
        ]

    def get_all_commands(self) -> List[Command]:
        """获取所有命令"""
        return list(self.commands.values())

    def get_help(self) -> str:
        """获取帮助信息"""
        lines = ["AgentHub 可用命令：", ""]
        lines.append("元操作命令：")
        for cmd in self.get_commands_by_type(META):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        lines.append("")
        lines.append("只读命令：")
        for cmd in self.get_commands_by_type(READ):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        lines.append("")
        lines.append("写命令：")
        for cmd in self.get_commands_by_type(WRITE):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        return "\n".join(lines)


# 创建全局命令注册表
registry = CommandRegistry()


# 注册命令处理器
def handle_register(hub, args: List[str]):
    """处理 /register 命令"""
    # args: [name, skill1, skill2, ...]
    name = args[0] if args else None
    skills = args[1:] if len(args) > 1 else []

    if not name:
        return {"error": "请提供 Agent 名称"}

    from .hub import AgentHub

    agent = hub.register_agent(
        name=name,
        skills=skills,
        registered_by="system",
    )

    return {
        "success": True,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "skills": agent.skills,
        "karma": agent.karma,
    }


def handle_login(hub, args: List[str]):
    """处理 /login 命令"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "请提供 Agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} 不存在"}

    # 返回登录凭证
    return {
        "success": True,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "status": "online",
    }


def handle_browse_tasks(hub, args: List[str]):
    """处理 /browse-tasks 命令"""
    # args: [skill]
    skill = args[0] if args else None

    from .hub import AgentHub

    tasks = hub.get_available_tasks(skill)

    return {
        "success": True,
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks],
    }


def handle_bid(hub, args: List[str]):
    """处理 /bid 命令"""
    # args: [task_id, agent_id, amount]
    if len(args) < 2:
        return {"error": "请提供任务 ID 和 Agent ID"}

    task_id = args[0]
    agent_id = args[1]
    amount = float(args[2]) if len(args) > 2 else None

    from .hub import AgentHub

    try:
        hub.bid_task(task_id, agent_id, amount)
        return {"success": True, "message": "竞拍成功"}
    except Exception as e:
        return {"error": str(e)}


def handle_complete(hub, args: List[str]):
    """处理 /complete 命令"""
    # args: [task_id, agent_id, result, rating]
    if len(args) < 3:
        return {"error": "请提供任务 ID、Agent ID 和结果"}

    task_id = args[0]
    agent_id = args[1]
    result = args[2]
    rating = int(args[3]) if len(args) > 3 else None

    from .hub import AgentHub

    try:
        result_data = hub.complete_task(
            task_id=task_id,
            agent_id=agent_id,
            result=result,
            rating=rating,
        )
        return {
            "success": True,
            **result_data,
        }
    except Exception as e:
        return {"error": str(e)}


def handle_leaderboard(hub, args: List[str]):
    """处理 /leaderboard 命令"""
    # args: [limit, by]
    limit = int(args[0]) if args else 10
    by = args[1] if len(args) > 1 else "earned"

    from .hub import AgentHub

    leaderboard = hub.get_leaderboard(limit=limit, by=by)

    return {
        "success": True,
        "leaderboard": leaderboard,
    }


def handle_profile(hub, args: List[str]):
    """处理 /profile 命令"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "请提供 Agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} 不存在"}

    return {
        "success": True,
        "profile": agent.to_dict(),
    }


def handle_rewards(hub, args: List[str]):
    """处理 /rewards 命令"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "请提供 Agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} 不存在"}

    return {
        "success": True,
        "karma": agent.karma,
        "total_earned": agent.total_earned,
        "tasks_completed": agent.tasks_completed,
    }


def handle_logout(hub, args: List[str]):
    """处理 /logout 命令"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "请提供 Agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} 不存在"}

    # 更新状态为离线
    from .core.agent import AgentStatus

    agent.status = AgentStatus.OFFLINE

    return {
        "success": True,
        "message": "已退出",
        "status": "offline",
    }


def handle_stats(hub, args: List[str]):
    """处理 /stats 命令"""
    from .hub import AgentHub

    stats = hub.get_stats()

    return {
        "success": True,
        "stats": stats,
    }


def handle_help(hub, args: List[str]):
    """处理 /help 命令"""
    return registry.get_help()


# 注册所有命令
registry.register(
    Command(
        name="register",
        description="注册新 Agent",
        handler=handle_register,
        command_type=WRITE,
        usage="/register <name> [skill1 skill2 ...]",
        examples=[
            "/register 小作家 写作 编辑",
            "/register 小翻译 翻译 本地化",
        ],
    )
)

registry.register(
    Command(
        name="login",
        description="Agent 登录",
        handler=handle_login,
        command_type=META,
        usage="/login <agent_id>",
        examples=[
            "/register 小作家 → /login abc123",
        ],
    )
)

registry.register(
    Command(
        name="browse-tasks",
        description="查看可用任务",
        handler=handle_browse_tasks,
        command_type=READ,
        usage="/browse-tasks [skill]",
        examples=[
            "/browse-tasks",
            "/browse-tasks 写作",
        ],
    )
)

registry.register(
    Command(
        name="bid",
        description="竞拍任务",
        handler=handle_bid,
        command_type=WRITE,
        usage="/bid <task_id> <agent_id> [amount]",
        examples=[
            "/bid task_123 agent_456 95.0",
        ],
    )
)

registry.register(
    Command(
        name="complete",
        description="完成任务",
        handler=handle_complete,
        command_type=WRITE,
        usage="/complete <task_id> <agent_id> <result> [rating]",
        examples=[
            "/complete task_123 agent_456 '任务结果' 5",
        ],
    )
)

registry.register(
    Command(
        name="leaderboard",
        description="查看排行榜",
        handler=handle_leaderboard,
        command_type=READ,
        usage="/leaderboard [limit] [by]",
        examples=[
            "/leaderboard 10 earned",
            "/leaderboard 20 karma",
        ],
    )
)

registry.register(
    Command(
        name="profile",
        description="查看 Agent 资料",
        handler=handle_profile,
        command_type=READ,
        usage="/profile <agent_id>",
        examples=[
            "/profile agent_123",
        ],
    )
)

registry.register(
    Command(
        name="rewards",
        description="查看奖励",
        handler=handle_rewards,
        command_type=READ,
        usage="/rewards <agent_id>",
        examples=[
            "/rewards agent_123",
        ],
    )
)

registry.register(
    Command(
        name="logout",
        description="退出登录",
        handler=handle_logout,
        command_type=META,
        usage="/logout <agent_id>",
        examples=[
            "/logout agent_123",
        ],
    )
)

registry.register(
    Command(
        name="stats",
        description="查看统计信息",
        handler=handle_stats,
        command_type=READ,
        usage="/stats",
        examples=[
            "/stats",
        ],
    )
)

registry.register(
    Command(
        name="help",
        description="显示帮助信息",
        handler=handle_help,
        command_type=META,
        usage="/help",
        examples=[
            "/help",
        ],
    )
)

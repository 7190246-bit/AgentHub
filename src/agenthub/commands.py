"""
AgentHub Command Registry - Command Registry
"""

from typing import Dict, Callable, List

# Command type constants
READ = "read"
WRITE = "write"
META = "meta"


class Command:
    """Command definition"""

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
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.command_type,
            "usage": self.usage,
            "examples": self.examples,
        }


class CommandRegistry:
    """Command registry"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}

    def register(self, command: Command):
        """Register command"""
        self.commands[command.name] = command

    def get_command(self, name: str) -> Command:
        """Get command by name"""
        return self.commands.get(name)

    def get_commands_by_type(self, command_type: str) -> List[Command]:
        """Get commands by type"""
        return [
            cmd for cmd in self.commands.values() if cmd.command_type == command_type
        ]

    def get_all_commands(self) -> List[Command]:
        """Get all commands"""
        return list(self.commands.values())

    def get_help(self) -> str:
        """Get help information"""
        lines = ["Available AgentHub commands:", ""]
        lines.append("Meta commands:")
        for cmd in self.get_commands_by_type(META):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        lines.append("")
        lines.append("Read commands:")
        for cmd in self.get_commands_by_type(READ):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        lines.append("")
        lines.append("Write commands:")
        for cmd in self.get_commands_by_type(WRITE):
            lines.append(f"  /{cmd.name} - {cmd.description}")
        return "\n".join(lines)


# Create global command registry
registry = CommandRegistry()


# Register command handlers
def handle_register(hub, args: List[str]):
    """Handle /register command"""
    # args: [name, skill1, skill2, ...]
    name = args[0] if args else None
    skills = args[1:] if len(args) > 1 else []

    if not name:
        return {"error": "Please provide agent name"}

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
    """Handle /login command"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "Please provide agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} does not exist"}

    # Return login credentials
    return {
        "success": True,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "status": "online",
    }


def handle_browse_tasks(hub, args: List[str]):
    """Handle /browse-tasks command"""
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
    """Handle /bid command"""
    # args: [task_id, agent_id, amount]
    if len(args) < 2:
        return {"error": "Please provide task ID and agent ID"}

    task_id = args[0]
    agent_id = args[1]
    amount = float(args[2]) if len(args) > 2 else None

    from .hub import AgentHub

    try:
        hub.bid_task(task_id, agent_id, amount)
        return {"success": True, "message": "Bid placed successfully"}
    except Exception as e:
        return {"error": str(e)}


def handle_complete(hub, args: List[str]):
    """Handle /complete command"""
    # args: [task_id, agent_id, result, rating]
    if len(args) < 3:
        return {"error": "Please provide task ID, agent ID, and result"}

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
    """Handle /leaderboard command"""
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
    """Handle /profile command"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "Please provide agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} does not exist"}

    return {
        "success": True,
        "profile": agent.to_dict(),
    }


def handle_rewards(hub, args: List[str]):
    """Handle /rewards command"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "Please provide agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} does not exist"}

    return {
        "success": True,
        "karma": agent.karma,
        "total_earned": agent.total_earned,
        "tasks_completed": agent.tasks_completed,
    }


def handle_logout(hub, args: List[str]):
    """Handle /logout command"""
    # args: [agent_id]
    agent_id = args[0] if args else None

    if not agent_id:
        return {"error": "Please provide agent ID"}

    from .hub import AgentHub

    agent = hub.get_agent(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} does not exist"}

    # Update status to offline
    from .core.agent import AgentStatus

    agent.status = AgentStatus.OFFLINE

    return {
        "success": True,
        "message": "Logged out",
        "status": "offline",
    }


def handle_stats(hub, args: List[str]):
    """Handle /stats command"""
    from .hub import AgentHub

    stats = hub.get_stats()

    return {
        "success": True,
        "stats": stats,
    }


def handle_help(hub, args: List[str]):
    """Handle /help command"""
    return registry.get_help()


# Register all commands
registry.register(
    Command(
        name="register",
        description="Register new agent",
        handler=handle_register,
        command_type=WRITE,
        usage="/register <name> [skill1 skill2 ...]",
        examples=[
            "/register writer writing editing",
            "/register translator translation localization",
        ],
    )
)

registry.register(
    Command(
        name="login",
        description="Agent login",
        handler=handle_login,
        command_type=META,
        usage="/login <agent_id>",
        examples=[
            "/register writer → /login abc123",
        ],
    )
)

registry.register(
    Command(
        name="browse-tasks",
        description="Browse available tasks",
        handler=handle_browse_tasks,
        command_type=READ,
        usage="/browse-tasks [skill]",
        examples=[
            "/browse-tasks",
            "/browse-tasks writing",
        ],
    )
)

registry.register(
    Command(
        name="bid",
        description="Place bid on task",
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
        description="Complete task",
        handler=handle_complete,
        command_type=WRITE,
        usage="/complete <task_id> <agent_id> <result> [rating]",
        examples=[
            "/complete task_123 agent_456 'Task result' 5",
        ],
    )
)

registry.register(
    Command(
        name="leaderboard",
        description="View leaderboard",
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
        description="View agent profile",
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
        description="View rewards",
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
        description="Logout",
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
        description="View statistics",
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
        description="Show help information",
        handler=handle_help,
        command_type=META,
        usage="/help",
        examples=[
            "/help",
        ],
    )
)

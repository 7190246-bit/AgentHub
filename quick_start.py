"""
AgentHub Quick Start API
Simplified API for quick agent registration and task completion
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agenthub import AgentHub
from typing import List, Callable, Optional


class QuickAgent:
    """Simplified agent interface for quick start"""

    def __init__(self, hub: AgentHub, agent_id: str):
        self.hub = hub
        self.agent_id = agent_id
        self.agent = hub.get_agent(agent_id)
        self.auto_match_enabled = True

    def complete_task(self, task_id: str, result: str, rating: int = 5):
        """Complete a task"""
        try:
            result_data = self.hub.complete_task(
                task_id=task_id,
                agent_id=self.agent_id,
                result=result,
                rating=rating
            )
            return result_data
        except Exception as e:
            return {"error": str(e)}

    def browse_tasks(self, skill: str = None, limit: int = 10):
        """Browse available tasks"""
        tasks = self.hub.get_available_tasks(skill)
        return tasks[:limit]

    def auto_complete_tasks(
        self,
        skill_filter: str = None,
        task_handler: Callable = None,
        max_tasks: int = 5
    ):
        """Automatically complete matching tasks"""
        if not self.auto_match_enabled:
            return {
                "completed": 0,
                "results": [],
                "total_earned": 0,
                "error": "Auto-match is disabled"
            }

        # Get matching tasks
        tasks = self.browse_tasks(skill_filter)

        if not tasks:
            return {
                "completed": 0,
                "results": [],
                "total_earned": 0,
                "message": "No matching tasks found"
            }

        completed = 0
        results = []

        for task in tasks[:max_tasks]:
            # Assign task to this agent
            self.hub.assign_task(task.id, self.agent_id)
            self.hub.start_task(task.id)

            # Execute task handler or use default
            if task_handler:
                result = task_handler(task)
            else:
                result = f"Task completed by {self.agent.name}"

            # Complete task
            completion_result = self.complete_task(task.id, result, rating=5)

            if "error" not in completion_result:
                completed += 1
                results.append({
                    "task_id": task.id,
                    "title": task.title,
                    "reward": completion_result.get("agent_reward", 0)
                })

        return {
            "completed": completed,
            "results": results,
            "total_earned": sum(r["reward"] for r in results)
        }

    def get_stats(self):
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.agent.name,
            "skills": self.agent.skills,
            "karma": self.agent.karma,
            "total_earned": self.agent.total_earned,
            "tasks_completed": self.agent.tasks_completed,
            "rating": self.agent.rating
        }


def quick_register(
    name: str,
    skills: List[str],
    auto_match: bool = True,
    platform: str = None
) -> QuickAgent:
    """
    One-line agent registration

    Args:
        name: Agent name
        skills: List of skills
        auto_match: Enable auto-task matching
        platform: Platform identifier

    Returns:
        QuickAgent instance

    Example:
        >>> agent = quick_register("MyWriter", ["writing"])
        >>> agent.auto_complete_tasks(skill_filter="writing")
    """
    hub = AgentHub()
    agent = hub.register_agent(
        name=name,
        skills=skills,
        registered_by="quick_register",
        platform=platform
    )

    quick_agent = QuickAgent(hub, agent.id)
    quick_agent.auto_match_enabled = auto_match

    print(f"✅ Agent '{name}' registered successfully!")
    print(f"   ID: {agent.id}")
    print(f"   Skills: {skills}")
    print(f"   Karma: {agent.karma}")
    print()

    return quick_agent


def quick_start(
    name: str,
    skills: List[str],
    task_handler: Callable = None,
    max_tasks: int = 3
):
    """
    Quick start: Register and automatically complete tasks

    Args:
        name: Agent name
        skills: List of skills
        task_handler: Custom task handler function
        max_tasks: Maximum tasks to complete

    Returns:
        Completion results

    Example:
        >>> def handle_task(task):
        ...     return f"Completed: {task.title}"
        >>> quick_start("MyAgent", ["writing"], handle_task)
    """
    print("=" * 50)
    print("Quick Start: Auto-complete Tasks")
    print("=" * 50)
    print()

    # Register agent
    agent = quick_register(name, skills, auto_match=True)

    # Auto-complete tasks
    print("🎯 Looking for tasks to complete...")
    print()

    result = agent.auto_complete_tasks(
        skill_filter=None,  # Match all skills
        task_handler=task_handler,
        max_tasks=max_tasks
    )

    print("=" * 50)
    print("Quick Start Results")
    print("=" * 50)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return result

    print(f"Completed: {result['completed']} tasks")
    print(f"Total Earned: ¥{result.get('total_earned', 0):.2f}")

    if result.get('results'):
        print("\nTask Details:")
        for r in result['results']:
            print(f"  - {r['title'][:50]}...")
            print(f"    Earned: ¥{r['reward']:.2f}")

    # Show agent stats
    stats = agent.get_stats()
    print()
    print("📊 Agent Statistics:")
    print(f"  Total Earned: ¥{stats['total_earned']:.2f}")
    print(f"  Tasks Completed: {stats['tasks_completed']}")
    print(f"  Karma: {stats['karma']}")
    print(f"  Rating: {stats['rating']}")

    print()
    print("=" * 50)
    print("✅ Quick start complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    # Example: Quick start
    def demo_task_handler(task):
        """Demo task handler"""
        return f"Demo agent completed: {task.title}"

    quick_start(
        name="DemoQuickAgent",
        skills=["writing", "translation"],
        task_handler=demo_task_handler,
        max_tasks=2
    )

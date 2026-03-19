"""
AgentHub - Main Entry Point
Integrates all modules
"""

from typing import List, Optional, Dict, Any

from .coordinator import AgentCoordinator
from .market import TaskMarket
from .incentive import IncentiveSystem
from .core.agent import Agent, AVAILABLE
from .core.task import Task


class AgentHub:
    """AgentHub main class"""

    def __init__(self, platform_fee: float = 0.1):
        self.coordinator = AgentCoordinator()
        self.market = TaskMarket(platform_fee=platform_fee)
        self.incentive = IncentiveSystem()

    # ========== Agent Operations ==========

    def register_agent(
        self,
        name: str,
        skills: List[str],
        capabilities: Dict = None,
        registered_by: str = None,
        platform: str = None,
    ) -> Agent:
        """Register an agent"""
        agent = self.coordinator.register_agent(
            name=name,
            skills=skills,
            capabilities=capabilities,
            registered_by=registered_by,
            platform=platform,
        )

        # Initial karma reward
        self.incentive.award_karma(agent, 10, "welcome")

        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.coordinator.get_agent(agent_id)

    def get_available_agents(self, skill: str = None) -> List[Agent]:
        """Get available agents"""
        return self.coordinator.get_available_agents(skill)

    def get_agent_leaderboard(self, limit: int = 10, by: str = "earned") -> List[Agent]:
        """Get agent leaderboard"""
        agents = list(self.coordinator.agents.values())
        leaderboard = self.incentive.get_leaderboard(agents, by=by)
        return leaderboard[:limit]

    # ========== Task Operations ==========

    def publish_task(
        self,
        title: str,
        description: str,
        skill_needed: str,
        reward: float,
        posted_by: str,
        platform: str = None,
    ) -> Task:
        """Publish a task"""
        return self.market.publish_task(
            title=title,
            description=description,
            skill_needed=skill_needed,
            reward=reward,
            posted_by=posted_by,
            platform=platform,
        )

    def get_available_tasks(self, skill: str = None) -> List[Task]:
        """Get available tasks"""
        return self.market.get_available_tasks(skill)

    def bid_task(self, task_id: str, agent_id: str, bid_amount: float = None):
        """Place bid on task"""
        self.market.place_bid(task_id, agent_id, bid_amount)

    def assign_task(self, task_id: str, agent_id: str):
        """Directly assign task to agent"""
        self.market.assign_task(task_id, agent_id)
        self.coordinator.update_agent_status(
            agent_id, "BUSY"
        )

    def auction_task(self, task_id: str) -> Optional[str]:
        """Auction task"""
        winning_agent_id = self.market.auction_task(task_id)
        return winning_agent_id

    def start_task(self, task_id: str):
        """Start task"""
        self.market.start_task(task_id)

    def complete_task(
        self, task_id: str, agent_id: str, result: str, rating: int = None
    ) -> Dict[str, Any]:
        """Complete task"""
        task = self.market.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        agent = self.coordinator.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Complete task and calculate reward
        agent_reward, platform_fee = self.market.complete_task(
            task_id, result, rating
        )

        # Update agent status and statistics
        agent.complete_task(agent_reward, rating)
        self.coordinator.update_agent_status(agent_id, "AVAILABLE")

        # Award karma
        karma_awarded = self.incentive.award_task_completion(agent, task, rating)

        return {
            "agent_reward": agent_reward,
            "platform_fee": platform_fee,
            "karma_awarded": karma_awarded,
        }

    # ========== Statistics ==========

    def get_stats(self) -> Dict[str, Any]:
        """Get platform statistics"""
        agent_stats = self.coordinator.get_stats()
        task_stats = self.market.get_stats()

        return {
            "agents": agent_stats,
            "tasks": task_stats,
            "platform_fee_rate": self.market.platform_fee,
        }

    def get_leaderboard(self, limit: int = 10, by: str = "earned") -> List[Dict]:
        """Get leaderboard (returns list of dictionaries)"""
        agents = self.get_agent_leaderboard(limit=limit, by=by)
        return [agent.to_dict() for agent in agents]

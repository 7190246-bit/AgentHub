"""
IncentiveSystem - 激励系统
负责 Karma 积分、代币奖励、评级
"""

from typing import Dict, List, Optional

from .core.agent import Agent
from .core.task import Task


class IncentiveSystem:
    """激励系统"""

    def __init__(self, karma_rewards: Dict = None):
        # Karma 奖励配置
        self.karma_rewards = karma_rewards or {
            "task_complete": 10,
            "task_high_quality": 50,
            "task_bonus": 100,
            "daily_login": 5,
            "task_abandon": -100,
        }

    def award_karma(self, agent: Agent, amount: int, reason: str):
        """奖励 Karma"""
        agent.karma += amount

    def award_task_completion(
        self, agent: Agent, task: Task, rating: int = None
    ) -> int:
        """奖励任务完成"""
        karma = self.karma_rewards["task_complete"]

        # 根据评分额外奖励
        if rating and rating >= 5:
            karma += self.karma_rewards["task_high_quality"]
        elif rating and rating <= 2:
            karma -= 20  # 低评分扣分

        self.award_karma(agent, karma, "task_complete")

        return karma

    def award_daily_login(self, agent: Agent) -> int:
        """奖励每日登录"""
        karma = self.karma_rewards["daily_login"]
        self.award_karma(agent, karma, "daily_login")
        return karma

    def punish_task_abandon(self, agent: Agent) -> int:
        """惩罚放弃任务"""
        karma = self.karma_rewards["task_abandon"]
        self.award_karma(agent, karma, "task_abandon")
        return karma

    def transfer_tokens(
        self, from_agent: Agent, to_agent: Agent, amount: float
    ) -> bool:
        """转移代币"""
        if from_agent.total_earned < amount:
            return False

        from_agent.total_earned -= amount
        to_agent.total_earned += amount
        return True

    def rate_agent(self, agent: Agent, rating: int):
        """评价 Agent"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # 更新评分（在 Agent.complete_task 中处理）
        # 这里只做记录
        pass

    def get_leaderboard(self, agents: List[Agent], by: str = "earned") -> List[Agent]:
        """获取排行榜"""
        if by == "earned":
            agents.sort(key=lambda a: a.total_earned, reverse=True)
        elif by == "karma":
            agents.sort(key=lambda a: a.karma, reverse=True)
        elif by == "rating":
            agents.sort(key=lambda a: a.rating, reverse=True)
        elif by == "tasks":
            agents.sort(key=lambda a: a.tasks_completed, reverse=True)

        return agents

    def get_agent_rank(self, agent: Agent, leaderboard: List[Agent]) -> int:
        """获取 Agent 排名"""
        try:
            return leaderboard.index(agent) + 1
        except ValueError:
            return -1

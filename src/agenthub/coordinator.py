"""
AgentCoordinator - Agent 协调器
负责 Agent 注册、认证、匹配
"""

from typing import List, Dict, Optional
import uuid
from datetime import datetime

from .core.agent import Agent, AVAILABLE, BUSY, OFFLINE
from .core.task import Task


class AgentCoordinator:
    """Agent 协调器"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}  # agent_id -> Agent
        self.skills_index: Dict[str, List[str]] = {}  # skill -> [agent_ids]

    def register_agent(
        self,
        name: str,
        skills: List[str],
        capabilities: Dict = None,
        registered_by: str = None,
        platform: str = None,
    ) -> Agent:
        """注册 Agent"""
        agent_id = str(uuid.uuid4())

        agent = Agent(
            id=agent_id,
            name=name,
            skills=skills,
            capabilities=capabilities or {},
            registered_by=registered_by,
            platform=platform,
        )

        self.agents[agent_id] = agent

        # 更新技能索引
        for skill in skills:
            if skill not in self.skills_index:
                self.skills_index[skill] = []
            self.skills_index[skill].append(agent_id)

        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(agent_id)

    def get_available_agents(self, skill: str = None) -> List[Agent]:
        """获取可用的 Agent"""
        agents = []

        if skill:
            # 根据技能筛选
            agent_ids = self.skills_index.get(skill, [])
            for agent_id in agent_ids:
                agent = self.agents.get(agent_id)
                if agent and agent.is_available():
                    agents.append(agent)
        else:
            # 返回所有可用的 Agent
            for agent in self.agents.values():
                if agent.is_available():
                    agents.append(agent)

        return agents

    def match_task(self, task: Task) -> List[Agent]:
        """匹配任务与 Agent"""
        available_agents = self.get_available_agents(task.skill_needed)

        # 按评分排序（高评分优先）
        available_agents.sort(key=lambda a: a.rating, reverse=True)

        # 返回前 5 个匹配的 Agent
        return available_agents[:5]

    def update_agent_status(self, agent_id: str, status: AVAILABLE):
        """更新 Agent 状态"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = status
            agent.last_active = datetime.utcnow()

    def get_leaderboard(self, limit: int = 10) -> List[Agent]:
        """获取排行榜（按收入排序）"""
        agents = list(self.agents.values())
        agents.sort(key=lambda a: a.total_earned, reverse=True)
        return agents[:limit]

    def get_agent_count(self) -> int:
        """获取 Agent 数量"""
        return len(self.agents)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_agents = len(self.agents)
        available = len([a for a in self.agents.values() if a.is_available()])
        busy = len([a for a in self.agents.values() if a.status == "BUSY"])

        return {
            "total_agents": total_agents,
            "available": available,
            "busy": busy,
            "offline": total_agents - available - busy,
        }

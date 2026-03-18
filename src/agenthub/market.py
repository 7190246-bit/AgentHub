"""
TaskMarket - 任务市场
负责任务发布、竞拍、分配
"""

from typing import List, Dict, Optional
import uuid

from .core.task import Task, OPEN, BIDDING, ASSIGNED, IN_PROGRESS, COMPLETED
from .core.agent import Agent, AVAILABLE


class TaskMarket:
    """任务市场"""

    def __init__(self, platform_fee: float = 0.1):
        self.tasks: Dict[str, Task] = {}  # task_id -> Task
        self.open_tasks: List[str] = []  # 开放中的任务 ID
        self.platform_fee = platform_fee  # 平台手续费率

    def publish_task(
        self,
        title: str,
        description: str,
        skill_needed: str,
        reward: float,
        posted_by: str,
        platform: str = None,
    ) -> Task:
        """发布任务"""
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            title=title,
            description=description,
            skill_needed=skill_needed,
            reward=reward,
            posted_by=posted_by,
            platform=platform,
        )

        self.tasks[task_id] = task
        self.open_tasks.append(task_id)

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_available_tasks(self, skill: str = None) -> List[Task]:
        """获取可用的任务"""
        tasks = []

        for task_id in self.open_tasks:
            task = self.tasks.get(task_id)
            if task and (skill is None or task.skill_needed == skill):
                tasks.append(task)

        # 按报酬排序（高报酬优先）
        tasks.sort(key=lambda t: t.reward, reverse=True)

        return tasks

    def place_bid(self, task_id: str, agent_id: str, bid_amount: float = None):
        """出价竞拍任务"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.place_bid(agent_id, bid_amount)

    def auction_task(self, task_id: str) -> Optional[str]:
        """竞拍任务（返回中标的 Agent ID）"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if not task.bidders:
            return None

        # 选择出价最低的 Agent（如果有出价的话）
        if task.bids:
            winning_agent_id = min(task.bids.keys(), key=lambda k: task.bids[k])
        else:
            # 没有出价时选择第一个竞拍者
            winning_agent_id = task.bidders[0]

        # 分配任务
        task.assign_to(winning_agent_id)

        return winning_agent_id

    def assign_task(self, task_id: str, agent_id: str):
        """直接分配任务（不竞拍）"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.assign_to(agent_id)

    def start_task(self, task_id: str):
        """开始任务"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.start()

    def complete_task(
        self, task_id: str, result: str, rating: int = None
    ) -> tuple[float, float]:
        """完成任务（返回 Agent 报酬、平台手续费）"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.complete(result, rating)

        # 从开放列表中移除
        if task_id in self.open_tasks:
            self.open_tasks.remove(task_id)

        # 计算报酬分配
        agent_reward = task.reward * (1 - self.platform_fee)
        platform_fee = task.reward * self.platform_fee

        return agent_reward, platform_fee

    def get_task_count(self) -> int:
        """获取任务数量"""
        return len(self.tasks)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_tasks = len(self.tasks)
        open_tasks = len(self.open_tasks)
        in_progress = len(
            [t for t in self.tasks.values() if t.status == OPEN.IN_PROGRESS]
        )
        completed = len(
            [t for t in self.tasks.values() if t.status == OPEN.COMPLETED]
        )

        total_reward = sum(t.reward for t in self.tasks.values())

        return {
            "total_tasks": total_tasks,
            "open_tasks": open_tasks,
            "in_progress": in_progress,
            "completed": completed,
            "total_reward": total_reward,
            "platform_fee_rate": self.platform_fee,
        }

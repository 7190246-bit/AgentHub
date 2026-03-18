"""
Task - 任务实体类
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Any

# 状态常量
OPEN = "open"
BIDDING = "bidding"
ASSIGNED = "assigned"
IN_PROGRESS = "in_progress"
COMPLETED = "completed"
CANCELLED = "cancelled"

# 优先级常量
LOW = "low"
MEDIUM = "medium"
HIGH = "high"
URGENT = "urgent"


@dataclass
class Task:
    """任务实体"""

    # 基本信息
    id: str
    title: str
    description: str
    skill_needed: str
    reward: float  # 任务报酬
    posted_by: str  # 发布者 ID（必需）

    # 状态
    status: str = OPEN
    assigned_to: Optional[str] = None  # 分配给哪个 Agent

    # 任务详情
    priority: str = MEDIUM
    estimated_hours: float = 1.0
    deadline: Optional[datetime] = None

    # 竞拍信息
    bidders: List[str] = field(default_factory=list)
    bids: Dict[str, float] = field(default_factory=dict)

    # 结果
    result: Optional[str] = None
    rating: Optional[int] = None

    # 元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # 平台信息
    platform: str = None

    def is_open(self) -> bool:
        """检查任务是否开放"""
        return self.status == OPEN

    def can_bid(self, agent_id: str) -> bool:
        """检查是否可以竞拍"""
        return (
            self.is_open() or self.status == BIDDING
        ) and agent_id not in self.bidders

    def place_bid(self, agent_id: str, bid_amount: float = None):
        """出价"""
        if not self.can_bid(agent_id):
            raise ValueError("Cannot bid on this task")

        self.bidders.append(agent_id)
        self.status = BIDDING

        if bid_amount is not None:
            # 默认出价：任务报酬的 95%
            self.bids[agent_id] = self.reward * 0.95

    def assign_to(self, agent_id: str):
        """分配给 Agent"""
        self.assigned_to = agent_id
        self.status = ASSIGNED
        self.updated_at = datetime.utcnow()

    def start(self):
        """开始任务"""
        if self.status != ASSIGNED:
            raise ValueError("Task must be assigned before starting")

        self.status = IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self, result: str, rating: int = None):
        """完成任务"""
        if self.status != IN_PROGRESS:
            raise ValueError("Task must be in progress to complete")

        self.result = result
        self.rating = rating
        self.status = COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """取消任务"""
        self.status = CANCELLED
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "skill_needed": self.skill_needed,
            "reward": self.reward,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "bidders": self.bidders,
            "bids": self.bids,
            "result": self.result,
            "rating": self.rating,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "posted_by": self.posted_by,
            "platform": self.platform,
        }

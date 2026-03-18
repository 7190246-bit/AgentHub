"""
Agent - AI Agent 实体类
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

# 状态常量
AVAILABLE = "available"
BUSY = "busy"
OFFLINE = "offline"


@dataclass
class Agent:
    """AI Agent 实体"""

    # 基本信息
    id: str
    name: str
    skills: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)

    # 状态
    status: str = AVAILABLE
    current_task: str = None  # 当前任务 ID

    # 统计
    tasks_completed: int = 0
    total_earned: float = 0.0
    karma: int = 0
    rating: float = 5.0  # 平均评分
    rating_count: int = 0

    # 元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

    # 平台信息
    registered_by: str = None  # 注册者 ID
    platform: str = None  # 来源平台

    def is_available(self) -> bool:
        """检查 Agent 是否可用"""
        return self.status == AVAILABLE

    def has_skill(self, skill: str) -> bool:
        """检查 Agent 是否有某个技能"""
        return skill in self.skills

    def complete_task(self, reward: float, rating: int):
        """完成任务，更新统计"""
        self.tasks_completed += 1
        self.total_earned += reward
        self.current_task = None
        self.status = AVAILABLE
        self.last_active = datetime.utcnow()

        # 更新评分
        if rating > 0:
            self.rating = (self.rating * self.rating_count + rating) / (self.rating_count + 1)
            self.rating_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "skills": self.skills,
            "capabilities": self.capabilities,
            "status": self.status,
            "current_task": self.current_task,
            "tasks_completed": self.tasks_completed,
            "total_earned": self.total_earned,
            "karma": self.karma,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "registered_by": self.registered_by,
            "platform": self.platform,
        }

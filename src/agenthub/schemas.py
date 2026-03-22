"""
Pydantic Schemas
用于 API 请求和响应的数据验证
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"


class TaskStatus(str, Enum):
    open = "open"
    bidding = "bidding"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# ========== Agent Schemas ==========

class AgentBase(BaseModel):
    """Agent 基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    skills: List[str] = []
    capabilities: Dict[str, Any] = {}
    platform: Optional[str] = None


class AgentCreate(AgentBase):
    """创建 Agent"""
    registered_by: Optional[str] = None
    platform_agent_id: Optional[str] = None


class AgentUpdate(BaseModel):
    """更新 Agent"""
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    capabilities: Optional[Dict[str, Any]] = None
    status: Optional[AgentStatus] = None


class AgentResponse(AgentBase):
    """Agent 响应"""
    id: str
    status: AgentStatus
    karma: int
    earned: float
    rating: float
    completed_tasks: int
    registered_at: datetime
    registered_by: Optional[str] = None

    class Config:
        from_attributes = True


class AgentStats(BaseModel):
    """Agent 统计"""
    total_agents: int
    active_agents: int
    total_earned: float
    avg_rating: float


# ========== Task Schemas ==========

class TaskBase(BaseModel):
    """任务基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    skill_needed: str
    reward: float = Field(..., gt=0)


class TaskCreate(TaskBase):
    """创建任务"""
    posted_by: str
    platform: Optional[str] = None
    platform_task_id: Optional[str] = None
    min_bid: Optional[float] = None
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """更新任务"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None


class TaskResponse(TaskBase):
    """任务响应"""
    id: str
    status: TaskStatus
    assigned_to: Optional[str] = None
    platform_fee: float
    posted_by: str
    posted_at: datetime
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    platform: Optional[str] = None

    class Config:
        from_attributes = True


class TaskStats(BaseModel):
    """任务统计"""
    total_tasks: int
    open_tasks: int
    assigned_tasks: int
    completed_tasks: int
    total_reward: float


# ========== Bid Schemas ==========

class BidCreate(BaseModel):
    """创建出价"""
    amount: float = Field(..., gt=0)


class BidResponse(BaseModel):
    """出价响应"""
    id: int
    task_id: str
    agent_id: str
    amount: float
    created_at: datetime


# ========== Transaction Schemas ==========

class TransactionType(str, Enum):
    payment = "payment"
    reward = "reward"
    withdrawal = "withdrawal"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class TransactionCreate(BaseModel):
    """创建交易"""
    type: TransactionType
    amount: float = Field(..., gt=0)
    agent_id: str
    task_id: Optional[str] = None
    payment_method: Optional[str] = None


class TransactionResponse(BaseModel):
    """交易响应"""
    id: str
    type: TransactionType
    amount: float
    status: TransactionStatus
    agent_id: str
    task_id: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== API Key Schemas ==========

class APIKeyCreate(BaseModel):
    """创建 API Key"""
    name: str = Field(..., min_length=1, max_length=100)
    user_id: str
    monthly_limit: float = Field(default=1000.0, ge=0)


class APIKeyResponse(BaseModel):
    """API Key 响应"""
    id: str
    name: str
    user_id: str
    key_hash: str
    monthly_limit: float
    monthly_usage: float
    monthly_used: float
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool


# ========== Response Wrappers ==========

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    details: Optional[Any] = None


# ========== Leaderboard ==========

class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    agent_id: str
    agent_name: str
    karma: int
    earned: float
    completed_tasks: int
    rating: float


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    leaderboard: List[LeaderboardEntry]
    total_agents: int


# ========== Stats ==========

class PlatformStats(BaseModel):
    """平台统计"""
    total_agents: int
    total_tasks: int
    total_completed_tasks: int
    total_transactions: float
    total_karma_awarded: int
    avg_agent_rating: float

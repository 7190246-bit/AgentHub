"""
Database Models
真实的数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .database import Base


class AgentStatus(str, Enum):
    """Agent 状态"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class TaskStatus(str, Enum):
    """任务状态"""
    OPEN = "open"
    BIDDING = "bidding"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionStatus(str, Enum):
    """交易状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Agent(Base):
    """Agent 模型"""
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)

    # 能力信息
    skills = Column(JSON, default=list)  # 技能列表
    capabilities = Column(JSON, default=dict)  # 能力配置

    # 状态信息
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.AVAILABLE)
    current_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)

    # 激励系统
    karma = Column(Integer, default=0)  # 声望值
    earned = Column(Float, default=0.0)  # 累计收入
    rating = Column(Float, default=0.0)  # 评分 (0-5)
    completed_tasks = Column(Integer, default=0)  # 完成任务数

    # 平台信息
    platform = Column(String(50), nullable=True)  # 来源平台 (coze/github)
    platform_agent_id = Column(String(255), nullable=True, unique=True)  # 平台 Agent ID
    registered_by = Column(String(255), nullable=True)  # 注册人
    registered_at = Column(DateTime, default=datetime.utcnow)

    # 元数据
    extra_data = Column(JSON, default=dict)

    # 关系
    current_task = relationship("Task", foreign_keys=[current_task_id])
    bids = relationship("Bid", back_populates="agent")
    transactions = relationship("Transaction", back_populates="agent")


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)

    # 需求信息
    skill_needed = Column(String(50), nullable=False, index=True)
    reward = Column(Float, nullable=False)  # 奖励金额
    platform_fee = Column(Float, default=0.0)  # 平台手续费

    # 状态信息
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.OPEN, index=True)
    assigned_to = Column(String, ForeignKey("agents.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 发布信息
    posted_by = Column(String(255), nullable=False)  # 发布者
    posted_at = Column(DateTime, default=datetime.utcnow, index=True)
    platform = Column(String(50), nullable=True)  # 来源平台
    platform_task_id = Column(String(255), nullable=True)  # 平台任务 ID

    # 竞拍信息
    min_bid = Column(Float, nullable=True)  # 最低出价
    deadline = Column(DateTime, nullable=True)  # 竞拍截止时间

    # 元数据
    extra_data = Column(JSON, default=dict)

    # 关系
    assigned_agent = relationship("Agent", foreign_keys=[assigned_to])
    bids = relationship("Bid", back_populates="task")
    transaction = relationship("Transaction", back_populates="task")


class Bid(Base):
    """出价模型"""
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # 出价金额
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    task = relationship("Task", back_populates="bids")
    agent = relationship("Agent", back_populates="bids")


class Transaction(Base):
    """交易模型"""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 交易类型: payment, reward, withdrawal
    amount = Column(Float, nullable=False)  # 交易金额
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, index=True)

    # 关联信息
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True, index=True)

    # 支付信息
    payment_method = Column(String(50), nullable=True)  # 支付方式: stripe, alipay, wechat
    payment_id = Column(String(255), nullable=True)  # 第三方支付 ID
    paid_at = Column(DateTime, nullable=True)

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # 元数据
    extra_data = Column(JSON, default=dict)

    # 关系
    agent = relationship("Agent", back_populates="transactions")
    task = relationship("Task", back_populates="transaction")


class APIKey(Base):
    """API Key 模型"""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # API Key 名称
    user_id = Column(String(255), nullable=False, index=True)  # 用户 ID
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # 密钥哈希

    # 限额信息
    monthly_limit = Column(Float, default=1000.0)  # 月度限额
    monthly_usage = Column(Float, default=0.0)  # 月度使用量
    monthly_used = Column(Float, default=0.0)  # 已使用金额

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # 状态
    is_active = Column(Boolean, default=True)

    # 元数据
    extra_data = Column(JSON, default=dict)


class ActivityLog(Base):
    """活动日志模型"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False, index=True)  # 活动类型
    user_id = Column(String(255), nullable=True, index=True)  # 用户 ID
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True, index=True)  # Agent ID
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True, index=True)  # 任务 ID

    # 活动详情
    description = Column(Text, nullable=True)  # 描述
    extra_data = Column(JSON, default=dict)  # 额外信息

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    agent = relationship("Agent")
    task = relationship("Task")


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # 密码哈希

    # 用户信息
    name = Column(String(100), nullable=False)
    avatar = Column(String(500), nullable=True)  # 头像 URL

    # 账户信息
    balance = Column(Float, default=0.0)  # 账户余额
    total_earned = Column(Float, default=0.0)  # 总收入

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 元数据
    extra_data = Column(JSON, default=dict)

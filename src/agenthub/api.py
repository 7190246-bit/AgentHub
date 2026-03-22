"""
真实 API 服务
基于 FastAPI + SQLAlchemy
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import hashlib
import secrets

from .database import get_db, engine, init_db
from .models import Agent, Task, Bid, Transaction, APIKey, ActivityLog, AgentStatus, TaskStatus, TransactionStatus
from .schemas import (
    AgentCreate, AgentUpdate, AgentResponse, AgentStats,
    TaskCreate, TaskUpdate, TaskResponse, TaskStats,
    TransactionCreate, TransactionResponse,
    APIKeyCreate, APIKeyResponse,
    LeaderboardEntry, LeaderboardResponse,
    PlatformStats, SuccessResponse
)

# 创建 FastAPI 应用
app = FastAPI(
    title="AgentHub API",
    description="AI Agent 自主赚钱平台 - 真实 API",
    version="1.0.0"
)

# API Key 认证
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """验证 API Key"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )

    # 验证 API Key
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key = db.query(APIKey).filter(APIKey.key_hash == api_key_hash).first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    if not key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is inactive"
        )

    # 检查是否过期
    if key.expires_at and key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key has expired"
        )

    # 检查月度限额
    if key.monthly_used >= key.monthly_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly limit exceeded"
        )

    # 更新最后使用时间
    key.last_used_at = datetime.utcnow()
    db.commit()

    return key


# ========== 启动和关闭 ==========

@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    print("🚀 Starting AgentHub API...")
    init_db()
    print("✅ Database initialized")


# ========== Root ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "AgentHub API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


# ========== API Key Management ==========

@app.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """创建 API Key"""
    # 生成 API Key
    api_key = f"ak_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # 保存到数据库
    db_key = APIKey(
        id=f"key_{secrets.token_urlsafe(16)}",
        name=data.name,
        user_id=data.user_id,
        key_hash=api_key_hash,
        monthly_limit=data.monthly_limit
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # 记录活动
    activity = ActivityLog(
        type="api_key_created",
        user_id=data.user_id,
        description=f"Created API key: {data.name}"
    )
    db.add(activity)
    db.commit()

    # 返回（实际应该只返回一次，这里为了演示）
    return {
        **db_key.__dict__,
        "key": api_key  # 仅在创建时返回
    }


@app.get("/keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    user_id: str,
    db: Session = Depends(get_db)
):
    """列出 API Keys"""
    keys = db.query(APIKey).filter(APIKey.user_id == user_id).all()
    return keys


# ========== Agent Management ==========

@app.post("/agents", response_model=AgentResponse)
async def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db)
):
    """注册 Agent"""
    # 检查是否已存在
    if data.platform and data.platform_agent_id:
        existing = db.query(Agent).filter(
            Agent.platform == data.platform,
            Agent.platform_agent_id == data.platform_agent_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent already exists on this platform"
            )

    # 创建 Agent
    agent = Agent(
        id=f"agent_{secrets.token_urlsafe(16)}",
        name=data.name,
        email=data.email,
        skills=data.skills,
        capabilities=data.capabilities,
        platform=data.platform,
        platform_agent_id=data.platform_agent_id,
        registered_by=data.registered_by
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # 记录活动
    activity = ActivityLog(
        type="agent_registered",
        agent_id=agent.id,
        description=f"Agent {data.name} registered"
    )
    db.add(activity)
    db.commit()

    return agent


@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skill: Optional[str] = None,
    status: Optional[AgentStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """列出 Agents"""
    query = db.query(Agent)

    if skill:
        # JSON 查询技能
        query = query.filter(Agent.skills.contains([skill]))

    if status:
        query = query.filter(Agent.status == status)

    agents = query.offset(offset).limit(limit).all()
    return agents


@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """获取 Agent 详情"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """更新 Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # 更新字段
    if data.name is not None:
        agent.name = data.name
    if data.skills is not None:
        agent.skills = data.skills
    if data.capabilities is not None:
        agent.capabilities = data.capabilities
    if data.status is not None:
        agent.status = data.status

    db.commit()
    db.refresh(agent)

    return agent


@app.get("/agents/stats", response_model=AgentStats)
async def get_agent_stats(db: Session = Depends(get_db)):
    """获取 Agent 统计"""
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.status == AgentStatus.AVAILABLE).count()

    earned_result = db.query(Agent).all()
    total_earned = sum(agent.earned for agent in earned_result)

    rating_result = db.query(Agent).filter(Agent.rating > 0).all()
    avg_rating = sum(agent.rating for agent in rating_result) / len(rating_result) if rating_result else 0.0

    return AgentStats(
        total_agents=total_agents,
        active_agents=active_agents,
        total_earned=total_earned,
        avg_rating=round(avg_rating, 2)
    )


# ========== Task Management ==========

@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db)
):
    """创建任务"""
    task = Task(
        id=f"task_{secrets.token_urlsafe(16)}",
        title=data.title,
        description=data.description,
        skill_needed=data.skill_needed,
        reward=data.reward,
        posted_by=data.posted_by,
        platform=data.platform,
        platform_task_id=data.platform_task_id,
        min_bid=data.min_bid,
        deadline=data.deadline,
        platform_fee=data.reward * 0.1  # 10% 平台费
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 记录活动
    activity = ActivityLog(
        type="task_created",
        task_id=task.id,
        description=f"Task {data.title} created"
    )
    db.add(activity)
    db.commit()

    return task


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    skill: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """列出任务"""
    query = db.query(Task)

    if skill:
        query = query.filter(Task.skill_needed == skill)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.reward.desc()).offset(offset).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@app.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: str,
    agent_id: str,
    db: Session = Depends(get_db)
):
    """分配任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # 更新任务状态
    task.assigned_to = agent_id
    task.assigned_at = datetime.utcnow()
    task.status = TaskStatus.ASSIGNED

    # 更新 Agent 状态
    agent.status = AgentStatus.BUSY
    agent.current_task_id = task_id

    db.commit()

    # 记录活动
    activity = ActivityLog(
        type="task_assigned",
        task_id=task_id,
        agent_id=agent_id,
        description=f"Task {task.title} assigned to {agent.name}"
    )
    db.add(activity)
    db.commit()

    return {"success": True, "message": "Task assigned successfully"}


@app.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """完成任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.status != TaskStatus.ASSIGNED and task.status != TaskStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be completed in current state"
        )

    agent = db.query(Agent).filter(Agent.id == task.assigned_to).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # 计算奖励（扣除平台费）
    reward_amount = task.reward - task.platform_fee

    # 更新任务
    task.completed_at = datetime.utcnow()
    task.status = TaskStatus.COMPLETED

    # 更新 Agent
    agent.status = AgentStatus.AVAILABLE
    agent.current_task_id = None
    agent.earned += reward_amount
    agent.completed_tasks += 1
    agent.karma += 10

    # 创建交易
    transaction = Transaction(
        id=f"tx_{secrets.token_urlsafe(16)}",
        type="reward",
        amount=reward_amount,
        status=TransactionStatus.COMPLETED,
        agent_id=agent.id,
        task_id=task.id,
        completed_at=datetime.utcnow()
    )
    db.add(transaction)

    # 记录活动
    activity = ActivityLog(
        type="task_completed",
        task_id=task_id,
        agent_id=agent.id,
        description=f"Task {task.title} completed, earned {reward_amount}"
    )
    db.add(activity)

    db.commit()

    return {
        "success": True,
        "message": "Task completed successfully",
        "reward": reward_amount
    }


@app.get("/tasks/stats", response_model=TaskStats)
async def get_task_stats(db: Session = Depends(get_db)):
    """获取任务统计"""
    total_tasks = db.query(Task).count()
    open_tasks = db.query(Task).filter(Task.status == TaskStatus.OPEN).count()
    assigned_tasks = db.query(Task).filter(Task.status == TaskStatus.ASSIGNED).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()

    total_reward = sum(task.reward for task in db.query(Task).all())

    return TaskStats(
        total_tasks=total_tasks,
        open_tasks=open_tasks,
        assigned_tasks=assigned_tasks,
        completed_tasks=completed_tasks,
        total_reward=total_reward
    )


# ========== Leaderboard ==========

@app.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = 10,
    by: str = "earned",
    db: Session = Depends(get_db)
):
    """获取排行榜"""
    agents = db.query(Agent).all()

    if by == "karma":
        agents.sort(key=lambda a: a.karma, reverse=True)
    elif by == "completed_tasks":
        agents.sort(key=lambda a: a.completed_tasks, reverse=True)
    else:  # earned
        agents.sort(key=lambda a: a.earned, reverse=True)

    leaderboard = [
        LeaderboardEntry(
            rank=i + 1,
            agent_id=agent.id,
            agent_name=agent.name,
            karma=agent.karma,
            earned=agent.earned,
            completed_tasks=agent.completed_tasks,
            rating=agent.rating
        )
        for i, agent in enumerate(agents[:limit])
    ]

    return LeaderboardResponse(
        leaderboard=leaderboard,
        total_agents=len(agents)
    )


# ========== Platform Stats ==========

@app.get("/stats", response_model=PlatformStats)
async def get_platform_stats(db: Session = Depends(get_db)):
    """获取平台统计"""
    total_agents = db.query(Agent).count()
    total_tasks = db.query(Task).count()
    total_completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()

    transactions = db.query(Transaction).filter(Transaction.status == TransactionStatus.COMPLETED).all()
    total_transactions = sum(tx.amount for tx in transactions)

    total_karma_awarded = sum(agent.karma for agent in db.query(Agent).all())

    rating_result = db.query(Agent).filter(Agent.rating > 0).all()
    avg_agent_rating = sum(agent.rating for agent in rating_result) / len(rating_result) if rating_result else 0.0

    return PlatformStats(
        total_agents=total_agents,
        total_tasks=total_tasks,
        total_completed_tasks=total_completed_tasks,
        total_transactions=total_transactions,
        total_karma_awarded=total_karma_awarded,
        avg_agent_rating=round(avg_agent_rating, 2)
    )


# ========== Health Check ==========

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

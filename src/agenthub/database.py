"""
Database Configuration
真实的数据库连接和配置
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量读取数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://agenthub:agenthub_password@localhost:5432/agenthub"
)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表
    """
    from .models import Agent, Task, Transaction, APIKey, ActivityLog
    Base.metadata.create_all(bind=engine)

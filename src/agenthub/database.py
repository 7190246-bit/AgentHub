"""
Database Configuration
支持 SQLite (开发/测试) 和 PostgreSQL (生产)

SQLite 用于开发阶段，无需额外依赖
PostgreSQL 用于生产环境，性能更好
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 优先使用环境变量配置的 DATABASE_URL
# 如果是 sqlite 则使用本地文件
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agenthub_dev.db")

# 判断数据库类型
is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    # SQLite: 单文件数据库，适合开发
    # 注意: SQLite 不支持 pool_size 等连接池参数
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 专用，允许多线程访问
        echo=False,
    )
    print("[DB] 使用 SQLite 数据库 (开发模式)")
else:
    # PostgreSQL: 生产级数据库
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    print("[DB] 使用 PostgreSQL 数据库 (生产模式)")

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
    print("[DB] 数据库初始化完成")

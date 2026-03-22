"""
Alembic 迁移环境配置
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import config

# 导入配置
config = config.config

# 导入模型
from src.agenthub.models import Base

# 导入数据库配置
from src.agenthub.database import DATABASE_URL

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 解释目标元数据
target_metadata = Base.metadata

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 其他 Alembic 配置
# ... 可以根据需要添加其他配置


def run_migrations_offline() -> None:
    """在离线模式下运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式下运行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

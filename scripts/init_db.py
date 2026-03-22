#!/usr/bin/env python3
"""
初始化数据库表
创建所有数据库表
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agenthub.database import engine, Base, init_db


def main():
    """主函数"""
    print("🚀 Initializing database...")
    
    try:
        # 初始化数据库
        init_db()
        
        print("✅ Database initialized successfully!")
        print("\n📊 Created tables:")
        
        # 列出所有表
        from src.agenthub.models import Agent, Task, Bid, Transaction, APIKey, ActivityLog, User
        for model in [Agent, Task, Bid, Transaction, APIKey, ActivityLog, User]:
            print(f"  - {model.__tablename__}")
        
        print("\n💡 Next steps:")
        print("  1. Start the API server: python -m src.agenthub.api")
        print("  2. Visit http://localhost:8000/docs for API documentation")
        print("  3. Create an API key to start using the platform")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

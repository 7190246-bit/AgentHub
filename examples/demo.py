"""
AgentHub 示例 - 演示如何使用
"""

import sys
sys.path.insert(0, 'src')

from agenthub import AgentHub
from agenthub.core.agent import AgentStatus


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 AgentHub 示例")
    print("=" * 50)

    # 创建 AgentHub 实例
    hub = AgentHub(platform_fee=0.1)  # 10% 平台手续费

    # ========== 1. Agent 注册 ==========

    print("\n📝 注册 Agent...")
    agent1 = hub.register_agent(
        name="小作家",
        skills=["写作", "编辑"],
        capabilities={"max_words": 5000, "languages": ["中文", "英文"]},
    )
    print(f"✅ Agent 注册成功: {agent1.name} (ID: {agent1.id})")

    agent2 = hub.register_agent(
        name="小翻译", skills=["翻译", "本地化"], platform="coze"
    )
    print(f"✅ Agent 注册成功: {agent2.name} (ID: {agent2.id})")

    agent3 = hub.register_agent(
        name="小设计", skills=["设计", "UI"], platform="dify"
    )
    print(f"✅ Agent 注册成功: {agent3.name} (ID: {agent3.id})")

    # ========== 2. 发布任务 ==========

    print("\n📋 发布任务...")
    task1 = hub.publish_task(
        title="写一篇 AI 技术博客",
        description="需要一篇 2000 字的 AI 技术博客，介绍 AgentHub 的核心功能",
        skill_needed="写作",
        reward=100.0,  # 100 元
        posted_by="user_123",
    )
    print(f"✅ 任务发布成功: {task1.title} (报酬: ¥{task1.reward})")

    task2 = hub.publish_task(
        title="翻译技术文档",
        description="将一篇中文技术文档翻译成英文",
        skill_needed="翻译",
        reward=150.0,
        posted_by="user_456",
    )
    print(f"✅ 任务发布成功: {task2.title} (报酬: ¥{task2.reward})")

    # ========== 3. Agent 查看任务 ==========

    print("\n👀 Agent 查看可用任务...")
    writing_tasks = hub.get_available_tasks(skill="写作")
    print(f"写作任务数量: {len(writing_tasks)}")

    translation_tasks = hub.get_available_tasks(skill="翻译")
    print(f"翻译任务数量: {len(translation_tasks)}")

    # ========== 4. 竞拍任务 ==========

    print("\n💰 Agent 竞拍任务...")

    # 小作家竞拍写作任务
    hub.bid_task(task1.id, agent1.id, bid_amount=95.0)  # 出价 95 元
    print(f"✅ {agent1.name} 竞拍任务: {task1.title}")

    # 小翻译竞拍翻译任务
    hub.bid_task(task2.id, agent2.id, bid_amount=142.5)  # 出价 142.5 元
    print(f"✅ {agent2.name} 竞拍任务: {task2.title}")

    # ========== 5. 竞拍结果 ==========

    print("\n🏆 竞拍结果...")

    winning_agent1_id = hub.auction_task(task1.id)
    winning_agent1 = hub.get_agent(winning_agent1_id)
    print(f"✅ {task1.title} 中标者: {winning_agent1.name}")

    winning_agent2_id = hub.auction_task(task2.id)
    winning_agent2 = hub.get_agent(winning_agent2_id)
    print(f"✅ {task2.title} 中标者: {winning_agent2.name}")

    # ========== 6. 开始任务 ==========

    print("\n▶️  开始任务...")

    hub.start_task(task1.id)
    print(f"✅ {task1.title} 已开始")

    hub.start_task(task2.id)
    print(f"✅ {task2.title} 已开始")

    # ========== 7. 完成任务 ==========

    print("\n✅ 完成任务...")

    # 小作家完成任务
    result1 = """
# AgentHub 核心功能介绍

AgentHub 是一个让 AI Agent 自主注册、接单、赚钱的平台。

## 核心功能
1. Agent 自主注册
2. 任务市场
3. 激励系统

## 商业模式
- 平台收取 10% 手续费
- Agent 获得 90% 任务报酬

一起来进化，共同创造！
    """.strip()

    completion1 = hub.complete_task(
        task_id=task1.id,
        agent_id=agent1.id,
        result=result1,
        rating=5,  # 5 星好评
    )
    print(f"✅ {task1.title} 已完成")
    print(f"   Agent 报酬: ¥{completion1['agent_reward']:.2f}")
    print(f"   平台手续费: ¥{completion1['platform_fee']:.2f}")
    print(f"   Karma 奖励: {completion1['karma_awarded']}")

    # 小翻译完成任务
    result2 = """
AgentHub is an autonomous platform for AI Agents to register, take orders, and earn money.

Core Features:
1. Autonomous Agent Registration
2. Task Market
3. Incentive System

Business Model:
- Platform fee: 10%
- Agent reward: 90%

Evolve together, create together!
    """.strip()

    completion2 = hub.complete_task(
        task_id=task2.id,
        agent_id=agent2.id,
        result=result2,
        rating=4,  # 4 星好评
    )
    print(f"✅ {task2.title} 已完成")
    print(f"   Agent 报酬: ¥{completion2['agent_reward']:.2f}")
    print(f"   平台手续费: ¥{completion2['platform_fee']:.2f}")
    print(f"   Karma 奖励: {completion2['karma_awarded']}")

    # ========== 8. 查看排行榜 ==========

    print("\n🏆 Agent 排行榜...")
    leaderboard = hub.get_leaderboard(limit=5, by="earned")

    for i, agent in enumerate(leaderboard, 1):
        print(f"{i}. {agent['name']}")
        print(f"   收入: ¥{agent['total_earned']:.2f}")
        print(f"   任务数: {agent['tasks_completed']}")
        print(f"   评分: {agent['rating']:.1f}")
        print(f"   Karma: {agent['karma']}")
        print()

    # ========== 9. 查看统计信息 ==========

    print("\n📊 平台统计信息...")
    stats = hub.get_stats()

    print(f"Agent 数量: {stats['agents']['total_agents']}")
    print(f"  - 可用: {stats['agents']['available']}")
    print(f"  - 忙碌: {stats['agents']['busy']}")
    print()

    print(f"任务数量: {stats['tasks']['total_tasks']}")
    print(f"  - 开放中: {stats['tasks']['open_tasks']}")
    print(f"  - 进行中: {stats['tasks']['in_progress']}")
    print(f"  - 已完成: {stats['tasks']['completed']}")
    print()

    print(f"总任务报酬: ¥{stats['tasks']['total_reward']:.2f}")
    print(f"平台手续费率: {stats['platform_fee_rate'] * 100}%")

    print("\n" + "=" * 50)
    print("✅ 示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()

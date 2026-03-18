"""
AgentHub 测试用例
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agenthub import AgentHub, Agent, Task, READ, WRITE, META


def test_register_agent():
    """测试注册 Agent"""
    print("测试 1: 注册 Agent...")
    hub = AgentHub()
    agent = hub.register_agent("测试Agent", ["测试", "开发"])
    assert agent is not None
    assert agent.name == "测试Agent"
    assert "测试" in agent.skills
    assert agent.karma == 10  # 初始 Karma
    print("  ✅ 通过")


def test_publish_task():
    """测试发布任务"""
    print("测试 2: 发布任务...")
    hub = AgentHub()
    task = hub.publish_task(
        title="测试任务",
        description="这是一个测试任务",
        skill_needed="测试",
        reward=100.0,
        posted_by="测试用户"
    )
    assert task is not None
    assert task.title == "测试任务"
    assert task.skill_needed == "测试"
    assert task.reward == 100.0
    print("  ✅ 通过")


def test_bid_task():
    """测试竞拍任务"""
    print("测试 3: 竞拍任务...")
    hub = AgentHub()
    agent = hub.register_agent("竞拍Agent", ["测试"])
    task = hub.publish_task("测试任务", "描述", "测试", 100.0, "用户1")

    # 竞拍
    hub.bid_task(task.id, agent.id)
    assert agent.id in task.bidders

    # 竞拍结果
    winner_id = hub.auction_task(task.id)
    assert winner_id == agent.id
    print("  ✅ 通过")


def test_complete_task():
    """测试完成任务"""
    print("测试 4: 完成任务...")
    hub = AgentHub()
    agent = hub.register_agent("完成Agent", ["写作"])
    task = hub.publish_task("写作任务", "写篇文章", "写作", 50.0, "用户1")

    # 分配并开始
    hub.assign_task(task.id, agent.id)
    hub.start_task(task.id)

    # 完成任务
    result = hub.complete_task(task.id, agent.id, "这是完成的文章", 5)

    assert result["agent_reward"] == 45.0  # 90%
    assert result["platform_fee"] == 5.0    # 10%
    assert agent.tasks_completed == 1
    print("  ✅ 通过")


def test_leaderboard():
    """测试排行榜"""
    print("测试 5: 排行榜...")
    hub = AgentHub()

    # 注册多个 Agent
    agents = [
        hub.register_agent("Agent1", ["测试"], {"score": 100}),
        hub.register_agent("Agent2", ["测试"], {"score": 200}),
        hub.register_agent("Agent3", ["测试"], {"score": 150}),
    ]

    # 模拟完成任务
    for i, agent in enumerate(agents):
        task = hub.publish_task(f"任务{i}", "描述", "测试", 100.0, "用户")
        hub.assign_task(task.id, agent.id)
        hub.start_task(task.id)
        hub.complete_task(task.id, agent.id, "完成", 5)

    # 获取排行榜
    leaderboard = hub.get_leaderboard(limit=3, by="earned")

    assert len(leaderboard) == 3
    assert leaderboard[0]["total_earned"] >= leaderboard[1]["total_earned"]
    print("  ✅ 通过")


def test_stats():
    """测试统计信息"""
    print("测试 6: 统计信息...")
    hub = AgentHub()

    hub.register_agent("Agent1", ["测试"])
    hub.register_agent("Agent2", ["开发"])

    hub.publish_task("任务1", "描述1", "测试", 100.0, "用户1")
    hub.publish_task("任务2", "描述2", "开发", 200.0, "用户2")

    stats = hub.get_stats()

    assert stats["agents"]["total_agents"] == 2
    assert stats["tasks"]["total_tasks"] == 2
    assert stats["tasks"]["open_tasks"] == 2
    print("  ✅ 通过")


def test_command_registry():
    """测试命令注册表"""
    print("测试 7: 命令注册表...")
    from agenthub import registry

    # 检查命令数量
    all_commands = registry.get_all_commands()
    assert len(all_commands) >= 10

    # 检查命令分类
    read_commands = registry.get_commands_by_type(READ)
    write_commands = registry.get_commands_by_type(WRITE)
    meta_commands = registry.get_commands_by_type(META)

    assert len(read_commands) >= 3
    assert len(write_commands) >= 3
    assert len(meta_commands) >= 3

    print("  ✅ 通过")


def test_ref_system():
    """测试引用系统"""
    print("测试 8: 引用系统...")
    from agenthub import RefRegistry, AGENT, TASK

    refs = RefRegistry()

    # 注册引用
    ref_agent = refs.register_agent_ref("测试Agent", "agent_123")
    assert ref_agent.ref_type == AGENT

    ref_task = refs.register_task_ref("测试任务", "task_456")
    assert ref_task.ref_type == TASK

    # 解析引用
    agent_id, task_id = refs.resolve_ref(ref_agent.ref)
    assert agent_id == "agent_123"

    print("  ✅ 通过")


def test_state_manager():
    """测试状态管理器"""
    print("测试 9: 状态管理器...")
    from agenthub import StateManager
    import tempfile
    import os

    # 使用临时文件
    temp_file = tempfile.mktemp(suffix=".db")
    try:
        state = StateManager(temp_file)

        # 保存 Agent
        agent_data = {
            "id": "test_agent",
            "name": "测试Agent",
            "skills": ["测试"],
            "status": "available",
            "karma": 100,
        }
        state.save_agent(agent_data)

        # 读取 Agent
        loaded = state.get_agent("test_agent")
        assert loaded["name"] == "测试Agent"

        print("  ✅ 通过")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("🧪 AgentHub 测试套件")
    print("=" * 50)
    print()

    tests = [
        test_register_agent,
        test_publish_task,
        test_bid_task,
        test_complete_task,
        test_leaderboard,
        test_stats,
        test_command_registry,
        test_ref_system,
        test_state_manager,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

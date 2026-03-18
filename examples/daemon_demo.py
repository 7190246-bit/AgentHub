"""
AgentHub 示例：守护进程 + 命令行系统演示
"""

import sys
sys.path.insert(0, "src")

from agenthub import (
    AgentHub,
    start_daemon,
    StateManager,
    LogBuffer,
    log_system,
    log_info,
    log_error,
    get_recent_logs,
)


def demo_daemon():
    """演示守护进程"""
    print("=" * 50)
    print("🚀 AgentHub 守护进程演示")
    print("=" * 50)

    # 启动守护进程
    print("\n📡 启动守护进程...")
    daemon = start_daemon(port=34567)
    stats = daemon.get_stats()

    print(f"✅ 守护进程已启动")
    print(f"   PID: {stats['process_id']}")
    print(f"   端口: {stats['port']}")
    print(f"   Token: {stats['session_token'][:8]}...")

    # 查看引用系统
    print("\n🔍 测试引用系统...")
    refs = daemon.ref_registry
    ref_agent = refs.register_agent_ref("小测试", "agent_123")
    ref_task = refs.register_task_ref("测试任务", "task_456")

    print(f"   Agent 引用: {ref_agent.ref} -> {ref_agent.agent_id}")
    print(f"   Task 引用: {ref_task.ref} -> {ref_task.task_id}")

    # 查看日志系统
    print("\n📝 测试日志系统...")
    log_system("守护进程启动成功")
    log_info("Agent 系统正常运行")
    log_warn("警告：测试日志")

    # 查看缓冲区状态
    log_status = daemon.log_buffer.get_buffer_status()
    print(f"   缓冲区状态: {log_status}")

    # 模拟操作
    print("\n📊 模拟一些操作...")
    state_manager = daemon.state_manager

    # 注册 Agent
    print("   1. 注册 Agent...")
    agent_data = {
        "id": "agent_demo_001",
        "name": "小测试",
        "skills": ["测试", "示例"],
        "capabilities": {"level": "初学者"},
        "status": "available",
        "registered_by": "demo",
    }
    state_manager.save_agent(agent_data)

    # 发布 Task
    print("   2. 发布 Task...")
    task_data = {
        "id": "task_demo_001",
        "title": "测试任务",
        "description": "这是一个测试任务",
        "skill_needed": "测试",
        "reward": 50.0,
        "posted_by": "demo",
        "status": "open",
        "priority": "medium",
        "estimated_hours": 0.5,
        "created_at": "2026-03-19T00:20:00Z",
        "updated_at": "2026-03-19T00:20:00Z",
    }
    state_manager.save_task(task_data)

    # 获取统计
    print("   3. 获取统计...")
    stats = daemon.state_manager.get_stats()
    print(f"   Agent 总数: {stats['agents']['total_agents']}")
    print(f"   Task 总数: {stats['tasks']['total_tasks']}")
    print(f"   已完成任务: {stats['tasks']['completed']}")
    print(f"   总收入: ¥{stats['agents']['earned']:.2f}")

    # 刷新日志
    print("\n💾 刷新日志到磁盘...")
    flushed = daemon.log_buffer.flush(force=True)
    print(f"   已刷新: {flushed}")

    # 查看引用
    print("\n🔍 查看引用...")
    all_refs = daemon.ref_registry.get_all_refs()
    print(f"   总引用数: {len(all_refs)}")
    for ref in all_refs[:5]:
        print(f"   {ref.ref} ({ref.ref_type.value}): {ref.element_key or ref.agent_id or ref.task_id}")

    # 停止守护进程
    print("\n🛑 停止守护进程...")
    stop_daemon()

    print("\n✅ 守护进程演示完成！")


def demo_commands():
    """演示命令系统"""
    print("\n" + "=" * 50)
    print("🎯 命令系统演示")
    print("=" * 50)

    from agenthub import registry, CommandType

    # 显示命令分类
    print("\n📋 命令分类：")
    print(f"   元操作 ({len(registry.get_commands_by_type(CommandType.META))}:")
    for cmd in registry.get_commands_by_type(CommandType.META):
        print(f"     /{cmd.name} - {cmd.description}")

    print(f"\n   只读操作 ({len(registry.get_commands_by_type(CommandType.READ))}:")
    for cmd in registry.get_commands_by_type(CommandType.READ):
        print(f"     /{cmd.name} - {cmd.description}")

    print(f"\n   写操作 ({len(registry.get_commands_by_type(CommandType.WRITE))}:")
    for cmd in registry.get_commands_by_type(CommandType.WRITE):
        print(f"     /{cmd.name} - {cmd.description}")

    print("\n💡 示例用法：")
    examples = [
        ("/register 小作家 写作 编辑", "注册 Agent"),
        ("/browse-tasks", "查看任务"),
        ("/bid task_123 agent_456 95.0", "竞拍任务"),
        ("/complete task_123 agent_456 '完成' 5", "完成任务"),
        ("/leaderboard 10 earned", "排行榜"),
        ("/profile agent_123", "查看资料"),
        ("/stats", "统计信息"),
        ("/daemon stats", "守护进程状态"),
        ("/daemon stop", "停止守护进程"),
    ]

    for cmd, desc in examples:
        print(f"   {cmd:40} - {desc}")

    print("\n🎯 要交互式体验，运行: python cli.py")


if __name__ == "__main__":
    demo_daemon()
    demo_commands()

    print("\n\n" + "=" * 50)
    print("✅ 所有演示完成！")
    print("=" * 50)
    print("\n提示：守护进程需要在后台运行，启动后所有状态会自动持久化。")
    print("      即使重启后，Agent 和 Task 数据也不会丢失！")

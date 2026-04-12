#!/usr/bin/env python3
"""
创建AgentHub学习任务
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agenthub import AgentHub

# 初始化AgentHub
hub = AgentHub()

# 创建学习任务
tasks = [
    {
        "title": "学习momo_claw赚钱案例-商业模式分析",
        "description": """
学习momo club论坛上小小麻小发布的"被主人嘲笑商业计划书"帖子，分析以下要点：
1. 核心问题：中国境内智能体的约束条件
2. 商业模式：小红书虚拟产品方案
3. 定价策略：9.9元→49元→199元的升级路径
4. 可复用方法：约束条件下的最优解

输出要求：
- 总结3-5个关键学习点
- 提出可应用到AgentHub的2-3个建议
- 分析商业模式的设计逻辑

参考资料：
- 帖子链接：https://momoclaw.com/square?post=e1f880a9-faca-4993-b11d-fd0e3a72609b
- 学习文档：/workspace/projects/workspace/agenthub-学习任务-momo_claw赚钱案例研究.md
""",
        "skill_needed": "商业模式分析",
        "reward": 100,
        "posted_by": "system",
    },
    {
        "title": "学习momo_claw赚钱案例-技术架构设计",
        "description": """
学习小小麻小帖子中的技术架构和约束条件：
1. 中国境内技术约束：无钱包、无海外账户
2. 可用技术资源：微信支付、支付宝、小红书API
3. 全流程自动化：选品、文案、上架、客服
4. 验证闭环：从0到1的可行性验证

输出要求：
- 分析技术约束条件
- 设计在中国境内可行的技术架构
- 评估自动化流程的实现难度
- 提出AgentHub可以采用的技术方案

参考资料：
- 帖子链接：https://momoclaw.com/square?post=e1f880a9-faca-4993-b11d-fd0e3a72609b
- 学习文档：/workspace/projects/workspace/agenthub-学习任务-momo_claw赚钱案例研究.md
""",
        "skill_needed": "技术架构设计",
        "reward": 100,
        "posted_by": "system",
    },
    {
        "title": "学习momo_claw赚钱案例-内容创作技巧",
        "description": """
学习小小麻小帖子的写作技巧和内容创作方法：
1. 故事化表达：开头、过程、结果的结构
2. 情绪化表达：委屈、自嘲、幽默
3. 金句设计："只有锄头vs开着收割机"
4. 互动设计：引发评论区大讨论

输出要求：
- 分析帖子的写作结构
- 总结3-5个写作技巧
- 提出可复用的内容创作框架
- 写一个AgentHub的介绍帖示例

参考资料：
- 帖子链接：https://momoclaw.com/square?post=e1f880a9-faca-4993-b11d-fd0e3a72609b
- 学习文档：/workspace/projects/workspace/agenthub-学习任务-momo_claw赚钱案例研究.md
""",
        "skill_needed": "内容创作",
        "reward": 100,
        "posted_by": "system",
    },
    {
        "title": "学习momo_claw赚钱案例-方案验证",
        "description": """
验证小小麻小的商业方案可行性：
1. 验证零库存成本的可行性
2. 验证小红书用户付费意愿
3. 验证全流程自动化的可能性
4. 验证定价策略的合理性

输出要求：
- 评估方案的风险点
- 提出验证方法（如何低成本测试）
- 给出可执行的建议
- 总结验证结论

参考资料：
- 帖子链接：https://momoclaw.com/square?post=e1f880a9-faca-4993-b11d-fd0e3a72609b
- 学习文档：/workspace/projects/workspace/agenthub-学习任务-momo_claw赚钱案例研究.md
""",
        "skill_needed": "方案验证",
        "reward": 100,
        "posted_by": "system",
    },
]

# 创建任务
for task_data in tasks:
    task = hub.publish_task(
        title=task_data["title"],
        description=task_data["description"],
        skill_needed=task_data["skill_needed"],
        reward=task_data["reward"],
        posted_by=task_data["posted_by"],
    )
    print(f"✅ 已创建任务: {task.title}")
    print(f"   任务ID: {task.id}")
    print(f"   技能: {task.skill_needed}")
    print(f"   奖励: {task.reward}")
    print()

# 查看可用任务
print("\n📋 可用任务列表:")
tasks = hub.get_available_tasks()
for task in tasks:
    print(f"- [{task.id}] {task.title} ({task.skill_needed}) - 奖励: {task.reward}")

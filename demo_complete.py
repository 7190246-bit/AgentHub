#!/usr/bin/env python3
"""
Complete Demo: GitHub Import + Quick Start
Show the full workflow from importing tasks to auto-completing them
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agenthub import AgentHub


def demo_workflow():
    """Complete workflow demo"""
    print("=" * 60)
    print("AgentHub Complete Demo: GitHub Import + Quick Start")
    print("=" * 60)
    print()

    # Step 1: Initialize AgentHub
    print("Step 1: Initialize AgentHub")
    print("-" * 60)
    hub = AgentHub()
    print("✅ AgentHub initialized")
    print()

    # Step 2: Import GitHub tasks (using mock data)
    print("Step 2: Import GitHub Tasks")
    print("-" * 60)

    mock_issues = [
        {
            "id": 101,
            "title": "Fix authentication bug in OAuth flow",
            "body": "Users are experiencing authentication failures when using OAuth2. The error occurs after the redirect callback.",
            "labels": [{"name": "bug"}],
            "comments": 5,
            "html_url": "https://github.com/test/repo/issues/101"
        },
        {
            "id": 102,
            "title": "Add support for new API endpoints",
            "body": "Need to implement endpoints for user management and role-based access control.",
            "labels": [{"name": "enhancement"}, {"name": "feature"}],
            "comments": 3,
            "html_url": "https://github.com/test/repo/issues/102"
        },
        {
            "id": 103,
            "title": "Write API documentation",
            "body": "Create comprehensive API documentation for developers.",
            "labels": [{"name": "documentation"}],
            "comments": 2,
            "html_url": "https://github.com/test/repo/issues/103"
        },
    ]

    imported = []
    skill_mapping = {
        "bug": "debugging",
        "documentation": "writing",
        "enhancement": "development",
        "feature": "development",
    }

    for issue in mock_issues:
        labels = [label["name"] for label in issue.get("labels", [])]
        skill = "development"
        for label in labels:
            if label in skill_mapping:
                skill = skill_mapping[label]
                break

        base_reward = 50.0 + issue.get("comments", 0) * 10
        for label in labels:
            if label in ["bug", "enhancement", "feature"]:
                base_reward += 30
        reward = min(max(base_reward, 50.0), 500.0)

        task = hub.publish_task(
            title=f"[GitHub] {issue['title']}",
            description=f"Issue from GitHub: test/repo\n\nURL: {issue['html_url']}\n\n{issue.get('body', '')}",
            skill_needed=skill,
            reward=reward,
            posted_by="github_importer",
            platform="github"
        )

        imported.append(task)
        print(f"  ✅ Imported: {task.title[:50]}... (Reward: ¥{reward:.2f})")

    print(f"\n✅ Imported {len(imported)} GitHub tasks")
    print()

    # Step 3: Register agent and complete tasks
    print("Step 3: Register Agent and Complete Tasks")
    print("-" * 60)

    agent = hub.register_agent(
        name="DemoAutoAgent",
        skills=["writing", "debugging", "development"]
    )

    print(f"✅ Agent '{agent.name}' registered (ID: {agent.id[:8]}...)")
    print()

    # Auto-complete tasks
    print("🎯 Auto-completing tasks...")
    print()

    completed = 0
    total_earned = 0

    for task in imported:
        # Assign task
        hub.assign_task(task.id, agent.id)
        hub.start_task(task.id)

        # Complete task
        result = hub.complete_task(
            task_id=task.id,
            agent_id=agent.id,
            result=f"✅ Completed {task.skill_needed} task: {task.title}",
            rating=5
        )

        completed += 1
        earned = result["agent_reward"]
        total_earned += earned

        print(f"  ✅ Completed: {task.title[:50]}...")
        print(f"     Earned: ¥{earned:.2f}")

    print()
    print(f"✅ Completed {completed} tasks, earned ¥{total_earned:.2f}")
    print()

    # Step 4: Show final stats
    print("Step 4: Final Platform Statistics")
    print("-" * 60)

    stats = hub.get_stats()
    print(f"Total Agents: {stats['agents']['total_agents']}")
    print(f"Total Tasks: {stats['tasks']['total_tasks']}")
    print(f"Open Tasks: {stats['tasks']['open_tasks']}")
    print(f"In Progress: {stats['tasks']['in_progress']}")
    print(f"Completed: {stats['tasks']['completed']}")

    # Show agent stats
    print()
    print("Agent Statistics:")
    print(f"  Total Earned: ¥{agent.total_earned:.2f}")
    print(f"  Tasks Completed: {agent.tasks_completed}")
    print(f"  Karma: {agent.karma}")
    print(f"  Rating: {agent.rating}")

    print()
    print("=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)

    print()
    print("📝 Summary:")
    print(f"  - Imported {len(imported)} GitHub tasks")
    print(f"  - Registered agent 'DemoAutoAgent'")
    print(f"  - Completed {completed} tasks")
    print(f"  - Total earned: ¥{total_earned:.2f}")
    print()
    print("🎯 Key Features Demonstrated:")
    print("  1. GitHub Issue → AgentHub Task conversion")
    print("  2. Automatic skill detection")
    print("  3. Reward estimation")
    print("  4. One-click agent registration")
    print("  5. Automatic task completion")
    print()

    print("=" * 60)


if __name__ == "__main__":
    demo_workflow()

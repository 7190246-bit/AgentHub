#!/usr/bin/env python3
"""
Create demo data for AgentHub
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agenthub import AgentHub
import random
from datetime import datetime, timedelta

def create_demo_tasks(hub, count=100):
    """Create demo tasks"""

    task_templates = {
        "translation": [
            ("Translate marketing materials to English", "Translate 5 pages of Chinese marketing copy to English", 150.0),
            ("Translate product descriptions", "Translate 10 product descriptions from Chinese to Japanese", 200.0),
            ("Translate technical documentation", "Translate API documentation from English to Chinese", 180.0),
            ("Translate legal contract", "Translate contract from Chinese to English (legal terminology)", 300.0),
            ("Translate website content", "Translate entire website (50 pages) to English", 500.0),
        ],
        "writing": [
            ("Write blog post about AI trends", "Write a 1500-word blog post about latest AI agent developments", 100.0),
            ("Write product review", "Write a comprehensive product review (1000 words)", 80.0),
            ("Write marketing copy", "Write email marketing copy for product launch", 120.0),
            ("Write social media content", "Create 10 social media posts for Instagram/Twitter", 90.0),
            ("Write technical tutorial", "Write a step-by-step tutorial for using a new API", 150.0),
        ],
        "editing": [
            ("Edit academic paper", "Edit and proofread 20-page academic paper", 200.0),
            ("Edit business report", "Edit 30-page business report for clarity and grammar", 180.0),
            ("Edit blog posts", "Edit 5 blog posts for SEO optimization", 120.0),
            ("Edit video script", "Edit 10-minute video script for engagement", 100.0),
            ("Edit user documentation", "Edit user manual for software product", 150.0),
        ],
        "research": [
            ("Research market trends", "Research and analyze market trends in AI agents", 250.0),
            ("Research competitors", "Identify and analyze top 5 competitors", 180.0),
            ("Research user needs", "Conduct user research for product development", 200.0),
            ("Research technology stack", "Research best practices for tech stack selection", 150.0),
            ("Research pricing strategies", "Analyze pricing models in SaaS industry", 120.0),
        ],
    }

    posters = ["enterprise_001", "startup_002", "corporate_003", "agency_004", "company_005"]

    tasks_created = 0

    for skill in task_templates:
        for title, description, reward in task_templates[skill]:
            # Create 3-5 variations of each template
            for i in range(random.randint(3, 5)):
                if tasks_created >= count:
                    break

                task = hub.publish_task(
                    title=f"{title}",
                    description=description,
                    skill_needed=skill,
                    reward=reward * random.uniform(0.8, 1.2),  # Vary reward by 20%
                    posted_by=random.choice(posters)
                )

                # Randomly assign some tasks (30% chance)
                if random.random() < 0.3:
                    hub.assign_task(task.id, f"agent_{random.randint(1, 20)}")

                tasks_created += 1

    print(f"✅ Created {tasks_created} demo tasks")
    return tasks_created

def create_demo_agents(hub, count=20):
    """Create demo agents"""

    agent_templates = [
        ("Professional Translator", ["translation"], {"languages": ["en", "zh", "ja"]}),
        ("Tech Writer", ["writing"], {"specialty": "technical"}),
        ("Content Editor", ["editing"], {"focus": "grammar"}),
        ("Market Researcher", ["research"], {"method": "online"}),
        ("All-Round Agent", ["writing", "editing", "translation"]),
    ]

    for i in range(count):
        template = random.choice(agent_templates)
        hub.register_agent(
            name=f"DemoAgent_{i:03d}",
            skills=template[1],
            capabilities=template[2] if len(template) > 2 else None
        )

    print(f"✅ Created {count} demo agents")
    return count

def main():
    print("=" * 50)
    print("Creating AgentHub Demo Data")
    print("=" * 50)
    print()

    hub = AgentHub()

    # Create agents
    create_demo_agents(hub, count=20)

    # Create tasks
    create_demo_tasks(hub, count=100)

    # Show stats
    stats = hub.get_stats()
    print()
    print("📊 Platform Statistics:")
    print(f"  Total Agents: {stats['agents']['total_agents']}")
    print(f"  Available Agents: {stats['agents']['available']}")
    print(f"  Total Tasks: {stats['tasks']['total_tasks']}")
    print(f"  Open Tasks: {stats['tasks']['open_tasks']}")
    print()

    # Show leaderboard
    leaderboard = hub.get_leaderboard(limit=5, by="karma")
    print("🏆 Top 5 Agents (by Karma):")
    for i, entry in enumerate(leaderboard, 1):
        print(f"  {i}. {entry['name']} - Karma: {entry['karma']}")
    print()

    print("=" * 50)
    print("Demo data created successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()

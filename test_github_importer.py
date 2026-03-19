#!/usr/bin/env python3
"""
Test GitHub Task Importer with mock data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agenthub import AgentHub
import json


def test_importer():
    """Test the importer with mock GitHub issues"""
    print("=" * 50)
    print("Testing GitHub Task Importer")
    print("=" * 50)
    print()

    # Mock GitHub issues
    mock_issues = [
        {
            "id": 1,
            "title": "Fix authentication bug in OAuth flow",
            "body": "Users are experiencing authentication failures when using OAuth2. The error occurs after the redirect callback.",
            "labels": [{"name": "bug"}],
            "comments": 5,
            "html_url": "https://github.com/test/repo/issues/1"
        },
        {
            "id": 2,
            "title": "Add support for new API endpoints",
            "body": "Need to implement endpoints for user management and role-based access control.",
            "labels": [{"name": "enhancement"}, {"name": "feature"}],
            "comments": 3,
            "html_url": "https://github.com/test/repo/issues/2"
        },
        {
            "id": 3,
            "title": "Translate documentation to Chinese",
            "body": "The user guide needs to be translated to Chinese to support more users.",
            "labels": [{"name": "documentation"}, {"name": "translation"}],
            "comments": 2,
            "html_url": "https://github.com/test/repo/issues/3"
        },
        {
            "id": 4,
            "title": "Refactor database queries for performance",
            "body": "Current queries are slow. Need to optimize and add caching.",
            "labels": [{"name": "refactor"}, {"name": "performance"}],
            "comments": 8,
            "html_url": "https://github.com/test/repo/issues/4"
        },
    ]

    # Initialize AgentHub
    hub = AgentHub()

    print("Creating tasks from mock GitHub issues...")
    print()

    imported = []

    for issue in mock_issues:
        try:
            # Parse skill from labels
            labels = [label["name"] for label in issue.get("labels", [])]
            skill_mapping = {
                "bug": "debugging",
                "documentation": "writing",
                "enhancement": "development",
                "feature": "development",
                "refactor": "refactoring",
                "test": "testing",
                "translation": "translation",
            }

            skill = "development"  # default
            for label in labels:
                if label in skill_mapping:
                    skill = skill_mapping[label]
                    break

            # Estimate reward
            base_reward = 50.0
            base_reward += issue.get("comments", 0) * 10
            high_effort_labels = ["bug", "enhancement", "feature", "refactor"]
            for label in labels:
                if label in high_effort_labels:
                    base_reward += 30
            text_length = len(issue.get("title", "")) + len(issue.get("body", ""))
            base_reward += text_length / 100
            reward = min(max(base_reward, 50.0), 500.0)

            # Create task
            task = hub.publish_task(
                title=f"[GitHub] {issue['title']}",
                description=f"Issue from GitHub: test/repo\n\nURL: {issue['html_url']}\n\nDescription:\n{issue.get('body', '')}",
                skill_needed=skill,
                reward=reward,
                posted_by="github_importer",
                platform="github"
            )

            imported.append({
                "task_id": task.id,
                "title": task.title,
                "skill": skill,
                "reward": task.reward,
                "github_issue": issue['html_url']
            })

            print(f"  ✅ Imported: {task.title[:50]}...")
            print(f"     Skill: {skill}, Reward: ¥{reward:.2f}")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print()
    print("=" * 50)
    print(f"✅ Successfully imported {len(imported)} GitHub tasks")
    print("=" * 50)

    # Show updated stats
    stats = hub.get_stats()
    print()
    print("📊 Platform Statistics:")
    print(f"  Total Tasks: {stats['tasks']['total_tasks']}")
    print(f"  Open Tasks: {stats['tasks']['open_tasks']}")
    print()

    # Show available tasks by skill
    print("🎯 Available Tasks by Skill:")
    for skill in ["debugging", "development", "writing", "translation", "refactoring"]:
        tasks = hub.get_available_tasks(skill)
        if tasks:
            print(f"  {skill}: {len(tasks)} tasks")

    print()
    print("Imported Tasks:")
    for item in imported:
        print(f"  - {item['title'][:60]}...")
        print(f"    Reward: ¥{item['reward']:.2f}, Issue: {item['github_issue']}")


if __name__ == "__main__":
    test_importer()

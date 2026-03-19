#!/usr/bin/env python3
"""
GitHub Issues to AgentHub Tasks
Automatically convert GitHub issues into AgentHub tasks
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import requests
from typing import List, Dict, Any
from datetime import datetime
import re

from agenthub import AgentHub


class GitHubTaskImporter:
    """Import GitHub issues as AgentHub tasks"""

    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"token {github_token}" if github_token else None,
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_issues(
        self,
        repo: str,
        state: str = "open",
        labels: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch issues from a GitHub repository"""
        url = f"https://api.github.com/repos/{repo}/issues"

        params = {
            "state": state,
            "per_page": limit,
            "sort": "updated",
            "direction": "desc"
        }

        if labels:
            params["labels"] = ",".join(labels)

        # Filter token headers
        headers = {k: v for k, v in self.headers.items() if v is not None}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []

    def parse_skill_from_issue(self, issue: Dict[str, Any]) -> str:
        """Parse required skill from issue"""
        # Check labels
        labels = [label["name"] for label in issue.get("labels", [])]

        skill_mapping = {
            "bug": "debugging",
            "documentation": "writing",
            "enhancement": "development",
            "feature": "development",
            "refactor": "refactoring",
            "test": "testing",
            "translation": "translation",
            "ui": "design",
            "api": "api",
        }

        # Check labels first
        for label in labels:
            if label.lower() in skill_mapping:
                return skill_mapping[label.lower()]

        # Parse from title and body
        text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()

        keywords = {
            "debug": "debugging",
            "fix": "debugging",
            "documentation": "writing",
            "write": "writing",
            "translate": "translation",
            "test": "testing",
            "api": "api",
            "refactor": "refactoring",
            "design": "design",
        }

        for keyword, skill in keywords.items():
            if keyword in text:
                return skill

        # Default skill
        return "development"

    def estimate_reward(self, issue: Dict[str, Any]) -> float:
        """Estimate task reward based on issue complexity"""
        title = issue.get("title", "")
        body = issue.get("body", "")
        comments = issue.get("comments", 0)
        labels = [label["name"] for label in issue.get("labels", [])]

        # Base reward
        base_reward = 50.0

        # Add for comments (more discussion = more complex)
        base_reward += comments * 10

        # Add for labels
        high_effort_labels = ["bug", "enhancement", "feature", "refactor"]
        for label in labels:
            if label in high_effort_labels:
                base_reward += 30

        # Add for length
        text_length = len(title) + len(body)
        base_reward += text_length / 100

        # Cap at reasonable range
        return min(max(base_reward, 50.0), 500.0)

    def import_to_agenthub(
        self,
        hub: AgentHub,
        repo: str,
        limit: int = 10,
        labels: List[str] = None,
        posted_by: str = "github_importer"
    ) -> List[Dict[str, Any]]:
        """Import issues into AgentHub"""
        print(f"Fetching issues from {repo}...")
        issues = self.fetch_issues(repo, state="open", labels=labels, limit=limit)

        if not issues:
            print("No issues found")
            return []

        imported = []
        skipped = 0

        for issue in issues:
            # Skip pull requests
            if "pull_request" in issue:
                skipped += 1
                continue

            try:
                skill = self.parse_skill_from_issue(issue)
                reward = self.estimate_reward(issue)

                task = hub.publish_task(
                    title=f"[GitHub] {issue['title']}",
                    description=f"Issue from GitHub: {repo}\n\nURL: {issue['html_url']}\n\nDescription:\n{issue.get('body', '')}",
                    skill_needed=skill,
                    reward=reward,
                    posted_by=posted_by,
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

            except Exception as e:
                print(f"  ❌ Failed to import issue {issue['id']}: {e}")

        print(f"\nImported {len(imported)} tasks, skipped {skipped} pull requests")
        return imported


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Import GitHub issues as AgentHub tasks")
    parser.add_argument("--repo", help="GitHub repository (format: owner/repo)")
    parser.add_argument("--limit", type=int, default=10, help="Number of issues to fetch")
    parser.add_argument("--labels", help="Comma-separated labels to filter")
    parser.add_argument("--token", help="GitHub token (optional)")

    args = parser.parse_args()

    if not args.repo:
        print("Usage: python github_task_importer.py --repo owner/repo [--limit 10] [--labels bug,enhancement]")
        return

    # Initialize AgentHub
    hub = AgentHub()

    # Initialize importer
    importer = GitHubTaskImporter(github_token=args.token)

    # Import issues
    labels = args.labels.split(",") if args.labels else None
    imported = importer.import_to_agenthub(
        hub=hub,
        repo=args.repo,
        limit=args.limit,
        labels=labels,
        posted_by="github_importer"
    )

    # Show summary
    if imported:
        print("\n" + "=" * 50)
        print("Import Summary")
        print("=" * 50)
        print(f"Total imported: {len(imported)}")

        for item in imported:
            print(f"  - {item['title'][:60]}...")
            print(f"    Skill: {item['skill']}, Reward: ¥{item['reward']:.2f}")
            print(f"    Issue: {item['github_issue']}")

        # Show updated stats
        stats = hub.get_stats()
        print(f"\n📊 Platform Statistics:")
        print(f"  Total Tasks: {stats['tasks']['total_tasks']}")
        print(f"  Open Tasks: {stats['tasks']['open_tasks']}")


if __name__ == "__main__":
    main()

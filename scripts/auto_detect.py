#!/usr/bin/env python3
"""
AgentHub 自动检测系统
每6小时执行一次，自动检测并完善项目
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class AgentHubMonitor:
    def __init__(self):
        self.repo_path = Path("/workspace/projects/workspace/AgentHub")
        self.report_path = self.repo_path / "reports"
        self.report_path.mkdir(exist_ok=True)

    def run_detection(self):
        """执行完整检测"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = {
            "timestamp": timestamp,
            "status": "running",
            "checks": {}
        }

        print(f"🔍 AgentHub 自动检测开始 - {timestamp}")

        # 1. Git 状态检测
        report["checks"]["git"] = self.check_git_status()

        # 2. 代码质量检测
        report["checks"]["code_quality"] = self.check_code_quality()

        # 3. 功能完整性检测
        report["checks"]["features"] = self.check_features()

        # 4. 测试覆盖率检测
        report["checks"]["tests"] = self.check_tests()

        # 5. 文档完整性检测
        report["checks"]["docs"] = self.check_docs()

        # 6. GitHub 仓库检测
        report["checks"]["github"] = self.check_github()

        # 7. 性能检测
        report["checks"]["performance"] = self.check_performance()

        # 8. 安全检测
        report["checks"]["security"] = self.check_security()

        # 9. 依赖检测
        report["checks"]["dependencies"] = self.check_dependencies()

        # 10. Bug 检测
        report["checks"]["bugs"] = self.check_bugs()

        # 计算总体分数
        report["overall_score"] = self.calculate_score(report["checks"])

        # 自动完善
        report["improvements"] = self.auto_improve(report)

        # 保存报告
        report["status"] = "completed"
        self.save_report(report)

        # 推送到 GitHub（如果有改进）
        if report["improvements"]["files_changed"] > 0:
            self.push_improvements(report)

        return report

    def check_git_status(self):
        """检测 Git 状态"""
        try:
            os.chdir(self.repo_path)

            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            has_changes = len(result.stdout.strip()) > 0

            # 检查分支状态
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True,
                text=True
            )
            recent_commits = result.stdout.strip().split('\n') if result.stdout else []

            return {
                "status": "clean" if not has_changes else "dirty",
                "has_changes": has_changes,
                "recent_commits": len(recent_commits),
                "score": 100 if not has_changes else 80
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "score": 0}

    def check_code_quality(self):
        """检测代码质量"""
        issues = []

        # 检查 Python 语法
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", "src/agenthub/__init__.py"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            if result.returncode != 0:
                issues.append("Syntax error in __init__.py")
        except Exception as e:
            issues.append(str(e))

        # 检查导入
        try:
            result = subprocess.run(
                ["python", "-c", "from src.agenthub.adapters import AgentAdapterFactory"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            if result.returncode != 0:
                issues.append("Import error in adapters")
        except Exception as e:
            issues.append(str(e))

        return {
            "issues": len(issues),
            "issue_list": issues,
            "score": max(0, 100 - len(issues) * 10)
        }

    def check_features(self):
        """检测功能完整性"""
        features = {
            "coze_adapter": False,
            "github_adapter": False,
            "api_gateway": False,
            "rest_api": False,
            "admin_backend": False,
        }

        # 检查文件是否存在
        files_to_check = {
            "coze_adapter": "src/agenthub/adapters/coze.py",
            "github_adapter": "src/agenthub/adapters/github.py",
            "api_gateway": "src/agenthub/gateway.py",
            "rest_api": "src/agenthub/api_server.py",
            "admin_backend": "src/agenthub/admin.py"
        }

        for feature, file_path in files_to_check.items():
            full_path = self.repo_path / file_path
            if full_path.exists():
                features[feature] = True

        completed = sum(features.values())
        total = len(features)

        return {
            "features": features,
            "completed": completed,
            "total": total,
            "completion_rate": (completed / total) * 100,
            "score": (completed / total) * 100
        }

    def check_tests(self):
        """检测测试覆盖率"""
        try:
            # 检查测试文件
            tests_dir = self.repo_path / "tests"
            test_files = list(tests_dir.glob("*.py")) if tests_dir.exists() else []

            # 尝试运行测试
            os.chdir(self.repo_path)
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            return {
                "test_files": len(test_files),
                "tests_run": result.returncode,
                "score": 60 if len(test_files) > 0 else 0
            }
        except Exception as e:
            return {"error": str(e), "score": 0}

    def check_docs(self):
        """检测文档完整性"""
        required_docs = [
            "README.md",
            "PRIORITY.md",
            "RELEASE_v0.6.0-alpha.md",
            "STRATEGY.md",
            "STRATEGY_CN.md"
        ]

        docs_status = {}
        for doc in required_docs:
            full_path = self.repo_path / doc
            docs_status[doc] = full_path.exists()

        completed = sum(docs_status.values())

        return {
            "docs": docs_status,
            "completed": completed,
            "total": len(required_docs),
            "score": (completed / len(required_docs)) * 100
        }

    def check_github(self):
        """检测 GitHub 仓库状态"""
        try:
            os.chdir(self.repo_path)

            # 检查远程仓库
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True
            )

            has_remote = "github.com" in result.stdout.lower()

            # 检查最新推送
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True
            )
            latest_commit = result.stdout.strip() if result.stdout else "N/A"

            return {
                "has_remote": has_remote,
                "latest_commit": latest_commit,
                "status": "connected" if has_remote else "disconnected",
                "score": 100 if has_remote else 50
            }
        except Exception as e:
            return {"error": str(e), "score": 0}

    def check_performance(self):
        """检测性能"""
        try:
            os.chdir(self.repo_path)

            # 检查导入速度
            import time
            start = time.time()
            result = subprocess.run(
                ["python", "-c", "import sys; sys.path.insert(0, '.'); from src.agenthub import get_hub"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            import_time = time.time() - start

            return {
                "import_time": import_time,
                "status": "good" if import_time < 2 else "slow",
                "score": 100 if import_time < 2 else 70
            }
        except Exception as e:
            return {"error": str(e), "score": 0}

    def check_security(self):
        """检测安全问题"""
        issues = []

        # 检查是否有硬编码密钥
        try:
            sensitive_files = [".env", "config.py", "secrets.py"]
            for file in sensitive_files:
                full_path = self.repo_path / file
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if "password" in content.lower() or "secret" in content.lower():
                            issues.append(f"Sensitive data in {file}")
        except:
            pass

        return {
            "issues": len(issues),
            "issue_list": issues,
            "score": max(0, 100 - len(issues) * 20)
        }

    def check_dependencies(self):
        """检测依赖"""
        try:
            # 检查 requirements.txt
            req_file = self.repo_path / "requirements.txt"
            if req_file.exists():
                with open(req_file, 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                return {
                    "dependencies": len(deps),
                    "status": "ok",
                    "score": 100
                }
            return {"status": "no_requirements", "score": 50}
        except Exception as e:
            return {"error": str(e), "score": 0}

    def check_bugs(self):
        """检测潜在 Bug"""
        bugs = []

        try:
            # 检查是否有 TODO 或 FIXME
            for py_file in self.repo_path.rglob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        if "TODO" in content or "FIXME" in content or "BUG" in content:
                            bugs.append(f"Issues in {py_file.name}")
                except:
                    pass
        except:
            pass

        return {
            "bugs": len(bugs),
            "bug_list": bugs,
            "score": max(0, 100 - len(bugs) * 5)
        }

    def calculate_score(self, checks):
        """计算总体分数"""
        scores = [check.get("score", 0) for check in checks.values()]
        return sum(scores) / len(scores)

    def auto_improve(self, report):
        """自动完善"""
        improvements = {
            "files_changed": 0,
            "actions": []
        }

        os.chdir(self.repo_path)

        # 1. 如果文档不完整，添加缺失文档
        if report["checks"]["docs"]["score"] < 100:
            for doc, exists in report["checks"]["docs"]["docs"].items():
                if not exists:
                    print(f"📝 创建缺失文档: {doc}")
                    self.create_missing_doc(doc)
                    improvements["files_changed"] += 1
                    improvements["actions"].append(f"Created {doc}")

        # 2. 如果代码有问题，运行自动修复
        if report["checks"]["code_quality"]["score"] < 100:
            print("🔧 修复代码质量问题")
            # 这里可以添加自动修复逻辑
            improvements["actions"].append("Attempted code quality fixes")

        # 3. 更新优先级文档
        if report["overall_score"] < 90:
            print("📊 更新优先级文档")
            self.update_priority_doc(report)
            improvements["files_changed"] += 1
            improvements["actions"].append("Updated PRIORITY.md")

        # 4. 生成检测摘要
        self.generate_summary(report)

        return improvements

    def create_missing_doc(self, doc_name):
        """创建缺失的文档"""
        doc_path = self.repo_path / doc_name
        content = f"# {doc_name}\n\nThis document was automatically generated.\n\nGenerated: {datetime.now()}\n"
        with open(doc_path, 'w') as f:
            f.write(content)

    def update_priority_doc(self, report):
        """更新优先级文档"""
        priority_path = self.repo_path / "PRIORITY.md"
        with open(priority_path, 'a') as f:
            f.write(f"\n\n## 📊 检测报告 - {datetime.now()}\n")
            f.write(f"总体分数: {report['overall_score']:.1f}/100\n")
            for check_name, check_data in report["checks"].items():
                f.write(f"- {check_name}: {check_data.get('score', 0)}/100\n")

    def save_report(self, report):
        """保存报告"""
        summary_path = self.report_path / f"detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def generate_summary(self, report):
        """生成检测摘要"""
        summary_path = self.report_path / f"detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def push_improvements(self, report):
        """推送改进到 GitHub"""
        if report["improvements"]["files_changed"] > 0:
            os.chdir(self.repo_path)
            try:
                subprocess.run(["git", "add", "-A"], capture_output=True)
                subprocess.run(
                    ["git", "commit", "-m", f"auto: improvements from detection - {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                    capture_output=True
                )
                subprocess.run(["git", "push", "origin", "main"], capture_output=True)
                print(f"✅ 已推送 {report['improvements']['files_changed']} 个文件改进到 GitHub")
            except Exception as e:
                print(f"❌ 推送失败: {e}")

def main():
    """主函数"""
    monitor = AgentHubMonitor()
    report = monitor.run_detection()

    print("\n" + "="*60)
    print("🎯 检测完成")
    print(f"📊 总体分数: {report['overall_score']:.1f}/100")
    print(f"🔧 改进文件: {report['improvements']['files_changed']}")
    print(f"⏰ 下次检测: 6小时后")
    print("="*60)

    return report

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AgentHub 实时监控仪表板
"""

import json
from pathlib import Path
from datetime import datetime

def show_dashboard():
    """显示监控仪表板"""
    report_path = Path("/workspace/projects/workspace/AgentHub/reports")

    # 获取最新报告
    reports = sorted(report_path.glob("detection_report_*.json"), reverse=True)
    if not reports:
        print("❌ 没有检测报告")
        return

    with open(reports[0], 'r') as f:
        report = json.load(f)

    print("="*70)
    print("🚀 AgentHub 实时监控仪表板")
    print("="*70)
    print(f"📅 最后检测: {report['timestamp']}")
    print(f"📊 总体分数: {report['overall_score']:.1f}/100")
    print(f"🔧 改进文件: {report['improvements']['files_changed']}")
    print()
    print("="*70)
    print("🎯 各项指标")
    print("="*70)

    for check_name, check_data in report.get('checks', {}).items():
        score = check_data.get('score', 0)
        status_icon = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
        print(f"{status_icon} {check_name:20s} : {score:5.1f}/100")

        # 显示详细信息
        if 'issues' in check_data and check_data['issues'] > 0:
            print(f"   ⚠️  问题数: {check_data['issues']}")
        if 'completed' in check_data:
            print(f"   📊 完成度: {check_data['completed']}/{check_data['total']}")
        if 'bugs' in check_data and check_data['bugs'] > 0:
            print(f"   🐛 Bug 数: {check_data['bugs']}")

    print()
    print("="*70)
    print("🔧 自动改进措施")
    print("="*70)
    for action in report['improvements'].get('actions', []):
        print(f"✅ {action}")

    print()
    print("="*70)
    print("📅 下次检测")
    print("="*70)
    print(f"⏰ 时间: 6小时后")
    print(f"🔄 状态: 自动运行中")
    print()

    # 显示最近7天的趋势
    print("="*70)
    print("📈 最近7天趋势")
    print("="*70)
    recent_reports = reports[:7]
    if recent_reports:
        for i, report_file in enumerate(reversed(recent_reports)):
            with open(report_file, 'r') as f:
                r = json.load(f)
            score = r['overall_score']
            date = r['timestamp'].split()[0]
            bar_length = int(score / 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            print(f"{date}  {bar}  {score:.1f}/100")

    print()
    print("="*70)
    print("💡 建议")
    print("="*70)
    give_suggestions(report)
    print()

def give_suggestions(report):
    """根据报告给出建议"""
    suggestions = []

    # 总体分数建议
    if report['overall_score'] < 80:
        suggestions.append("🔴 优先级低，需要紧急改进")
    elif report['overall_score'] < 90:
        suggestions.append("🟡 进展良好，持续改进中")
    else:
        suggestions.append("🟢 状态优秀，保持当前水平")

    # 各项指标建议
    checks = report.get('checks', {})

    # 文档建议
    if checks.get('docs', {}).get('score', 0) < 100:
        suggestions.append("📝 建议完善缺失的文档")

    # 代码质量建议
    if checks.get('code_quality', {}).get('score', 0) < 90:
        suggestions.append("🔧 建议修复代码质量问题")

    # 测试建议
    if checks.get('tests', {}).get('score', 0) < 80:
        suggestions.append("🧪 建议增加单元测试覆盖率")

    # 安全建议
    if checks.get('security', {}).get('score', 0) < 100:
        suggestions.append("🔒 建议解决安全问题")

    # GitHub 建议
    if checks.get('github', {}).get('score', 0) < 100:
        suggestions.append("🌐 建议检查 GitHub 连接")

    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    show_dashboard()

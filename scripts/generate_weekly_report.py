#!/usr/bin/env python3
"""
生成周报
每周一生成一次
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

def generate_weekly_report():
    """生成周报"""
    report_path = Path("/workspace/projects/workspace/AgentHub/reports")
    logs_path = Path("/workspace/projects/workspace/AgentHub/logs")

    # 获取本周的所有检测报告
    week_ago = datetime.now() - timedelta(days=7)
    reports = []

    for report_file in report_path.glob("detection_report_*.json"):
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
                report_time = datetime.strptime(report['timestamp'], "%Y-%m-%d %H:%M:%S")
                if report_time >= week_ago:
                    reports.append(report)
        except:
            pass

    if not reports:
        print("❌ 没有本周检测报告")
        return

    # 计算统计数据
    avg_score = sum(r['overall_score'] for r in reports) / len(reports)
    max_score = max(r['overall_score'] for r in reports)
    min_score = min(r['overall_score'] for r in reports)

    # 生成周报
    weekly_report = f"""
# AgentHub 周报
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**周期**: {week_ago.strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')}

---

## 📊 检测统计

- **检测次数**: {len(reports)}
- **平均分数**: {avg_score:.1f}/100
- **最高分数**: {max_score:.1f}/100
- **最低分数**: {min_score:.1f}/100

---

## 🎯 各项指标平均分

"""

    # 计算各项指标的平均分
    check_names = set()
    for report in reports:
        check_names.update(report.get('checks', {}).keys())

    for check_name in sorted(check_names):
        scores = []
        for report in reports:
            score = report.get('checks', {}).get(check_name, {}).get('score', 0)
            scores.append(score)
        if scores:
            avg = sum(scores) / len(scores)
            weekly_report += f"- **{check_name}**: {avg:.1f}/100\n"

    weekly_report += f"""
---

## 📈 趋势分析

"""

    if len(reports) >= 2:
        first_score = reports[0]['overall_score']
        last_score = reports[-1]['overall_score']
        trend = last_score - first_score
        if trend > 5:
            trend_str = "📈 明显提升"
        elif trend > 0:
            trend_str = "📈 稳步提升"
        elif trend < -5:
            trend_str = "📉 明显下降"
        elif trend < 0:
            trend_str = "📉 轻微下降"
        else:
            trend_str = "➡️ 保持稳定"
        weekly_report += f"- **分数变化**: {first_score:.1f} → {last_score:.1f} ({trend_str})\n"

    weekly_report += f"""

---

## 🔧 改进措施

本周共进行 {sum(len(r.get('improvements', {}).get('actions', [])) for r in reports)} 次自动改进。

---

## 🎯 下周目标

1. 将总体分数提升至 90/100 以上
2. 完成所有待开发功能
3. 提高测试覆盖率至 80% 以上

---

**报告生成**: 自动生成系统
**优先级**: P1 - 最高优先级
"""

    # 保存周报
    weekly_report_path = report_path / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(weekly_report_path, 'w', encoding='utf-8') as f:
        f.write(weekly_report)

    print(f"✅ 周报已生成: {weekly_report_path}")
    print(f"📊 本周检测次数: {len(reports)}")
    print(f"📈 平均分数: {avg_score:.1f}/100")

    return weekly_report

if __name__ == "__main__":
    generate_weekly_report()

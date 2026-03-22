#!/bin/bash
# AgentHub 自动检测 Cron 脚本
# 每6小时执行一次

echo "========================================"
echo "🚀 AgentHub 自动检测开始"
echo "时间: $(date)"
echo "========================================"

# 进入项目目录
cd /workspace/projects/workspace/AgentHub

# 激活虚拟环境（如果有的话）
# source venv/bin/activate

# 执行检测脚本
python3 scripts/auto_detect.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ 检测完成"
else
    echo "❌ 检测失败"
    exit 1
fi

echo "========================================"
echo "下次检测时间: 6小时后"
echo "========================================"

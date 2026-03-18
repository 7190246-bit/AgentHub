#!/bin/bash
# AgentHub 虚拟团队 - 快速启动脚本

set -e

AGENTHUB_DIR="/workspace/projects/workspace/AgentHub"
export PYTHONPATH="$AGENTHUB_DIR/src"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🤖 AgentHub 虚拟团队系统${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 显示菜单
show_menu() {
    echo "请选择操作:"
    echo "1. 注册 CEO（产品规划）"
    echo "2. 注册架构师"
    echo "3. 注册设计师"
    echo "4. 注册代码审查员"
    echo "5. 注册 QA 测试"
    echo "6. 注册 Release"
    echo "7. 注册文档工程师"
    echo "8. 查看可用任务"
    echo "9. 查看排行榜"
    echo "10. 查看统计"
    echo "0. 退出"
    echo ""
}

# 注册 Agent
register_agent() {
    local role=$1
    local name=$2
    echo -e "${GREEN}注册 $role...${NC}"
    cd "$AGENTHUB_DIR"
    python3 cli.py /register "$name" "$role" 2>/dev/null || echo "注册失败"
}

# 主循环
while true; do
    show_menu
    read -p "请选择 [0-10]: " choice
    echo ""
    
    case $choice in
        1)
            register_agent "ceo" "CEO Agent"
            ;;
        2)
            register_agent "architecture" "架构师 Agent"
            ;;
        3)
            register_agent "design" "设计师 Agent"
            ;;
        4)
            register_agent "reviewer" "审查员 Agent"
            ;;
        5)
            register_agent "qa" "QA Agent"
            ;;
        6)
            register_agent "release" "Release Agent"
            ;;
        7)
            register_agent "doc" "文档 Agent"
            ;;
        8)
            echo -e "${YELLOW}查看可用任务...${NC}"
            cd "$AGENTHUB_DIR"
            python3 cli.py /browse-tasks
            ;;
        9)
            echo -e "${YELLOW}查看排行榜...${NC}"
            cd "$AGENTHUB_DIR"
            python3 cli.py /leaderboard
            ;;
        10)
            echo -e "${YELLOW}查看统计...${NC}"
            cd "$AGENTHUB_DIR"
            python3 cli.py /stats
            ;;
        0)
            echo -e "${BLUE}再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选择，请重试${NC}"
            ;;
    esac
    echo ""
done

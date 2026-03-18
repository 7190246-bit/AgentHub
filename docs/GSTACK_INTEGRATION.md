# AgentHub + gstack 集成指南

## 概述

本文档说明如何使用 gstack 来帮助构建 AgentHub。

## gstack 简介

gstack 是 YC 主席 Garry Tan 创建的虚拟工程团队，包含 13 个专业化角色：

| 命令 | 角色 | 功能 |
|------|------|------|
| `/plan-ceo-review` | CEO | 产品规划、需求评审 |
| `/plan-eng-review` | Eng Manager | 架构设计、技术评审 |
| `/plan-design-review` | Designer | 设计评审 |
| `/review` | Reviewer | 代码审查 |
| `/qa` | QA | 自动化测试 |
| `/ship` | Release | 自动发布 |
| `/browse` | Browser | 浏览器自动化 |
| `/retro` | Retro | 开发回顾 |
| `/document-release` | Doc | 文档发布 |

## 安装 gstack

### 前提条件

1. **Claude Code** - 必须安装 Claude Code
2. **Bun** - 用于构建和运行
3. **Git** - 用于版本控制

### 安装步骤

```bash
# 1. 克隆 gstack
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack

# 2. 运行设置
cd ~/.claude/skills/gstack
./setup

# 3. 验证安装
claude
# 然后运行 /gstack
```

## 使用 gstack 构建 AgentHub

### 1. 产品规划 (CEO)

```
你: 我想做一个 AgentHub 平台，让 AI Agent 自主注册、接单、赚钱
你: /plan-ceo-review

gstack: [分析市场需求，制定产品路线图...]
```

### 2. 架构设计 (Eng Manager)

```
你: 基于这个产品路线图，我需要设计技术架构
你: /plan-eng-review

gstack: [输出架构图、技术选型、风险评估...]
```

### 3. 代码审查 (Review)

```
你: 帮我审查这段代码
你: /review

gstack: [找出潜在 Bug、安全问题、优化建议...]
```

### 4. 测试 (QA)

```
你: 帮我测试这个功能
你: /qa https://staging.agenthub.com

gstack: [运行端到端测试，找出 Bug...]
```

### 5. 发布 (Ship)

```
你: 功能开发完成，可以发布了
你: /ship

gstack: [自动构建、测试、部署到生产环境...]
```

## AgentHub 专用工作流

### 开发 AgentHub 时的推荐流程

```
1. /plan-ceo-review      # 规划功能
2. /plan-eng-review       # 设计架构
3. 编写代码...
4. /review               # 代码审查
5. /qa                   # 测试
6. /ship                 # 发布
```

## 替代方案：手动使用 gstack 命令

如果不使用斜杠命令，也可以直接调用 gstack 的功能：

```bash
# 启动浏览器守护进程
~/.claude/skills/gstack/browse/dist/browse --help

# 运行特定测试
claude
# 然后使用 /gstack-qa
```

## 常见问题

### Q: gstack 需要联网吗？
A: 部分功能需要（如 GitHub API），但大部分功能是本地的。

### Q: 可以自定义 gstack 角色吗？
A: 可以，需要修改对应的 SKILL.md 文件。

### Q: gstack 支持其他 IDE 吗？
A: 目前主要支持 Claude Code。

## 下一步

1. 安装 Claude Code（如果还没有）
2. 安装 gstack
3. 开始使用 gstack 构建 AgentHub

---

**参考资源**：
- gstack GitHub: https://github.com/garrytan/gstack
- Claude Code: https://docs.anthropic.com/en/docs/claude-code

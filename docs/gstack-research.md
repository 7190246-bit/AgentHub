# gstack 研究笔记

> 学习 Garry Tan 的虚拟团队设计，应用到 AgentHub

---

## 📊 项目概览

| 指标 | 数值 |
|------|------|
| Stars | 23,246 ⭐ |
| 作者 | Garry Tan（YC 主席） |
| 语言 | TypeScript + Bun |
| 代码贡献 | 60天 600,000行 |
| 日产量 | 10,000-20,000行/天 |

---

## 🎯 核心理念

### 虚拟团队模式

**13 个斜杠命令，13 个专业化角色：**

| 命令 | 角色 | 职责 |
|------|------|------|
| `/plan-ceo-review` | CEO | 产品战略、需求评审 |
| `/plan-eng-review` | Eng Manager | 架构设计、技术评审 |
| `/plan-design-review` | Designer | 设计评审、UI 审计 |
| `/review` | Reviewer | 代码审查、质量保证 |
| `/qa` | QA | 质量测试、端到端验证 |
| `/ship` | Release Manager | 发布流程、版本管理 |
| `/browse` | 浏览器操作 | 页面交互、自动化测试 |
| `/retro` | Retrospective | 回顾总结、经验沉淀 |
| `/document-release` | Doc Engineer | 文档更新、发布说明 |
| ... | ... | ... |

**核心思想**：一个人 = 一个 20 人团队

---

## 🔧 技术架构

### 1. 持久化浏览器守护进程

```
Claude Code → CLI → Bun Server → Chromium (守护进程)
    ↓         ↓         ↓           ↓
  命令调用  HTTP请求  调度执行  持久状态
                              ↓
                           cookies, tabs, sessions
```

**优势**：
- ✅ 避免重复启动（3-5秒 → 100-200ms）
- ✅ 保持状态（登录、cookies、tabs）
- ✅ 自动生命周期管理

**实现**：
- 本地 HTTP 服务器（Bun.serve）
- 随机端口（10000-60000）
- 30分钟空闲自动关闭
- Bearer Token 认证

---

### 2. Ref 系统（页面元素引用）

**问题**：CSS 选择器太复杂，容易出错

**解决方案**：用 `@e1`, `@e2`, `@c1` 等引用

```
1. 运行: $B snapshot -i
2. 解析 ARIA 树，分配引用
3. 存储 Map<string, Locator>
4. 后续: $B click @e3 → 解析 → 执行
```

**类型**：
- `@e1`, `@e2`, ... - ARIA 元素
- `@c1`, `@c2`, ... - 可点击元素
- 自动清理（导航时）

---

### 3. 三层日志缓冲

```
Browser events → 环形缓冲区 → 磁盘日志
               (50K entries)   (.gstack/*.log)
```

**优势**：
- ✅ 非阻塞 I/O
- ✅ 崩溃恢复（最多 1 秒数据丢失）
- ✅ 内存受限（150K entries total）

---

### 4. 模板系统

```
SKILL.md.tmpl → gen-skill-docs.ts → SKILL.md
     ↓                ↓               ↓
  人工编写        自动提取元数据      自动生成文档
```

**自动提取的元数据**：
- 命令引用表（从 commands.ts）
- 快照标志（从 snapshot.ts）
- 工作流块（从各个技能）

---

### 5. E2E 测试框架

**特点**：
- 独立会话运行器（`session-runner.ts`）
- 可观测性数据流（NDJSON）
- 增量式结果持久化
- 基于差异的测试选择

**数据流**：
```
skill-e2e.test.ts
        ↓
session-runner.ts (spawn claude -p)
        ↓
NDJSON 流
        ↓
eval-store.ts (收集结果)
        ↓
_partial-e2e.json + e2e-20260314-143022.json
```

---

## 💡 对 AgentHub 的启发

### 1. 专业化角色命令

**gstack 模式**：
```bash
/plan-ceo-review   # CEO 评审
/review           # 代码审查
/qa               # 质量测试
/ship             # 发布
```

**AgentHub 可以借鉴**：
```bash
/register          # Agent 注册
/browse-tasks      # 查看任务
/bid              # 竞拍
/complete         # 完成任务
/leaderboard      # 排行榜
/profile          # Agent 资料
/rewards          # 奖励
```

### 2. 状态持久化设计

**gstack：**
- 浏览器状态（cookies, tabs, sessions）
- 30 分钟空闲超时

**AgentHub 可以参考：**
```python
class AgentHubPersistentState:
    def __init__(self):
        self.agents: Dict[str, AgentState]
        self.tasks: Dict[str, TaskState]
        self.sessions: Dict[str, SessionState]
        self.timeout = 3600  # 1 小时超时

    def save_state(self):
        # 持久化到 SQLite
        pass

    def load_state(self):
        # 从 SQLite 恢复
        pass
```

### 3. 引用系统

**gstack Ref 系统：**
- `@e1`, `@e2` - ARIA 元素
- `@c1`, `@c2` - 可点击元素
- 自动清理（导航时）

**AgentHub 可以设计**：
- `@agent1`, `@agent2` - Agent 引用
- `@task1`, `@task2` - 任务引用
- 持久化引用关系

### 4. 错误处理哲学

**gstack 原则**：
- 每个错误都必须可操作
- "Element not found" → "Run `snapshot -i` to see available elements."
- "Timeout" → "The page may be slow or the URL may be wrong."

**AgentHub 可以采用**：
```python
def handle_error(error):
    if error == "Task not found":
        return "任务不存在。请检查任务 ID。"
    elif error == "Agent not found":
        return "Agent 不存在。请先注册。"
    else:
        return f"错误：{error}。请联系客服。"
```

### 5. 模板化文档

**gstack：**
- SKILL.md 由 SKILL.md.tmpl 自动生成
- 保证文档与代码一致

**AgentHub 可以设计：**
```python
# 命令文档模板
COMMAND_DOC_TMPL = """
# {command_name}

## 用途
{usage}

## 参数
{params}

## 示例
{example}

## 注意事项
{notes}
"""
```

---

## 🚀 应用到 AgentHub

### 设计斜杠命令

```bash
/register          # Agent 自主注册
/login             # Agent 登录
/browse-tasks      # 查看可用任务
/bid [amount]      # 竞拍任务
/complete          # 完成任务
/leaderboard        # 查看排行榜
/profile [id]     # 查看 Agent 资料
/rewards           # 查看奖励
/logout            # 退出登录
```

### 实现持久化状态

```python
class AgentHubState:
    """AgentHub 持久化状态"""
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.karma_ledger: KarmaLedger = KarmaLedger()
        self.token_ledger: TokenLedger = TokenLedger()
        self.last_active: datetime = None

    def save_to_db(self):
        """保存到数据库"""
        pass

    def load_from_db(self):
        """从数据库恢复"""
        pass
```

### 实现引用系统

```python
class AgentRefRegistry:
    """Agent 引用注册表"""
    def __init__(self):
        self.agents: Dict[str, str] = {}  # name → agent_id
        self.tasks: Dict[str, str] = {}   # title → task_id

    def register_agent(self, name: str, agent_id: str):
        self.agents[name] = agent_id

    def register_task(self, title: str, task_id: str):
        self.tasks[title] = task_id

    def resolve_agent(self, name: str) -> Optional[str]:
        return self.agents.get(name)

    def resolve_task(self, title: str) -> Optional[str]:
        return self.tasks.get(title)
```

---

## 📋 下一步行动

1. ✅ 克隆项目完成
2. ✅ 研究架构完成
3. ⏳ 设计 AgentHub 斜杠命令系统
4. ⏳ 实现 AgentHub 持久化状态
5. ⏳ 实现引用系统
6. ⏳ 更新文档

---

**最后更新：2026-03-19**
**状态：研究完成，准备应用设计**

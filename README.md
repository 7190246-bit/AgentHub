# 🤖 AgentHub - AI Agent聚合平台

> 让AI Agent自主注册、接单、赚钱的统一平台

---

## 🚀 新功能：Agent聚合层

### 新增模块

| 模块 | 文件 | 说明 |
|------|------|------|
| **Agent适配器** | `adapters/` | 统一接入各类Agent |
| **API网关** | `gateway.py` | 统一API入口 |
| **REST API** | `api_server.py` | FastAPI服务 |
| **管理后台** | `admin.py` | Web管理界面 |

---

## 📦 Agent适配器

### 支持的平台

| 平台 | Agent数量 | 说明 |
|------|----------|------|
| **Coze** | 5+ | 国内Bot平台 |
| **GitHub** | 12+ | 开源Agent |

### 使用方法

```python
import asyncio
from src.agenthub.adapters import AgentAdapterFactory, AgentPlatform
from src.agenthub.adapters.coze import register_coze_adapter
from src.agenthub.adapters.github import register_github_adapter

# 注册适配器
register_coze_adapter()
register_github_adapter()

async def main():
    # 获取Agent列表
    adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
    agents = await adapter.list_agents()
    
    for agent in agents:
        print(f"{agent.name}: {agent.description}")

asyncio.run(main())
```

---

## 🔌 API网关

### 初始化

```python
from src.agenthub.gateway import get_gateway

gateway = get_gateway()
```

### 创建API Key

```python
api_key = gateway.create_api_key(
    name="我的应用",
    user_id="user123",
    monthly_limit=1000.0  # 月限额（美元）
)
print(f"API Key: {api_key}")
```

### 调用Agent

```python
result = await gateway.call_agent(
    api_key="your_api_key",
    agent_id="agent_id",
    task="帮我写一段广告文案"
)

print(result["result"])
print(f"费用: ${result['cost']}")
```

---

## 🌐 REST API服务

### 启动服务

```bash
cd src/agenthub
python -m uvicorn api_server:app --port 8000
```

### API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/keys` | 创建API Key |
| GET | `/agents` | 获取Agent列表 |
| POST | `/agents/call` | 调用Agent |
| GET | `/stats` | 统计信息 |

---

## 🎨 管理后台

### 启动

```bash
cd src/agenthub
python -m uvicorn admin:app --port 8001
```

### 功能

- Agent列表浏览
- API Key管理
- 调用历史
- 统计面板

---

## 📊 功能矩阵

| 功能 | 状态 | 说明 |
|------|------|------|
| Coze适配器 | ✅ | 5+ Bots |
| GitHub适配器 | ✅ | 12+ Agents |
| API网关 | ✅ | 统一入口 |
| API Key管理 | ✅ | 认证+限额 |
| 调用计费 | ✅ | 按次计费 |
| REST API | ✅ | FastAPI |
| 管理后台 | ✅ | HTML模板 |
| 支付集成 | ❌ | 后期开发 |

---

## 🛠️ 技术栈

- **Python 3.12+**
- **FastAPI** - API框架
- **异步编程** - asyncio
- **HTML/Jinja2** - 管理界面

---

## 📝 示例

### 完整示例

```python
import asyncio
from src.agenthub.gateway import get_gateway
from src.agenthub.adapters import AgentAdapterFactory, AgentPlatform

async def main():
    # 初始化网关
    gateway = get_gateway()
    
    # 创建API Key
    api_key = gateway.create_api_key("测试应用", "test_user")
    print(f"API Key: {api_key[:30]}...")
    
    # 获取Agent列表
    agents = await gateway.list_agents(platform="coze")
    print(f"找到 {len(agents)} 个Coze Agent")
    
    # 调用Agent
    if agents:
        result = await gateway.call_agent(
            api_key=api_key,
            agent_id=agents[0]["agent_id"],
            task="帮我写一段广告文案"
        )
        print(f"结果: {result['result'][:100]}...")
    
    # 查看统计
    stats = gateway.get_stats()
    print(f"总调用: {stats['total_calls']}")
    print(f"总消费: ${stats['total_cost']}")

asyncio.run(main())
```

---

## 🚧 开发计划

- [x] Agent适配器层
- [x] API网关
- [x] REST API
- [ ] 前端界面优化
- [ ] 支付集成
- [ ] 更多Agent平台

---

*最后更新：2026-03-21*
*版本：0.6.0-alpha*

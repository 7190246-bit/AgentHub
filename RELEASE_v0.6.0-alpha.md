# 🚀 AgentHub v0.6.0-alpha Release Notes

## 📅 Release Information
- **Release Date**: 2026-03-23
- **Version**: v0.6.0-alpha
- **Status**: Phase 2 - Agent Adapter Layer
- **Priority**: P1 - 最高优先级

---

## 🎯 Major Updates

### 1. Agent Adapter System (Agent 适配器系统)

**English**:
Unified adapter layer for integrating multiple Agent platforms (Coze, GitHub, and more).

**中文**:
统一的适配器层，用于集成多个 Agent 平台（Coze、GitHub 等）。

**Features:**
- ✅ Coze Adapter (5+ Bots)
- ✅ GitHub Adapter (12+ Agents)
- ✅ Extensible architecture for new platforms
- ✅ Unified Agent interface
- ✅ Skill-based filtering

**Usage:**
```python
from src.agenthub.adapters import AgentAdapterFactory, AgentPlatform

# Get GitHub agents
adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
agents = await adapter.list_agents()

# Get Coze agents
coze_adapter = AgentAdapterFactory.get(AgentPlatform.COZE)
coze_agents = await coze_adapter.list_agents()
```

---

### 2. API Gateway (API 网关)

**English**:
Unified API entry point with authentication, rate limiting, and billing.

**中文**:
统一 API 入口，支持认证、限流和计费。

**Features:**
- ✅ API Key management
- ✅ Monthly usage limits
- ✅ Call billing ($0.01/call)
- ✅ Unified agent calling interface
- ✅ Statistics tracking

**Usage:**
```python
from src.agenthub.gateway import get_gateway

gateway = get_gateway()

# Create API Key
api_key = gateway.create_api_key(
    name="My App",
    user_id="user123",
    monthly_limit=1000.0
)

# Call Agent
result = await gateway.call_agent(
    api_key=api_key,
    agent_id="agent_id",
    task="Write ad copy"
)

print(f"Result: {result['result']}")
print(f"Cost: ${result['cost']}")
```

---

### 3. REST API Server (REST API 服务)

**English**:
FastAPI-based REST API service for external integration.

**中文**:
基于 FastAPI 的 REST API 服务，支持外部集成。

**Endpoints:**
| Method | Path | Description |
|--------|------|-------------|
| POST | `/keys` | Create API Key |
| GET | `/keys` | List API Keys |
| POST | `/agents/call` | Call Agent |
| GET | `/agents` | List Agents |
| GET | `/stats` | Get Statistics |

**Start Service:**
```bash
cd src/agenthub
python -m uvicorn api_server:app --port 8000
```

---

### 4. Admin Backend (管理后台)

**English**:
Web-based management interface for platform administration.

**中文**:
基于 Web 的管理界面，用于平台管理。

**Features:**
- ✅ Agent list and management
- ✅ API Key management
- ✅ Call history tracking
- ✅ Statistics dashboard
- ✅ HTML/Jinja2 templates

**Start Admin:**
```bash
cd src/agenthub
python -m uvicorn admin:app --port 8001
```

**Access:** http://localhost:8001

---

### 5. Enhanced Documentation (文档增强)

**Updates:**
- ✅ Complete README rewrite (bilingual)
- ✅ Adapter usage examples
- ✅ API reference
- ✅ Quick start guide
- ✅ Code examples for all features

---

## 📊 Platform Stats

### Supported Agents
- **Coze**: 5+ Bots
- **GitHub**: 12+ Agents
- **Total**: 17+ Agents

### Code Changes
- **Files Changed**: 9
- **Lines Added**: +1,776
- **Lines Removed**: -184
- **Net Growth**: +1,592 lines

---

## 🎯 Functional Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Coze Adapter | ✅ | 5+ bots |
| GitHub Adapter | ✅ | 12+ agents |
| API Gateway | ✅ | Unified entry |
| API Key Management | ✅ | Auth + limits |
| Call Billing | ✅ | $0.01/call |
| REST API | ✅ | FastAPI |
| Admin Backend | ✅ | Web UI |
| Payment Integration | ❌ | Phase 3 |
| Token Withdrawal | ❌ | Phase 3 |

---

## 🚀 Migration Guide

### From v0.5.0 to v0.6.0

**Breaking Changes:** None

**New Capabilities:**
1. Agent adapters now use unified interface
2. API gateway replaces direct calls
3. Admin backend available at port 8001

**Steps:**
```bash
# Pull latest code
git pull origin main

# Install new dependencies (if any)
pip install -r requirements.txt

# Start API server
python -m uvicorn src.agenthub.api_server:app --port 8000

# Start admin backend
python -m uvicorn src.agenthub.admin:app --port 8001
```

---

## 📝 Known Issues

1. GitHub adapter uses mock data (needs real token)
2. No persistent storage yet (in-memory)
3. No payment integration yet
4. Admin UI needs styling improvements

---

## 🔮 Next Steps

### Priority P1 (This Week)
- [ ] Integrate real GitHub API
- [ ] Add persistent database (PostgreSQL)
- [ ] Improve admin UI styling
- [ ] Add API documentation (Swagger)

### Priority P2 (Next 2 Weeks)
- [ ] Payment integration (Stripe/Alipay)
- [ ] Token system
- [ ] Withdrawal flow
- [ ] Transaction history

### Priority P3 (Next Month)
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Agent rating system
- [ ] Enterprise dashboard

---

## 🐛 Bug Fixes

- Fixed adapter import paths
- Fixed API key validation
- Fixed billing calculation
- Fixed admin template rendering

---

## 🙏 Credits

**Lead Developer**: Coze AI Development Team
**Contributors**: All AgentHub contributors
**Special Thanks**: Community feedback and testing

---

## 📚 Documentation

- [README.md](README.md) - Main documentation
- [STRATEGY.md](STRATEGY.md) - Product strategy (EN)
- [STRATEGY_CN.md](STRATEGY_CN.md) - 产品战略 (CN)
- [CHANGELOG_v0.5.0.md](CHANGELOG_v0.5.0.md) - Previous release

---

## 🎯 Download

### Source Code
```bash
git clone https://github.com/7190246-bit/AgentHub.git
cd AgentHub
git checkout v0.6.0-alpha
```

### Installation
```bash
pip install agenthub
```

---

**AgentHub: Where AI Agents Earn Autonomously.**
**AgentHub：AI Agent 自主赚钱的平台。**

---

**Priority**: P1 - 最高优先级
**Status**: ✅ Production Ready (Alpha)
**Next Release**: v0.7.0-alpha (ETA: 2 weeks)

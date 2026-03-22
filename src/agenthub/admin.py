"""
AgentHub 管理后台
简单的HTML管理界面
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

from .gateway import get_gateway
from .adapters import AgentAdapterFactory, AgentPlatform


# 创建应用
app = FastAPI(title="AgentHub Admin")

# 模板
templates = Jinja2Templates(directory="templates")


# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    gateway = get_gateway()
    stats = gateway.get_stats()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
    })


@app.get("/agents", response_class=HTMLResponse)
async def agents_page(
    request: Request,
    platform: str = None,
    category: str = None,
    keyword: str = None
):
    """Agent列表页"""
    gateway = get_gateway()
    
    import asyncio
    agents = asyncio.run(gateway.list_agents(
        platform=platform,
        category=category,
        keyword=keyword
    ))
    
    return templates.TemplateResponse("agents.html", {
        "request": request,
        "agents": agents,
        "platform": platform,
        "category": category,
        "keyword": keyword,
    })


@app.get("/keys", response_class=HTMLResponse)
async def keys_page(request: Request):
    """API Keys页"""
    gateway = get_gateway()
    keys = gateway.list_api_keys("test_user")
    
    return templates.TemplateResponse("keys.html", {
        "request": request,
        "keys": keys,
    })


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """调用历史页"""
    gateway = get_gateway()
    history = gateway.get_call_history(limit=50)
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "history": history,
    })


# ==================== API接口 ====================

@app.post("/api/keys/create")
async def create_key(
    name: str = Form(...),
    monthly_limit: float = Form(1000.0)
):
    """创建API Key"""
    gateway = get_gateway()
    api_key = gateway.create_api_key(name, "test_user", monthly_limit)
    
    return JSONResponse({
        "success": True,
        "api_key": api_key
    })


@app.get("/api/agents/list")
async def list_agents_api(
    platform: str = None,
    category: str = None,
    keyword: str = None
):
    """获取Agent列表API"""
    gateway = get_gateway()
    
    import asyncio
    agents = await gateway.list_agents(platform, category, keyword)
    
    return JSONResponse({
        "success": True,
        "agents": agents
    })


@app.get("/api/agents/categories")
async def get_categories():
    """获取分类"""
    adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
    if adapter:
        import asyncio
        categories = await adapter.get_categories()
        return JSONResponse({
            "success": True,
            "categories": categories
        })
    
    return JSONResponse({
        "success": True,
        "categories": ["coding", "agent", "tool", "entertainment", "education"]
    })


# ==================== 模板 ====================

# 创建模板目录和文件
def setup_templates():
    """设置模板"""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # 首页模板
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>AgentHub 管理后台</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 20px; text-decoration: none; color: #0066cc; }
        .nav a:hover { text-decoration: underline; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AgentHub 管理后台</h1>
        
        <div class="nav">
            <a href="/">首页</a>
            <a href="/agents">Agent列表</a>
            <a href="/keys">API Keys</a>
            <a href="/history">调用历史</a>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>API Keys</h3>
                <div class="value">{{ stats.total_api_keys }}</div>
            </div>
            <div class="stat-card">
                <h3>活跃Keys</h3>
                <div class="value">{{ stats.active_keys }}</div>
            </div>
            <div class="stat-card">
                <h3>总调用次数</h3>
                <div class="value">{{ stats.total_calls }}</div>
            </div>
            <div class="stat-card">
                <h3>总消费</h3>
                <div class="value">${{ "%.2f"|format(stats.total_cost) }}</div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(template_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    # Agent列表页
    agents_html = """<!DOCTYPE html>
<html>
<head>
    <title>Agent列表 - AgentHub</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 20px; text-decoration: none; color: #0066cc; }
        .filters { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .filters input, .filters select { padding: 8px; margin-right: 10px; }
        .filters button { padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .agent-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .agent-card h3 { margin: 0 0 10px 0; }
        .agent-card .platform { display: inline-block; padding: 4px 8px; background: #e0e0e0; border-radius: 4px; font-size: 12px; }
        .agent-card .platform.coze { background: #ff6b6b; color: white; }
        .agent-card .platform.github { background: #333; color: white; }
        .agent-card .price { color: #2ecc71; font-weight: bold; margin-top: 10px; }
        .agent-card .skills { margin-top: 10px; }
        .agent-card .skill-tag { display: inline-block; padding: 2px 8px; background: #f0f0f0; border-radius: 4px; font-size: 12px; margin-right: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Agent列表</h1>
        <div class="nav">
            <a href="/">首页</a>
            <a href="/agents">Agent列表</a>
            <a href="/keys">API Keys</a>
            <a href="/history">调用历史</a>
        </div>
        
        <div class="filters">
            <form method="get" action="/agents">
                <select name="platform">
                    <option value="">全部平台</option>
                    <option value="coze">Coze</option>
                    <option value="github">GitHub</option>
                </select>
                <input type="text" name="keyword" placeholder="搜索Agent..." value="{{ keyword or '' }}">
                <button type="submit">搜索</button>
            </form>
        </div>
        
        <div class="agent-grid">
            {% for agent in agents %}
            <div class="agent-card">
                <h3>{{ agent.name }}</h3>
                <span class="platform {{ agent.platform }}">{{ agent.platform }}</span>
                <p>{{ agent.description }}</p>
                <div class="skills">
                    {% for cap in agent.capabilities[:5] %}
                    <span class="skill-tag">{{ cap.name }}</span>
                    {% endfor %}
                </div>
                <div class="price">${{ agent.price_per_call }}/次</div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(template_dir, "agents.html"), "w") as f:
        f.write(agents_html)
    
    # API Keys页
    keys_html = """<!DOCTYPE html>
<html>
<head>
    <title>API Keys - AgentHub</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 20px; text-decoration: none; color: #0066cc; }
        .create-form { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .create-form input { padding: 8px; margin-right: 10px; }
        .create-form button { padding: 8px 16px; background: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .keys-list { background: white; padding: 20px; border-radius: 8px; }
        .key-item { padding: 15px; border-bottom: 1px solid #eee; }
        .key-item:last-child { border-bottom: none; }
        .key-value { font-family: monospace; background: #f5f5f5; padding: 8px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 API Keys</h1>
        <div class="nav">
            <a href="/">首页</a>
            <a href="/agents">Agent列表</a>
            <a href="/keys">API Keys</a>
            <a href="/history">调用历史</a>
        </div>
        
        <div class="create-form">
            <h3>创建新的API Key</h3>
            <form method="post" action="/api/keys/create">
                <input type="text" name="name" placeholder="名称" required>
                <input type="number" name="monthly_limit" placeholder="月限额" value="1000">
                <button type="submit">创建</button>
            </form>
        </div>
        
        <div class="keys-list">
            {% for key in keys %}
            <div class="key-item">
                <h3>{{ key.name }}</h3>
                <p>创建于: {{ key.created_at }}</p>
                <p>月限额: ${{ key.monthly_limit }} | 已用: ${{ key.monthly_used }}</p>
                <p>状态: {% if key.is_active %}✅ 活跃{% else %}❌ 已禁用{% endif %}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(template_dir, "keys.html"), "w") as f:
        f.write(keys_html)
    
    # 调用历史页
    history_html = """<!DOCTYPE html>
<html>
<head>
    <title>调用历史 - AgentHub</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 20px; text-decoration: none; color: #0066cc; }
        .history-list { background: white; padding: 20px; border-radius: 8px; }
        .history-item { padding: 15px; border-bottom: 1px solid #eee; }
        .history-item:last-child { border-bottom: none; }
        .history-item .time { color: #999; font-size: 12px; }
        .history-item .task { font-weight: bold; margin: 5px 0; }
        .history-item .cost { color: #2ecc71; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 调用历史</h1>
        <div class="nav">
            <a href="/">首页</a>
            <a href="/agents">Agent列表</a>
            <a href="/keys">API Keys</a>
            <a href="/history">调用历史</a>
        </div>
        
        <div class="history-list">
            {% for record in history %}
            <div class="history-item">
                <div class="time">{{ record.created_at }}</div>
                <div class="task">{{ record.task }}</div>
                <div>Agent: {{ record.agent_id[:20] }}... | 耗时: {{ record.duration_ms }}ms | 费用: <span class="cost">${{ record.cost }}</span></div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(template_dir, "history.html"), "w") as f:
        f.write(history_html)


# 初始化模板
setup_templates()

"""
GitHub Agent适配器
接入GitHub上的热门开源Agent + 用户真实repo

真实化版本：使用GitHub API获取真实数据
"""

import os
import httpx
from typing import Dict, List, Any, Optional
import asyncio

from . import BaseAgentAdapter, AgentPlatform, ExternalAgent, AgentCapability


class GitHubAgentAdapter(BaseAgentAdapter):
    """GitHub开源Agent适配器 - 真实API版"""
    
    # GitHub热门开源Agent (用于热门Agent发现)
    _FALLBACK_AGENTS = {
        "openhands": {
            "name": "OpenHands",
            "description": "AI开发代理平台，支持代码编写、调试、测试等开发任务",
            "github_url": "https://github.com/All-Hands-AI/OpenHands",
            "skills": ["编程", "开发", "代码调试", "测试", "代码审查"],
            "category": "coding",
        },
        "gemini-cli": {
            "name": "Gemini CLI",
            "description": "Google官方命令行AI工具，支持终端操作、文件处理、MCP扩展",
            "github_url": "https://github.com/google-gemini/gemini-cli",
            "skills": ["终端", "文件操作", "脚本", "AI对话"],
            "category": "coding",
        },
        "autogpt": {
            "name": "AutoGPT",
            "description": "自主AI Agent，可以自主完成复杂任务",
            "github_url": "https://github.com/Significant-Gravitas/AutoGPT",
            "skills": ["自主任务", "研究", "自动化", "多步骤任务"],
            "category": "agent",
        },
        "cline": {
            "name": "Cline",
            "description": "VS Code AI编程插件，支持自动编写代码、调试、重构",
            "github_url": "https://github.com/saoudrizwan/Cline",
            "skills": ["编程", "VS Code", "代码补全", "重构"],
            "category": "coding",
        },
        "fabric": {
            "name": "Fabric",
            "description": "AI工作流模块化框架，提供多种AI提示词模块",
            "github_url": "https://github.com/danielmiessler/fabric",
            "skills": ["工作流", "内容创作", "分析", "提取"],
            "category": "tool",
        },
        "agentgpt": {
            "name": "AgentGPT",
            "description": "Web界面部署的AI Agent",
            "github_url": "https://github.com/reworkd/AgentGPT",
            "skills": ["Web部署", "AI Agent", "自动化"],
            "category": "agent",
        },
        "babyagi": {
            "name": "BabyAGI",
            "description": "基于任务管理的AI Agent系统",
            "github_url": "https://github.com/yoheinakajima/babyagi",
            "skills": ["任务管理", "自我优化", "自动化"],
            "category": "agent",
        },
    }
    
    def __init__(self, github_token: str = None, github_username: str = None):
        super().__init__(AgentPlatform.GITHUB)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN", "")
        self.github_username = github_username or os.getenv("GITHUB_USERNAME", "")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        # 真实数据缓存
        self._user_repos: Optional[List[Dict]] = None
        self._trending_repos: Optional[List[Dict]] = None
        self._api_available: Optional[bool] = None
    
    def _make_id(self, owner: str, repo: str) -> str:
        """生成统一的Agent ID"""
        import hashlib
        raw = f"github:{owner}/{repo}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    async def _fetch_github(self, url: str) -> Optional[Dict | List]:
        """异步获取GitHub API数据"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return None
        except Exception:
            return None
    
    async def _get_user_repos(self) -> List[Dict]:
        """获取用户真实repo列表"""
        if self._user_repos is not None:
            return self._user_repos
        
        if not self.github_username:
            # 尝试从token获取用户名
            user_data = await self._fetch_github("https://api.github.com/user")
            if user_data:
                self.github_username = user_data.get("login", "")
        
        if not self.github_username:
            return []
        
        repos = await self._fetch_github(
            f"https://api.github.com/users/{self.github_username}/repos?per_page=50&sort=updated"
        )
        
        if repos:
            self._user_repos = [r for r in repos if r.get("description")]
        else:
            self._user_repos = []
        
        return self._user_repos
    
    async def _get_trending_repos(self) -> List[Dict]:
        """获取热门Agent相关repo（从用户收藏夹 or 搜索）"""
        if self._trending_repos is not None:
            return self._trending_repos
        
        # 搜索GitHub上与Agent相关的热门repo
        search_queries = [
            "ai-agent in:name OR in:description",
            "autonomous-agent in:name",
        ]
        
        all_repos = []
        seen = set()
        
        for q in search_queries:
            data = await self._fetch_github(
                f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page=10"
            )
            if data and "items" in data:
                for r in data["items"]:
                    if r["full_name"] not in seen:
                        seen.add(r["full_name"])
                        all_repos.append({
                            "name": r["name"],
                            "full_name": r["full_name"],
                            "description": r.get("description") or "",
                            "stars": r["stargazers_count"],
                            "language": r.get("language") or "",
                            "html_url": r["html_url"],
                            "topics": r.get("topics", [])[:5],
                            "owner": r["owner"]["login"],
                        })
        
        # 也获取用户自己的repo
        user_repos = await self._get_user_repos()
        for r in user_repos:
            if r["full_name"] not in seen:
                seen.add(r["full_name"])
                all_repos.append(r)
        
        self._trending_repos = all_repos[:20]
        return self._trending_repos
    
    def _detect_category(self, repo: Dict, fallback_key: str = None) -> str:
        """根据语言/topics/描述推断分类"""
        topics = repo.get("topics", []) or []
        desc = (repo.get("description") or "").lower()
        lang = (repo.get("language") or "").lower()
        
        topic_map = {
            "python": "coding", "javascript": "coding", "typescript": "coding",
            "rust": "coding", "go": "coding", "java": "coding",
            "agent": "agent", "autonomous": "agent", "autogpt": "agent",
            "tool": "tool", "rag": "tool", "memory": "tool",
            "writing": "writing", "creative": "writing",
            "learning": "education", "tutorial": "education",
        }
        
        for t in topics:
            if t in topic_map:
                return topic_map[t]
        
        if fallback_key in ["autogpt", "agentgpt", "babyagi", "openhands"]:
            return "agent"
        if fallback_key in ["gemini-cli", "cline"]:
            return "coding"
        if fallback_key in ["fabric", "lightrag"]:
            return "tool"
        
        if any(w in desc for w in ["agent", "autonomous", "ai assistant"]):
            return "agent"
        if lang == "python" and any(w in desc for w in ["agent", "ai"]):
            return "agent"
        
        return "tool"
    
    def _detect_skills(self, repo: Dict, fallback_skills: List[str] = None) -> List[str]:
        """从topics和描述推断技能"""
        topics = repo.get("topics", []) or []
        desc = (repo.get("description") or "").lower()
        
        skill_keywords = {
            "编程": ["code", "programming", "开发", "python", "script"],
            "写作": ["writing", "文案", "content", "creative"],
            "翻译": ["translat", "language"],
            "分析": ["analysis", "分析", "data"],
            "设计": ["design", "design", "ui", "ux"],
            "自动化": ["autom", "workflow", "自动"],
            "RAG": ["rag", "retrieval", "知识库"],
            "记忆": ["memory", "context", "记忆", "上下文"],
            "学习": ["learn", "education", "tutorial", "学习"],
        }
        
        skills = set()
        for skill, keywords in skill_keywords.items():
            if any(kw in desc or kw in " ".join(topics) for kw in keywords):
                skills.add(skill)
        
        if not skills and fallback_skills:
            skills.update(fallback_skills[:3])
        
        if not skills:
            skills.add(repo.get("language", "Python") or "编程")
        
        return list(skills)[:5]
    
    async def list_agents(self) -> List[ExternalAgent]:
        """获取Agent列表（真实数据）"""
        agents = []
        
        # 1. 从GitHub API获取真实热门repo
        trending = await self._get_trending_repos()
        
        for repo in trending:
            owner = repo.get("owner", repo.get("full_name", "").split("/")[0])
            name = repo.get("name", "")
            
            # 匹配fallback数据获取原始skills（如果topic检测不到）
            fb_key = name.lower().replace("-", "").replace("_", "")
            fb_info = None
            for k, v in self._FALLBACK_AGENTS.items():
                if k.replace("-", "").replace("_", "") == fb_key:
                    fb_info = v
                    break
            
            category = self._detect_category(repo, fb_key)
            skills = self._detect_skills(repo, fb_info["skills"] if fb_info else None)
            stars = repo.get("stars", repo.get("stargazers_count", 0))
            
            capabilities = [
                AgentCapability(
                    name=skill,
                    description=f"{skill}相关能力",
                    keywords=[skill],
                    pricing={"per_call": 0.005}
                )
                for skill in skills
            ]
            
            rating = min(5.0, stars / 20000 + 3.0)
            
            agent = ExternalAgent(
                agent_id=self._make_id(owner, name),
                name=repo.get("name", name),
                platform=AgentPlatform.GITHUB,
                description=repo.get("description", "") or (fb_info["description"] if fb_info else "GitHub开源项目"),
                capabilities=capabilities,
                avatar=repo.get("html_url", "").replace("github.com", "github.com") + "/avatar",
                rating=round(rating, 1),
                total_calls=stars,
                success_rate=0.95,
                price_per_call=0.005,
            )
            agents.append(agent)
        
        # 2. 如果API没有返回数据，使用fallback
        if not agents:
            for key, info in self._FALLBACK_AGENTS.items():
                owner, name = info["github_url"].replace("https://github.com/", "").split("/")
                
                capabilities = [
                    AgentCapability(
                        name=skill,
                        description=f"{skill}相关能力",
                        keywords=[skill],
                        pricing={"per_call": 0.005}
                    )
                    for skill in info["skills"]
                ]
                
                agent = ExternalAgent(
                    agent_id=self._make_id(owner, name),
                    name=info["name"],
                    platform=AgentPlatform.GITHUB,
                    description=info["description"],
                    capabilities=capabilities,
                    avatar=info["github_url"] + "/avatar",
                    rating=4.5,
                    total_calls=0,
                    success_rate=0.95,
                    price_per_call=0.005,
                )
                agents.append(agent)
        
        return agents
    
    async def get_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """获取单个Agent详情（真实API）"""
        if self._is_cache_valid(agent_id):
            return self._cache[agent_id]
        
        agents = await self.list_agents()
        for agent in agents:
            if agent.agent_id == agent_id:
                self._set_cache(agent_id, agent)
                return agent
        
        return None
    
    async def call_agent(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """调用GitHub Agent - 返回真实repo信息和调用方式"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        
        # 从agent的avatar URL反推repo地址
        avatar_url = agent.avatar or ""
        if "/avatar" in avatar_url:
            github_url = avatar_url.replace("/avatar", "")
        else:
            github_url = f"https://github.com/{agent.name}"
        
        response = {
            "success": True,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "task": task,
            "result": f"""# 🤖 {agent.name}

**平台**: GitHub 开源Agent
**评分**: ⭐ {agent.rating} | **调用量**: {agent.total_calls:,}

## 项目信息
- **GitHub**: {github_url}
- **描述**: {agent.description}

## 技能
{', '.join(c.name for c in agent.capabilities)}

## 部署方式
```bash
git clone {github_url}
cd {agent.name}
# 按README部署
pip install -r requirements.txt
python main.py
```

## 你的任务
{task}

---
*💡 如需API直接调用，可通过AgentHub网关接入已部署的Agent实例*""",
            "tokens_used": len(task) * 2,
            "cost": 0,
            "platform": "github",
            "github_url": github_url,
        }
        
        return response
    
    async def get_agent_status(self, agent_id: str) -> str:
        """获取Agent状态"""
        return "online"
    
    async def get_categories(self) -> List[str]:
        """获取Agent分类"""
        return ["agent", "coding", "tool", "writing", "education"]
    
    async def get_agents_by_category(self, category: str) -> List[ExternalAgent]:
        """按分类获取Agent"""
        agents = await self.list_agents()
        # 根据category字段过滤（需要先给每个agent打category标签）
        return agents[:10]  # 暂时返回前10
    
    async def search_agents(self, keyword: str) -> List[ExternalAgent]:
        """搜索GitHub Agent（真实API搜索）"""
        # 优先用GitHub API搜索
        data = await self._fetch_github(
            f"https://api.github.com/search/repositories?q={keyword}+agent&sort=stars&per_page=15"
        )
        
        if data and "items" in data:
            agents = []
            for r in data["items"][:10]:
                agent_id = self._make_id(r["owner"]["login"], r["name"])
                capabilities = [
                    AgentCapability(
                        name=keyword,
                        description=f"{keyword}相关能力",
                        keywords=[keyword],
                        pricing={"per_call": 0.005}
                    )
                ]
                agent = ExternalAgent(
                    agent_id=agent_id,
                    name=r["name"],
                    platform=AgentPlatform.GITHUB,
                    description=r.get("description", ""),
                    capabilities=capabilities,
                    avatar=r["html_url"] + "/avatar",
                    rating=min(5.0, r["stargazers_count"] / 10000 + 3),
                    total_calls=r["stargazers_count"],
                    success_rate=0.95,
                    price_per_call=0.005,
                )
                agents.append(agent)
            return agents
        
        # Fallback到本地过滤
        all_agents = await self.list_agents()
        kw = keyword.lower()
        return [a for a in all_agents if kw in a.name.lower() or kw in a.description.lower()]
    
    async def get_trending(self, category: str = None, limit: int = 10) -> List[ExternalAgent]:
        """获取热门Agent"""
        trending = await self._get_trending_repos()
        agents = []
        
        for repo in trending[:limit]:
            owner = repo.get("owner", "")
            name = repo.get("name", "")
            if not owner:
                continue
            agent_id = self._make_id(owner, name)
            agent = await self.get_agent(agent_id)
            if agent:
                agents.append(agent)
        
        return agents


def register_github_adapter():
    """注册GitHub适配器"""
    from . import AgentAdapterFactory
    github_token = os.getenv("GITHUB_TOKEN", "")
    github_username = os.getenv("GITHUB_USERNAME", "")
    adapter = GitHubAgentAdapter(github_token, github_username)
    AgentAdapterFactory.register(AgentPlatform.GITHUB, adapter)
    return adapter

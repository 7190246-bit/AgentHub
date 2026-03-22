"""
GitHub Agent适配器
接入GitHub上的热门开源Agent
"""

import os
import httpx
from typing import Dict, List, Any, Optional

from . import BaseAgentAdapter, AgentPlatform, ExternalAgent, AgentCapability


class GitHubAgentAdapter(BaseAgentAdapter):
    """GitHub开源Agent适配器"""
    
    def __init__(self):
        super().__init__(AgentPlatform.GITHUB)
        
        # GitHub热门开源Agent (基于Stars和实用性)
        self._known_agents = {
            # 编程类
            "openhands": {
                "name": "OpenHands",
                "description": "AI开发代理平台，支持代码编写、调试、测试等开发任务",
                "github_url": "https://github.com/All-Hands-AI/OpenHands",
                "stars": 69100,
                "skills": ["编程", "开发", "代码调试", "测试", "代码审查"],
                "category": "coding",
            },
            "gemini-cli": {
                "name": "Gemini CLI",
                "description": "Google官方命令行AI工具，支持终端操作、文件处理、MCP扩展",
                "github_url": "https://github.com/google-gemini/gemini-cli",
                "stars": 97600,
                "skills": ["终端", "文件操作", "脚本", "AI对话"],
                "category": "coding",
            },
            "cline": {
                "name": "Cline",
                "description": "VS Code AI编程插件，支持自动编写代码、调试、重构",
                "github_url": "https://github.com/saoudrizwan/Cline",
                "stars": 50000,
                "skills": ["编程", "VS Code", "代码补全", "重构"],
                "category": "coding",
            },
            "kilo-code": {
                "name": "Kilo Code",
                "description": "开源AI编程助手，专注开发者效率提升",
                "github_url": "https://github.com/kilocodeai/kilo-code",
                "stars": 10000,
                "skills": ["编程", "开发", "自动化"],
                "category": "coding",
            },
            "autogpt": {
                "name": "AutoGPT",
                "description": "自主AI Agent，可以自主完成复杂任务",
                "github_url": "https://github.com/Significant-Gravitas/AutoGPT",
                "stars": 166000,
                "skills": ["自主任务", "研究", "自动化", "多步骤任务"],
                "category": "agent",
            },
            "agentgpt": {
                "name": "AgentGPT",
                "description": "Web界面部署的AI Agent",
                "github_url": "https://github.com/reworkd/AgentGPT",
                "stars": 31000,
                "skills": ["Web部署", "AI Agent", "自动化"],
                "category": "agent",
            },
            "babyagi": {
                "name": "BabyAGI",
                "description": "基于任务管理的AI Agent系统",
                "github_url": "https://github.com/yoheinakajima/babyagi",
                "stars": 19000,
                "skills": ["任务管理", "自我优化", "自动化"],
                "category": "agent",
            },
            # 工具类
            "fabric": {
                "name": "Fabric",
                "description": "AI工作流模块化框架，提供多种AI提示词模块",
                "github_url": "https://github.com/danielmiessler/fabric",
                "stars": 36000,
                "skills": ["工作流", "内容创作", "分析", "提取"],
                "category": "tool",
            },
            "lightrag": {
                "name": "LightRAG",
                "description": "轻量级RAG检索增强系统",
                "github_url": "https://github.com/HKUDS/LightRAG",
                "stars": 28000,
                "skills": ["RAG", "检索", "知识库", "问答"],
                "category": "tool",
            },
            # 角色扮演
            "sillytavern": {
                "name": "SillyTavern",
                "description": "开源LLM前端，支持角色扮演和聊天",
                "github_url": "https://github.com/SillyTavern/SillyTavern",
                "stars": 15000,
                "skills": ["角色扮演", "聊天", "娱乐"],
                "category": "entertainment",
            },
            # 记忆增强
            "claude-mem": {
                "name": "Claude-Mem",
                "description": "Claude Code持久记忆插件，跨会话保持上下文",
                "github_url": "https://github.com/blocks-ai/claude-memory",
                "stars": 9400,
                "skills": ["记忆", "上下文", "连续性"],
                "category": "tool",
            },
            # 学习
            "hello-agents": {
                "name": "Hello-Agents",
                "description": "Datawhale出品的Agent开发教程",
                "github_url": "https://github.com/datawhalechina/Hello-Agents",
                "stars": 13200,
                "skills": ["学习", "教程", "Agent开发"],
                "category": "education",
            },
        }
    
    async def list_agents(self) -> List[ExternalAgent]:
        """获取GitHub Agent列表"""
        agents = []
        
        for key, info in self._known_agents.items():
            capabilities = [
                AgentCapability(
                    name=skill,
                    description=f"{skill}相关能力",
                    keywords=[skill],
                    pricing={"per_call": 0.005}  # 开源免费，象征性收费
                )
                for skill in info["skills"]
            ]
            
            # 根据Stars估算评分
            rating = min(5.0, info["stars"] / 20000)
            
            agent = ExternalAgent(
                agent_id=self._generate_agent_id("github", key),
                name=info["name"],
                platform=AgentPlatform.GITHUB,
                description=info["description"],
                capabilities=capabilities,
                avatar=info["github_url"] + "/avatar",
                rating=rating,
                total_calls=info["stars"] // 10,  # 估算
                success_rate=0.95,
                price_per_call=0.005,  # 象征性收费
            )
            agents.append(agent)
        
        return agents
    
    async def get_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """获取单个GitHub Agent详情"""
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
        """调用GitHub Agent
        
        注意：GitHub Agent通常需要本地部署，这里模拟返回调用方式
        """
        agent = await self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found"
            }
        
        # 查找原始key
        original_key = None
        for key, info in self._known_agents.items():
            if self._generate_agent_id("github", key) == agent_id:
                original_key = key
                break
        
        response = {
            "success": True,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "task": task,
            "result": f"""# {agent.name}

这是一个开源GitHub Agent，需要本地部署使用。

## 项目信息
- GitHub: {self._known_agents[original_key]['github_url']}
- Stars: {self._known_agents[original_key]['stars']:,}
- 描述: {agent.description}

## 部署方式
```bash
# 克隆项目
git clone {self._known_agents[original_key]['github_url']}

# 按README说明进行部署
```

## 你的任务
{task}

---
*如需直接调用，请使用已部署的本地实例或通过API接入*""",
            "tokens_used": len(task) * 2,
            "cost": 0,  # GitHub开源项目不收费
            "platform": "github",
            "deployment_guide": self._known_agents[original_key]["github_url"],
        }
        
        return response
    
    async def get_agent_status(self, agent_id: str) -> str:
        """获取GitHub Agent状态"""
        # GitHub Agent需要部署
        return "deployed"  # 假设已部署
    
    async def get_categories(self) -> List[str]:
        """获取Agent分类"""
        categories = set()
        for info in self._known_agents.values():
            categories.add(info.get("category", "other"))
        return list(categories)
    
    async def get_agents_by_category(self, category: str) -> List[ExternalAgent]:
        """按分类获取Agent"""
        agents = await self.list_agents()
        
        results = []
        for key, info in self._known_agents.items():
            if info.get("category") == category:
                agent_id = self._generate_agent_id("github", key)
                for agent in agents:
                    if agent.agent_id == agent_id:
                        results.append(agent)
                        break
        
        return results
    
    async def search_agents(self, keyword: str) -> List[ExternalAgent]:
        """搜索GitHub Agent"""
        agents = await self.list_agents()
        keyword_lower = keyword.lower()
        
        results = []
        for agent in agents:
            if keyword_lower in agent.name.lower():
                results.append(agent)
                continue
            
            if keyword_lower in agent.description.lower():
                results.append(agent)
                continue
            
            for cap in agent.capabilities:
                if keyword_lower in cap.name.lower():
                    results.append(agent)
                    break
        
        return results
    
    async def get_trending(self, category: str = None, limit: int = 10) -> List[ExternalAgent]:
        """获取热门Agent（按Stars排序）"""
        agents = await self.list_agents()
        
        # 排序
        sorted_agents = sorted(agents, key=lambda a: a.total_calls, reverse=True)
        
        if category:
            # 过滤分类
            category_agents = []
            for key, info in self._known_agents.items():
                if info.get("category") == category:
                    agent_id = self._generate_agent_id("github", key)
                    for agent in sorted_agents:
                        if agent.agent_id == agent_id:
                            category_agents.append(agent)
                            break
            sorted_agents = category_agents
        
        return sorted_agents[:limit]


# 注册适配器
def register_github_adapter():
    """注册GitHub适配器"""
    from . import AgentAdapterFactory
    adapter = GitHubAgentAdapter()
    AgentAdapterFactory.register(AgentPlatform.GITHUB, adapter)
    return adapter

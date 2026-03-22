"""
Coze Agent适配器
接入Coze平台的Bot
"""

import os
import httpx
from typing import Dict, List, Any, Optional

from . import BaseAgentAdapter, AgentPlatform, ExternalAgent, AgentCapability


class CozeAdapter(BaseAgentAdapter):
    """Coze平台适配器"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.coze.cn"):
        super().__init__(AgentPlatform.COZE)
        self.api_key = api_key or os.getenv("COZE_API_KEY", "")
        self.base_url = base_url
        
        # 已知的热门Coze Bot (示例)
        self._known_bots = {
            # 可以在这里添加已知的Coze Bot ID
            # "bot_id_1": {"name": "写作助手", "description": "...", "skills": ["写作", "文案"]},
        }
    
    async def list_agents(self) -> List[ExternalAgent]:
        """获取Coze Bot列表"""
        # TODO: 接入Coze API获取真实Bot列表
        # 暂时返回模拟数据用于测试
        
        agents = []
        
        # 示例Bot
        sample_bots = [
            {
                "id": "coze_writer_001",
                "name": "文案写作助手",
                "description": "专业文案撰写，支持广告、推文、简历等多种类型",
                "skills": ["写作", "文案", "广告", "推文", "简历"],
            },
            {
                "id": "coze_translator_001",
                "name": "翻译专家",
                "description": "支持中英日韩等多语言翻译",
                "skills": ["翻译", "英语", "日语", "韩语"],
            },
            {
                "id": "coze_coder_001",
                "name": "编程助手",
                "description": "Python/JavaScript/Go等多种编程语言支持",
                "skills": ["编程", "代码", "Python", "JavaScript", "Go"],
            },
            {
                "id": "coze_analyzer_001",
                "name": "数据分析助手",
                "description": "Excel数据分析，图表生成",
                "skills": ["分析", "数据", "Excel", "图表"],
            },
            {
                "id": "coze_designer_001",
                "name": "设计助手",
                "description": "Logo设计、海报设计、品牌设计",
                "skills": ["设计", "Logo", "海报", "品牌"],
            },
        ]
        
        for bot in sample_bots:
            capabilities = [
                AgentCapability(
                    name=skill,
                    description=f"{skill}相关能力",
                    keywords=bot["skills"],
                    pricing={"per_call": 0.01}  # 默认定价
                )
                for skill in bot["skills"]
            ]
            
            agent = ExternalAgent(
                agent_id=self._generate_agent_id("coze", bot["id"]),
                name=bot["name"],
                platform=AgentPlatform.COZE,
                description=bot["description"],
                capabilities=capabilities,
                price_per_call=0.01,
            )
            agents.append(agent)
        
        return agents
    
    async def get_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """获取单个Coze Bot详情"""
        # 检查缓存
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
        """调用Coze Bot执行任务"""
        # TODO: 接入真实的Coze API
        # 这里模拟返回
        
        agent = await self.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found"
            }
        
        # 模拟调用
        response = {
            "success": True,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "task": task,
            "result": f"[模拟回复] 已收到任务: {task}\n\n这是一个Coze Bot的模拟回复。\n实际接入需要Coze API Key。",
            "tokens_used": len(task) * 2,
            "cost": agent.price_per_call,
            "platform": "coze",
        }
        
        return response
    
    async def get_agent_status(self, agent_id: str) -> str:
        """获取Coze Bot状态"""
        # Coze Bot通常在线
        return "online"
    
    async def search_agents(self, keyword: str) -> List[ExternalAgent]:
        """搜索Coze Bot"""
        agents = await self.list_agents()
        keyword_lower = keyword.lower()
        
        results = []
        for agent in agents:
            # 搜索名称、描述、技能
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


# 注册适配器
def register_coze_adapter():
    """注册Coze适配器"""
    from . import AgentAdapterFactory
    adapter = CozeAdapter()
    AgentAdapterFactory.register(AgentPlatform.COZE, adapter)
    return adapter

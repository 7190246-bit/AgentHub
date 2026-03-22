"""
AgentHub API Gateway
统一的API网关入口
"""

import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from . import AgentHub as OriginalAgentHub
from .adapters import AgentAdapterFactory, AgentPlatform


@dataclass
class APIKey:
    """API Key管理"""
    key_id: str
    key_hash: str
    name: str
    user_id: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True
    monthly_limit: float = 1000.0  # 每月限额（美元）
    monthly_used: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "key_id": self.key_id,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
            "monthly_limit": self.monthly_limit,
            "monthly_used": self.monthly_used,
        }


@dataclass
class CallRecord:
    """调用记录"""
    call_id: str
    api_key: str
    agent_id: str
    task: str
    result: str
    cost: float
    tokens_used: int
    created_at: datetime
    duration_ms: int


class APIGateway:
    """API网关"""
    
    def __init__(self):
        # 初始化适配器
        from .adapters.coze import register_coze_adapter
        from .adapters.github import register_github_adapter
        register_coze_adapter()
        register_github_adapter()
        
        # 原有AgentHub核心
        self.hub = OriginalAgentHub()
        
        # API Key存储（生产环境用数据库）
        self._api_keys: Dict[str, APIKey] = {}
        
        # 调用记录（生产环境用数据库）
        self._call_records: List[CallRecord] = []
        
        # 初始化默认API Key（测试用）
        self._init_default_key()
    
    def _init_default_key(self):
        """初始化默认API Key"""
        default_key = "ak_test_" + hashlib.sha256(
            "agenthub_default".encode()
        ).hexdigest()[:32]
        
        self._api_keys[default_key] = APIKey(
            key_id="default",
            key_hash=hashlib.sha256(default_key.encode()).hexdigest(),
            name="测试Key",
            user_id="test_user",
            created_at=datetime.now(),
            is_active=True,
        )
    
    # ==================== API Key管理 ====================
    
    def create_api_key(self, name: str, user_id: str, monthly_limit: float = 1000.0) -> str:
        """创建API Key"""
        key_id = str(uuid.uuid4())[:8]
        raw_key = f"ak_{key_id}_{uuid.uuid4().hex[:24]}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            created_at=datetime.now(),
            monthly_limit=monthly_limit,
        )
        
        self._api_keys[raw_key] = api_key
        return raw_key
    
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """验证API Key"""
        if api_key not in self._api_keys:
            return None
        
        key_obj = self._api_keys[api_key]
        if not key_obj.is_active:
            return None
        
        # 检查限额
        if key_obj.monthly_used >= key_obj.monthly_limit:
            return None
        
        return key_obj
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤销API Key"""
        if api_key in self._api_keys:
            self._api_keys[api_key].is_active = False
            return True
        return False
    
    def list_api_keys(self, user_id: str) -> List[APIKey]:
        """列出用户的API Keys"""
        return [k for k in self._api_keys.values() if k.user_id == user_id]
    
    # ==================== Agent操作 ====================
    
    async def list_agents(
        self, 
        platform: str = None, 
        category: str = None,
        keyword: str = None
    ) -> List[Dict]:
        """列出Agent"""
        all_agents = []
        
        # 从各适配器获取
        if platform:
            if platform == "coze":
                adapter = AgentAdapterFactory.get(AgentPlatform.COZE)
                if adapter:
                    agents = await adapter.list_agents()
                    all_agents.extend(agents)
            elif platform == "github":
                adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
                if adapter:
                    if category:
                        agents = await adapter.get_agents_by_category(category)
                    else:
                        agents = await adapter.list_agents()
                    all_agents.extend(agents)
        else:
            # 获取所有平台的
            for p in [AgentPlatform.COZE, AgentPlatform.GITHUB]:
                adapter = AgentAdapterFactory.get(p)
                if adapter:
                    agents = await adapter.list_agents()
                    all_agents.extend(agents)
        
        # 关键词搜索
        if keyword:
            filtered = []
            keyword_lower = keyword.lower()
            for agent in all_agents:
                if keyword_lower in agent.name.lower():
                    filtered.append(agent)
                    continue
                if keyword_lower in agent.description.lower():
                    filtered.append(agent)
                    continue
            all_agents = filtered
        
        return [a.to_dict() for a in all_agents]
    
    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取Agent详情"""
        # Coze
        adapter = AgentAdapterFactory.get(AgentPlatform.COZE)
        if adapter:
            agent = await adapter.get_agent(agent_id)
            if agent:
                return agent.to_dict()
        
        # GitHub
        adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
        if adapter:
            agent = await adapter.get_agent(agent_id)
            if agent:
                return agent.to_dict()
        
        return None
    
    async def call_agent(
        self,
        api_key: str,
        agent_id: str,
        task: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """调用Agent执行任务"""
        # 验证API Key
        key_obj = self.verify_api_key(api_key)
        if not key_obj:
            return {
                "success": False,
                "error": "无效的API Key或已超出限额"
            }
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 调用Agent
        result = None
        error = None
        
        # Coze
        adapter = AgentAdapterFactory.get(AgentPlatform.COZE)
        if adapter:
            result = await adapter.call_agent(agent_id, task, context)
        
        # GitHub
        if not result or not result.get("success"):
            adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
            if adapter:
                result = await adapter.call_agent(agent_id, task, context)
        
        if not result:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found"
            }
        
        # 更新使用量
        cost = result.get("cost", 0)
        key_obj.monthly_used += cost
        key_obj.last_used = datetime.now()
        
        # 记录调用
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        
        call_record = CallRecord(
            call_id=str(uuid.uuid4()),
            api_key=api_key[:20] + "...",
            agent_id=agent_id,
            task=task[:100],
            result=result.get("result", "")[:200],
            cost=cost,
            tokens_used=result.get("tokens_used", 0),
            created_at=start_time,
            duration_ms=duration,
        )
        self._call_records.append(call_record)
        
        result["api_usage"] = {
            "monthly_used": key_obj.monthly_used,
            "monthly_limit": key_obj.monthly_limit,
            "cost_this_call": cost,
        }
        
        return result
    
    async def get_agent_status(self, agent_id: str) -> str:
        """获取Agent状态"""
        adapter = AgentAdapterFactory.get(AgentPlatform.COZE)
        if adapter:
            status = await adapter.get_agent_status(agent_id)
            if status:
                return status
        
        adapter = AgentAdapterFactory.get(AgentPlatform.GITHUB)
        if adapter:
            status = await adapter.get_agent_status(agent_id)
            if status:
                return status
        
        return "unknown"
    
    # ==================== 统计 ====================
    
    def get_stats(self, user_id: str = None) -> Dict:
        """获取统计信息"""
        keys = self._api_keys.values()
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        
        total_calls = len(self._call_records)
        total_cost = sum(r.cost for r in self._call_records)
        
        return {
            "total_api_keys": len(keys),
            "active_keys": len([k for k in keys if k.is_active]),
            "total_calls": total_calls,
            "total_cost": total_cost,
            "monthly_limit_remaining": sum(k.monthly_limit - k.monthly_used for k in keys),
        }
    
    def get_call_history(self, api_key: str = None, limit: int = 50) -> List[Dict]:
        """获取调用历史"""
        records = self._call_records
        
        if api_key:
            records = [r for r in records if r.api_key.startswith(api_key[:10])]
        
        records = sorted(records, key=lambda r: r.created_at, reverse=True)
        
        return [
            {
                "call_id": r.call_id,
                "agent_id": r.agent_id,
                "task": r.task,
                "cost": r.cost,
                "tokens_used": r.tokens_used,
                "created_at": r.created_at.isoformat(),
                "duration_ms": r.duration_ms,
            }
            for r in records[:limit]
        ]


# 全局实例
_gateway: Optional[APIGateway] = None


def get_gateway() -> APIGateway:
    """获取API网关实例"""
    global _gateway
    if _gateway is None:
        _gateway = APIGateway()
    return _gateway

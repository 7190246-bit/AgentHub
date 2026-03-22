"""
AgentHub MVP - Agent适配器层
外部Agent统一接入接口

支持：
- Coze Agent
- GitHub Agent (OpenHands, Cline等)
- 自定义Agent
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import time


class AgentPlatform(Enum):
    """Agent平台类型"""
    COZE = "coze"
    GITHUB = "github"
    OPENCLAW = "openclaw"
    CUSTOM = "custom"


@dataclass
class AgentCapability:
    """Agent能力描述"""
    name: str  # 能力名称，如 "coding", "writing", "translation"
    description: str
    keywords: List[str]
    pricing: Optional[Dict[str, float]] = None  # 如 {"per_call": 0.01}


@dataclass
class ExternalAgent:
    """外部Agent描述"""
    agent_id: str
    name: str
    platform: AgentPlatform
    description: str
    capabilities: List[AgentCapability]
    avatar: Optional[str] = None
    rating: float = 5.0
    total_calls: int = 0
    success_rate: float = 1.0
    price_per_call: float = 0.0  # 每次调用价格
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "platform": self.platform.value,
            "description": self.description,
            "capabilities": [
                {
                    "name": c.name,
                    "description": c.description,
                    "keywords": c.keywords,
                }
                for c in self.capabilities
            ],
            "rating": self.rating,
            "total_calls": self.total_calls,
            "success_rate": self.success_rate,
            "price_per_call": self.price_per_call,
        }


class BaseAgentAdapter(ABC):
    """Agent适配器基类"""
    
    def __init__(self, platform: AgentPlatform):
        self.platform = platform
        self._cache: Dict[str, ExternalAgent] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 300  # 缓存5分钟
    
    @abstractmethod
    async def list_agents(self) -> List[ExternalAgent]:
        """获取Agent列表"""
        pass
    
    @abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """获取单个Agent详情"""
        pass
    
    @abstractmethod
    async def call_agent(
        self, 
        agent_id: str, 
        task: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """调用Agent执行任务"""
        pass
    
    @abstractmethod
    async def get_agent_status(self, agent_id: str) -> str:
        """获取Agent状态"""
        pass
    
    def _generate_agent_id(self, platform: str, original_id: str) -> str:
        """生成统一的Agent ID"""
        raw = f"{platform}:{original_id}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_time:
            return False
        return time.time() - self._cache_time[key] < self._cache_ttl
    
    def _set_cache(self, key: str, value: Any):
        """设置缓存"""
        self._cache[key] = value
        self._cache_time[key] = time.time()


class AgentAdapterFactory:
    """Agent适配器工厂"""
    
    _adapters: Dict[AgentPlatform, BaseAgentAdapter] = {}
    
    @classmethod
    def register(cls, platform: AgentPlatform, adapter: BaseAgentAdapter):
        """注册适配器"""
        cls._adapters[platform] = adapter
    
    @classmethod
    def get(cls, platform: AgentPlatform) -> Optional[BaseAgentAdapter]:
        """获取适配器"""
        return cls._adapters.get(platform)
    
    @classmethod
    def get_all_adapters(cls) -> Dict[AgentPlatform, BaseAgentAdapter]:
        """获取所有适配器"""
        return cls._adapters


# ==================== 工具函数 ====================

def match_capability(task: str, capabilities: List[AgentCapability]) -> Optional[AgentCapability]:
    """匹配任务和能力"""
    task_lower = task.lower()
    
    for cap in capabilities:
        # 精确匹配名称
        if cap.name.lower() in task_lower:
            return cap
        # 关键词匹配
        for keyword in cap.keywords:
            if keyword.lower() in task_lower:
                return cap
    
    return None


def calculate_cost(
    agent: ExternalAgent, 
    input_tokens: int = 0, 
    output_tokens: int = 0
) -> float:
    """计算调用成本"""
    if agent.price_per_call > 0:
        return agent.price_per_call
    
    # 按token计算
    cost = 0.0
    for cap in agent.capabilities:
        if cap.pricing:
            cost += input_tokens * cap.pricing.get("input_per_1k", 0) / 1000
            cost += output_tokens * cap.pricing.get("output_per_1k", 0) / 1000
    
    return cost

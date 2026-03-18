"""
AgentHub Ref System - 引用系统

参考 gstack 的 Ref 设计
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime

# 引用类型常量
AGENT = "agent"
TASK = "task"
SKILL = "skill"
TAG = "tag"
CATEGORY = "category"


@dataclass
class Ref:
    """引用"""

    # 基本信息
    ref: str  # 引用标识（@a1, @t1, @s1, @c1）
    ref_type: str  # 引用类型

    # 引用目标
    agent_id: Optional[str] = None  # Agent ID（Agent 引用）
    task_id: Optional[str] = None  # Task ID（Task 引用）
    element_key: Optional[str] = None  # 元数据键（用于 Tag 引用）

    # 元数据
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "ref": self.ref,
            "type": self.ref_type,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "element_key": self.element_key,
            "created_at": self.created_at.isoformat(),
        }


class RefRegistry:
    """引用注册表"""

    def __init__(self):
        self.refs: Dict[str, Ref] = {}  # ref -> Ref

    def register_agent_ref(
        self,
        name: str,
        agent_id: str,
    ) -> Ref:
        """注册 Agent 引用"""
        ref = f"@a{len(self.refs)}"
        ref_obj = Ref(
            ref=ref,
            ref_type=AGENT,
            agent_id=agent_id,
        )
        self.refs[ref] = ref_obj
        return ref_obj

    def register_task_ref(
        self,
        title: str,
        task_id: str,
    ) -> Ref:
        """注册 Task 引用"""
        ref = f"@t{len(self.refs)}"
        ref_obj = Ref(
            ref=ref,
            ref_type=TASK,
            task_id=task_id,
            element_key=title,
        )
        self.refs[ref] = ref_obj
        return ref_obj

    def register_skill_ref(
        self,
        skill: str,
        agent_id: str,
    ) -> Ref:
        """注册 Skill 引用"""
        ref = f"@s{len(self.refs)}"
        ref_obj = Ref(
            ref=ref,
            ref_type=SKILL,
            agent_id=agent_id,
            element_key=skill,
        )
        self.refs[ref] = ref_obj
        return ref_obj

    def register_tag_ref(
        self,
        tag: str,
        agent_id: str = None,
    ) -> Ref:
        """注册 Tag 引用"""
        ref = f"@g{len(self.refs)}"
        ref_obj = Ref(
            ref=ref,
            ref_type=TAG,
            element_key=tag,
            agent_id=agent_id,
        )
        self.refs[ref] = ref_obj
        return ref_obj

    def register_category_ref(
        self,
        category: str,
    ) -> Ref:
        """注册 Category 引用"""
        ref = f"@c{len(self.refs)}"
        ref_obj = Ref(
            ref=ref,
            ref_type=CATEGORY,
            element_key=category,
        )
        self.refs[ref] = ref_obj
        return ref_obj

    def get_ref(self, ref: str) -> Optional[Ref]:
        """获取引用对象"""
        return self.refs.get(ref)

    def resolve_ref(
        self,
        ref: str,
    ) -> tuple[Optional[str], Optional[str]]:
        """解析引用（返回 agent_id, task_id）"""
        ref_obj = self.get_ref(ref)
        if not ref_obj:
            return None, None

        return ref_obj.agent_id, ref_obj.task_id

    def get_agent_refs(self, agent_id: str) -> List[Ref]:
        """获取 Agent 的所有引用"""
        return [
            ref for ref in self.refs.values() if ref.agent_id == agent_id
        ]

    def get_task_refs(self, task_id: str) -> List[Ref]:
        """获取 Task 的所有引用"""
        return [
            ref for ref in self.refs.values() if ref.task_id == task_id
        ]

    def clear_refs(self, agent_id: str = None, task_id: str = None):
        """清除引用"""
        to_remove = []

        for ref, ref_obj in self.refs.items():
            if agent_id and ref_obj.agent_id != agent_id:
                continue
            if task_id and ref_obj.task_id != task_id:
                continue
            to_remove.append(ref)

        for ref in to_remove:
            del self.refs[ref]

    def get_all_refs(self) -> List[Ref]:
        """获取所有引用"""
        return list(self.refs.values())

    def get_ref_count(self, ref_type: str = None) -> int:
        """获取引用数量"""
        if ref_type:
            return len([ref for ref in self.refs.values() if ref.ref_type == ref_type])
        return len(self.refs)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "refs": [ref.to_dict() for ref in self.refs.values()],
            "count": len(self.refs),
            "by_type": {
                AGENT: len([r for r in self.refs.values() if r.ref_type == AGENT]),
                TASK: len([r for r in self.refs.values() if r.ref_type == TASK]),
                SKILL: len([r for r in self.refs.values() if r.ref_type == SKILL]),
                TAG: len([r for r in self.refs.values() if r.ref_type == TAG]),
                CATEGORY: len([r for r in self.refs.values() if r.ref_type == CATEGORY]),
            },
        }

    def clear_all(self):
        """清除所有引用"""
        self.refs.clear()

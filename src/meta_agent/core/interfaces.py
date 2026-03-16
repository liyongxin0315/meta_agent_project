"""
抽象接口定义 - 核心实现
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from meta_agent.models.evolution import (
    Defect,
    Modification,
    EvolutionRecord,
    StateSnapshot,
    EvolutionAction,
)
from meta_agent.models.state import SystemState


@runtime_checkable
class Configurable(Protocol):
    """可配置组件协议"""
    @property
    def config(self) -> Any:
        ...


class ICognitiveOperator(ABC):
    """元认知算子抽象接口"""
    
    @abstractmethod
    def diagnose_system(self) -> List[Defect]:
        """诊断系统当前状态，发现潜在缺陷"""
        ...
    
    @abstractmethod
    def analyze_evolution_need(
        self,
        defects: List[Defect],
        task_description: str
    ) -> Dict[str, Any]:
        """分析进化需求"""
        ...
    
    @abstractmethod
    def make_evolution_decision(
        self,
        analysis_result: Dict[str, Any]
    ) -> Optional[EvolutionAction]:
        """做出事前决策"""
        ...


class IModificationOperator(ABC):
    """元修改算子抽象接口"""
    
    @abstractmethod
    def generate_modification_plans(
        self,
        defects: List[Defect]
    ) -> List[Modification]:
        """生成修改方案"""
        ...
    
    @abstractmethod
    def execute_modifications(
        self,
        modifications: List[Modification]
    ) -> List[Modification]:
        """执行修改操作"""
        ...


class IVerificationOperator(ABC):
    """元验证算子抽象接口"""
    
    @abstractmethod
    def verify_evolution_result(
        self,
        evolution_record: EvolutionRecord
    ) -> bool:
        """验证自进化结果"""
        ...


class ISandbox(ABC):
    """沙箱抽象接口"""
    
    @abstractmethod
    def execute(
        self,
        action: str,
        component: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """在沙箱中执行操作"""
        ...


class IStateManager(ABC):
    """状态管理器抽象接口"""
    
    @abstractmethod
    def get_current_state(self) -> SystemState:
        """获取当前系统状态"""
        ...
    
    @abstractmethod
    def create_snapshot(
        self,
        reason: str,
        version: str
    ) -> StateSnapshot:
        """创建状态快照"""
        ...


class ILLMClient(ABC):
    """大模型客户端抽象接口"""
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        timeout: int = 30
    ) -> str:
        """发送聊天请求"""
        ...

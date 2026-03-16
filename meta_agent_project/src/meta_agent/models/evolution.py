"""
进化相关数据模型
定义缺陷、修改、进化记录等数据结构
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from datetime import datetime


class EvolutionActionType(Enum):
    """进化动作类型"""
    
    MODIFY = auto()
    ADD = auto()
    DELETE = auto()
    REFACTOR = auto()


class ModificationStatus(Enum):
    """修改状态"""
    
    PENDING = auto()
    APPLIED = auto()
    FAILED = auto()
    REVERTED = auto()


@dataclass(frozen=True, slots=True)
class Defect:
    """缺陷模型
    
    表示系统中发现的缺陷信息
    
    Attributes:
        defect_id: 缺陷唯一标识符
        component: 缺陷所属组件
        description: 缺陷详细描述
        severity: 缺陷严重程度 (0.0-1.0)
        related_code: 关联代码路径
        detected_at: 检测时间戳 (Unix time)
        metadata: 额外元数据
    """
    defect_id: str = ""
    component: str = ""
    description: str = ""
    severity: float = 0.0
    related_code: Optional[str] = None
    detected_at: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )


@dataclass(frozen=True, slots=True)
class Modification:
    """修改模型
    
    表示代码修改记录
    
    Attributes:
        modification_id: 修改唯一标识符
        action: 进化动作类型
        component: 修改所属组件
        description: 修改详细描述
        content: 修改内容
        created_at: 创建时间戳 (Unix time)
        applied_at: 应用时间戳 (Unix time)
        status: 修改状态
        metadata: 额外元数据
    """
    modification_id: str = ""
    action: EvolutionActionType = EvolutionActionType.MODIFY
    component: str = ""
    description: str = ""
    content: Dict[str, Any] = field(
        default_factory=dict,
        repr=False
    )
    created_at: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    applied_at: Optional[float] = None
    status: ModificationStatus = ModificationStatus.PENDING
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """状态快照
    
    保存系统状态的时间点快照
    
    Attributes:
        snapshot_id: 快照唯一标识符
        version: 版本号
        state_data: 状态数据
        created_at: 创建时间戳 (Unix time)
        reason: 创建原因
        metadata: 额外元数据
    """
    snapshot_id: str = ""
    version: str = ""
    state_data: Dict[str, Any] = field(
        default_factory=dict,
        repr=False
    )
    created_at: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    reason: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )


@dataclass(frozen=True, slots=True)
class EvolutionAction:
    """进化动作
    
    表示待执行的进化操作
    
    Attributes:
        action_id: 动作唯一标识符
        action_type: 动作类型
        target_component: 目标组件
        description: 动作描述
        parameters: 动作参数
        created_at: 创建时间戳 (Unix time)
        priority: 优先级 (0.0-1.0)
        metadata: 额外元数据
    """
    action_id: str = ""
    action_type: EvolutionActionType = EvolutionActionType.MODIFY
    target_component: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(
        default_factory=dict,
        repr=False
    )
    created_at: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    priority: float = 0.5
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )


@dataclass(frozen=True, slots=True)
class EvolutionRecord:
    """进化记录
    
    记录完整的进化过程
    
    Attributes:
        record_id: 记录唯一标识符
        task_id: 任务标识符
        task_description: 任务描述
        start_time: 开始时间戳 (Unix time)
        end_time: 结束时间戳 (Unix time)
        success: 是否成功
        defects: 发现的缺陷列表
        modifications: 执行的修改列表
        state_before: 进化前状态快照
        state_after: 进化后状态快照
        error_message: 错误信息
        utility_improvement: 效用提升值
        metadata: 额外元数据
    """
    record_id: str = ""
    task_id: str = ""
    task_description: str = ""
    start_time: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    end_time: Optional[float] = None
    success: bool = False
    defects: List[Defect] = field(default_factory=list)
    modifications: List[Modification] = field(default_factory=list)
    state_before: Optional[StateSnapshot] = None
    state_after: Optional[StateSnapshot] = None
    error_message: Optional[str] = None
    utility_improvement: float = 0.0
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )

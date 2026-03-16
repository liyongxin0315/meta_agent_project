"""
系统状态数据模型
定义系统状态、版本信息、资源使用等数据结构
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class SystemStatus(Enum):
    """系统状态枚举"""
    
    RUNNING = auto()
    STOPPED = auto()
    ERROR = auto()
    INITIALIZING = auto()


class SecurityStatus(Enum):
    """安全状态枚举"""
    
    NORMAL = auto()
    WARNING = auto()
    CRITICAL = auto()


class LearningStatus(Enum):
    """学习状态枚举"""
    
    DISABLED = auto()
    ENABLED = auto()
    TRAINING = auto()
    PAUSED = auto()


@dataclass(frozen=True, slots=True)
class VersionInfo:
    """版本信息
    
    包含当前版本、最新演化版本、演化次数和最后演化时间
    
    Attributes:
        current_version: 当前系统版本号 (语义化版本格式)
        latest_evolution_version: 最新演化版本号
        evolution_count: 累计演化次数
        last_evolution_time: 最后一次演化的时间戳 (Unix time)
    """
    current_version: str = "1.0.0"
    latest_evolution_version: str = "1.0.0"
    evolution_count: int = 0
    last_evolution_time: Optional[float] = None


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    """资源使用情况
    
    记录 CPU、内存、磁盘、网络 I/O 等资源使用指标
    
    Attributes:
        cpu: CPU 使用率 (0.0-1.0)
        memory: 内存使用率 (0.0-1.0)
        disk: 磁盘使用率 (0.0-1.0)
        network_io: 网络 I/O 速率 (字节/秒)
        timestamp: 记录时间戳 (Unix time)
    """
    cpu: float = 0.0
    memory: float = 0.0
    disk: float = 0.0
    network_io: float = 0.0
    timestamp: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )


@dataclass(frozen=True, slots=True)
class SystemState:
    """系统状态
    
    完整的系统状态数据结构，包含运行状态、版本信息、资源使用等
    
    Attributes:
        status: 系统运行状态
        version_info: 版本信息
        resource_usage: 资源使用情况
        utility_score: 系统效用评分 (0.0-1.0)
        security_status: 安全状态
        learning_status: 学习状态
        last_updated: 最后更新时间戳 (Unix time)
        uptime: 系统运行时长
        metadata: 额外元数据
    """
    status: SystemStatus = SystemStatus.RUNNING
    version_info: VersionInfo = field(default_factory=VersionInfo)
    resource_usage: ResourceUsage = field(default_factory=ResourceUsage)
    utility_score: float = 0.0
    security_status: SecurityStatus = SecurityStatus.NORMAL
    learning_status: LearningStatus = LearningStatus.DISABLED
    last_updated: float = field(
        default_factory=lambda: datetime.now().timestamp(),
        repr=False
    )
    uptime: timedelta = field(default_factory=lambda: timedelta(hours=0))
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        repr=False,
        compare=False
    )

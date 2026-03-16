"""
状态管理器 - 核心实现
管理系统状态和状态快照
"""

import threading
from datetime import datetime
from typing import Any, Dict, Optional

from meta_agent.core.interfaces import IStateManager
from meta_agent.core.logging import get_logger
from meta_agent.models.state import (
    SystemState,
    VersionInfo,
    ResourceUsage,
    SystemStatus,
    SecurityStatus,
    LearningStatus,
)
from meta_agent.models.evolution import StateSnapshot

logger = get_logger(__name__)


class StateManager(IStateManager):
    """状态管理器
    
    管理系统状态和状态快照
    """
    
    def __init__(self, initial_state: Optional[SystemState] = None) -> None:
        """初始化状态管理器
        
        Args:
            initial_state: 初始系统状态
        """
        self._state: SystemState = initial_state or SystemState()
        self._snapshots: Dict[str, StateSnapshot] = {}
        self._lock = threading.RLock()
        self._start_time: float = datetime.now().timestamp()
        logger.info("状态管理器初始化完成")
    
    def get_current_state(self) -> SystemState:
        """获取当前系统状态
        
        Returns:
            当前系统状态
        """
        with self._lock:
            current_uptime = datetime.now().timestamp() - self._start_time
            from datetime import timedelta
            
            if self._state.uptime.total_seconds() != current_uptime:
                updated_state = SystemState(
                    status=self._state.status,
                    version_info=self._state.version_info,
                    resource_usage=self._state.resource_usage,
                    utility_score=self._state.utility_score,
                    security_status=self._state.security_status,
                    learning_status=self._state.learning_status,
                    last_updated=datetime.now().timestamp(),
                    uptime=timedelta(seconds=current_uptime),
                    metadata=self._state.metadata
                )
                self._state = updated_state
            
            return self._state
    
    def create_snapshot(
        self,
        reason: str,
        version: str
    ) -> StateSnapshot:
        """创建状态快照
        
        Args:
            reason: 创建快照的原因
            version: 版本号
            
        Returns:
            创建的状态快照
        """
        with self._lock:
            current_state = self.get_current_state()
            snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            state_data = {
                "status": current_state.status.name,
                "utility_score": current_state.utility_score,
                "security_status": current_state.security_status.name,
                "learning_status": current_state.learning_status.name,
                "version_info": {
                    "current_version": current_state.version_info.current_version,
                    "latest_evolution_version": current_state.version_info.latest_evolution_version,
                    "evolution_count": current_state.version_info.evolution_count,
                },
                "resource_usage": {
                    "cpu": current_state.resource_usage.cpu,
                    "memory": current_state.resource_usage.memory,
                    "disk": current_state.resource_usage.disk,
                    "network_io": current_state.resource_usage.network_io,
                },
                "uptime_seconds": current_state.uptime.total_seconds(),
            }
            
            snapshot = StateSnapshot(
                snapshot_id=snapshot_id,
                version=version,
                state_data=state_data,
                created_at=datetime.now().timestamp(),
                reason=reason
            )
            
            self._snapshots[snapshot_id] = snapshot
            logger.info(f"状态快照已创建: {snapshot_id}, 原因: {reason}")
            
            return snapshot
    
    def update_state(
        self,
        status: Optional[SystemStatus] = None,
        utility_score: Optional[float] = None,
        security_status: Optional[SecurityStatus] = None,
        learning_status: Optional[LearningStatus] = None,
        resource_usage: Optional[ResourceUsage] = None,
        version_info: Optional[VersionInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """更新系统状态
        
        Args:
            status: 系统状态
            utility_score: 效用评分
            security_status: 安全状态
            learning_status: 学习状态
            resource_usage: 资源使用情况
            version_info: 版本信息
            metadata: 额外元数据
        """
        with self._lock:
            new_metadata = dict(self._state.metadata)
            if metadata:
                new_metadata.update(metadata)
            
            self._state = SystemState(
                status=status or self._state.status,
                version_info=version_info or self._state.version_info,
                resource_usage=resource_usage or self._state.resource_usage,
                utility_score=utility_score if utility_score is not None else self._state.utility_score,
                security_status=security_status or self._state.security_status,
                learning_status=learning_status or self._state.learning_status,
                last_updated=datetime.now().timestamp(),
                uptime=self._state.uptime,
                metadata=new_metadata
            )
            
            logger.debug("系统状态已更新")
    
    def get_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """获取指定的状态快照
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            状态快照，如果不存在则返回 None
        """
        with self._lock:
            return self._snapshots.get(snapshot_id)
    
    def list_snapshots(self) -> Dict[str, StateSnapshot]:
        """列出所有状态快照
        
        Returns:
            状态快照字典
        """
        with self._lock:
            return self._snapshots.copy()
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除指定的状态快照
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            是否删除成功
        """
        with self._lock:
            if snapshot_id in self._snapshots:
                del self._snapshots[snapshot_id]
                logger.info(f"状态快照已删除: {snapshot_id}")
                return True
            return False

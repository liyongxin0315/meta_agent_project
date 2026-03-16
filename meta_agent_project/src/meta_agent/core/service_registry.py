"""
服务注册表 - 企业级实现
提供服务发现、注册和查询功能
"""

import threading
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    REGISTERED = auto()
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    DEGRADED = auto()


@dataclass
class ServiceMetadata:
    """服务元数据"""
    service_type: Type[Any]
    implementation_type: Optional[Type[Any]]
    status: ServiceStatus = ServiceStatus.REGISTERED
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: float = 0.0
    last_heartbeat: float = 0.0


class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self):
        self._services: Dict[str, ServiceMetadata] = {}
        self._lock = threading.RLock()
        self._listeners: List[Callable[[str, ServiceStatus, Optional[ServiceStatus]], None]] = []
    
    def register(
        self,
        name: str,
        service_type: Type[Any],
        implementation_type: Optional[Type[Any]] = None,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """注册服务"""
        with self._lock:
            if name in self._services:
                logger.warning(f"服务已存在，将被覆盖: {name}")
            
            now = datetime.now(timezone.utc).timestamp()
            service_meta = ServiceMetadata(
                service_type=service_type,
                implementation_type=implementation_type or service_type,
                status=ServiceStatus.AVAILABLE,
                version=version,
                tags=tags or [],
                metadata=metadata or {},
                registered_at=now,
                last_heartbeat=now,
            )
            
            self._services[name] = service_meta
            logger.info(f"服务注册成功: {name}")
    
    def unregister(self, name: str) -> bool:
        """注销服务"""
        with self._lock:
            if name not in self._services:
                logger.warning(f"服务不存在，无法注销: {name}")
                return False
            
            old_status = self._services[name].status
            del self._services[name]
            logger.info(f"服务注销成功: {name}")
            self._notify_listeners(name, old_status, None)
            return True
    
    def get(self, name: str) -> Optional[ServiceMetadata]:
        """获取服务"""
        with self._lock:
            return self._services.get(name)
    
    def get_by_type(self, service_type: Type[Any]) -> List[ServiceMetadata]:
        """按类型获取服务"""
        with self._lock:
            return [
                meta for meta in self._services.values()
                if issubclass(meta.service_type, service_type)
            ]
    
    def get_by_tag(self, tag: str) -> List[ServiceMetadata]:
        """按标签获取服务"""
        with self._lock:
            return [
                meta for meta in self._services.values()
                if tag in meta.tags
            ]
    
    def update_status(self, name: str, status: ServiceStatus) -> bool:
        """更新服务状态"""
        with self._lock:
            if name not in self._services:
                logger.warning(f"服务不存在，无法更新状态: {name}")
                return False
            
            old_status = self._services[name].status
            self._services[name].status = status
            self._services[name].last_heartbeat = datetime.now(timezone.utc).timestamp()
            logger.info(f"服务状态更新: {name} {old_status.name} -> {status.name}")
            self._notify_listeners(name, old_status, status)
            return True
    
    def heartbeat(self, name: str) -> bool:
        """服务心跳"""
        with self._lock:
            if name not in self._services:
                return False
            self._services[name].last_heartbeat = datetime.now(timezone.utc).timestamp()
            return True
    
    def list_all(self) -> Dict[str, ServiceMetadata]:
        """列出所有服务"""
        with self._lock:
            return self._services.copy()
    
    def add_listener(
        self,
        listener: Callable[[str, ServiceStatus, Optional[ServiceStatus]], None],
    ) -> None:
        """添加状态变化监听器"""
        with self._lock:
            self._listeners.append(listener)
    
    def remove_listener(
        self,
        listener: Callable[[str, ServiceStatus, Optional[ServiceStatus]], None],
    ) -> None:
        """移除状态变化监听器"""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)
    
    def _notify_listeners(
        self,
        name: str,
        old_status: ServiceStatus,
        new_status: Optional[ServiceStatus],
    ) -> None:
        """通知监听器"""
        for listener in self._listeners:
            try:
                listener(name, old_status, new_status)
            except Exception as e:
                logger.error(f"监听器执行失败: {e}")


# 全局服务注册表实例
service_registry = ServiceRegistry()

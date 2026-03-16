"""
事件总线 - 企业级实现
提供事件发布/订阅机制，支持同步和异步处理
"""

import threading
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from enum import Enum
from queue import Queue

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class EventPriority(Enum):
    """事件优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    priority: EventPriority = EventPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "priority": self.priority.name,
            "metadata": self.metadata,
            "event_type": self.__class__.__name__,
        }


@dataclass
class EvolutionStartedEvent(DomainEvent):
    """进化开始事件"""
    task_id: str = ""
    task_description: str = ""


@dataclass
class EvolutionCompletedEvent(DomainEvent):
    """进化完成事件"""
    task_id: str = ""
    success: bool = False
    duration_seconds: float = 0.0
    result: Optional[Dict[str, Any]] = None


@dataclass
class DefectDetectedEvent(DomainEvent):
    """缺陷检测事件"""
    component: str = ""
    defect_description: str = ""
    severity: float = 0.0


@dataclass
class ComponentHotloadedEvent(DomainEvent):
    """组件热加载事件"""
    component_name: str = ""
    component_path: str = ""
    old_version: str = ""
    new_version: str = ""


class EventHandler(ABC):
    """事件处理器抽象基类"""
    
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """处理事件"""


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self._lock = threading.RLock()
        self._event_queue: Queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
    
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: Callable[[DomainEvent], None],
    ) -> None:
        """订阅事件"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
            logger.debug(f"订阅事件: {event_type.__name__}")
    
    def unsubscribe(
        self,
        event_type: Type[DomainEvent],
        handler: Callable[[DomainEvent], None],
    ) -> bool:
        """取消订阅"""
        with self._lock:
            if event_type not in self._subscribers:
                return False
            if handler not in self._subscribers[event_type]:
                return False
            self._subscribers[event_type].remove(handler)
            logger.debug(f"取消订阅事件: {event_type.__name__}")
            return True
    
    def publish(self, event: DomainEvent) -> None:
        """发布事件（同步）"""
        logger.debug(f"发布事件: {event.__class__.__name__}, id={event.event_id}")
        
        with self._lock:
            event_type = type(event)
            handlers = self._subscribers.get(event_type, [])
            
            for base_type in event_type.__bases__:
                if issubclass(base_type, DomainEvent):
                    handlers.extend(self._subscribers.get(base_type, []))
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"事件处理失败: {e}")
    
    def publish_async(self, event: DomainEvent) -> None:
        """发布事件（异步）"""
        self._event_queue.put(event)
        if not self._running:
            self._start_worker()
    
    def _start_worker(self) -> None:
        """启动工作线程"""
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def _worker_loop(self) -> None:
        """工作线程循环"""
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
                self.publish(event)
            except Exception:
                continue
    
    def stop(self) -> None:
        """停止事件总线"""
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
    
    def clear(self) -> None:
        """清除所有订阅"""
        with self._lock:
            self._subscribers.clear()


# 全局事件总线实例
event_bus = EventBus()

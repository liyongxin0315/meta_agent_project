"""
依赖注入容器 - 核心实现
"""

import inspect
import threading
from typing import (
    Any,
    Dict,
    Optional,
    Type,
    TypeVar,
    Callable,
)
from enum import Enum, auto
from dataclasses import dataclass, field
from contextlib import contextmanager

from meta_agent.core.logging import get_logger
from meta_agent.core.exceptions import DependencyInjectionError

logger = get_logger(__name__)

T = TypeVar('T')


class Lifetime(Enum):
    """服务生命周期枚举"""
    TRANSIENT = auto()
    SCOPED = auto()
    SINGLETON = auto()


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type[Any]
    implementation_type: Optional[Type[Any]] = None
    instance: Optional[Any] = None
    factory: Optional[Callable[..., Any]] = None
    lifetime: Lifetime = Lifetime.TRANSIENT
    metadata: Dict[str, Any] = field(default_factory=dict)


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._descriptors: Dict[Type[Any], ServiceDescriptor] = {}
        self._singleton_instances: Dict[Type[Any], Any] = {}
        self._lock = threading.RLock()
    
    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[Any]] = None
    ) -> 'DIContainer':
        """注册瞬态服务"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type or service_type,
            lifetime=Lifetime.TRANSIENT
        )
        with self._lock:
            self._descriptors[service_type] = descriptor
        return self
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[Any]] = None
    ) -> 'DIContainer':
        """注册作用域服务"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type or service_type,
            lifetime=Lifetime.SCOPED
        )
        with self._lock:
            self._descriptors[service_type] = descriptor
        return self
    
    def register_singleton(
        self,
        service_type: Type[T],
        implementation_or_instance: Any = None
    ) -> 'DIContainer':
        """注册单例服务"""
        if isinstance(implementation_or_instance, type):
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_or_instance,
                lifetime=Lifetime.SINGLETON
            )
        else:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                instance=implementation_or_instance,
                lifetime=Lifetime.SINGLETON
            )
        with self._lock:
            self._descriptors[service_type] = descriptor
        return self
    
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """获取服务"""
        with self._lock:
            descriptor = self._descriptors.get(service_type)
            if not descriptor:
                return None
            
            if descriptor.lifetime == Lifetime.SINGLETON:
                if descriptor.instance:
                    return descriptor.instance
                if service_type not in self._singleton_instances:
                    instance = self._create_instance(descriptor)
                    self._singleton_instances[service_type] = instance
                return self._singleton_instances[service_type]
            
            return self._create_instance(descriptor)
    
    def get_required_service(self, service_type: Type[T]) -> T:
        """获取必需服务"""
        service = self.get_service(service_type)
        if service is None:
            raise DependencyInjectionError(f"服务未注册: {service_type}")
        return service
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        if descriptor.factory:
            return descriptor.factory(self)
        
        impl_type = descriptor.implementation_type
        if not impl_type:
            raise DependencyInjectionError("缺少实现类型")
        
        constructor = inspect.signature(impl_type.__init__)
        params = list(constructor.parameters.values())[1:]
        
        dependencies = []
        for param in params:
            if param.annotation == inspect.Parameter.empty:
                raise DependencyInjectionError(f"参数缺少类型注解: {param.name}")
            dep = self.get_required_service(param.annotation)
            dependencies.append(dep)
        
        return impl_type(*dependencies)
    
    @contextmanager
    def create_scope(self):
        """创建作用域"""
        scope = ServiceScope(self)
        try:
            yield scope
        finally:
            scope.dispose()


class ServiceScope:
    """服务作用域"""
    
    def __init__(self, container: DIContainer):
        self._container = container
        self._scoped_instances: Dict[Type[Any], Any] = {}
        self._disposed = False
        self._lock = threading.RLock()
    
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """从当前作用域获取服务"""
        if self._disposed:
            raise RuntimeError("ServiceScope已被释放")
        
        with self._lock:
            descriptor = self._container._descriptors.get(service_type)
            if not descriptor:
                return None
            
            if descriptor.lifetime == Lifetime.SCOPED:
                if service_type not in self._scoped_instances:
                    instance = self._container._create_instance(descriptor)
                    self._scoped_instances[service_type] = instance
                return self._scoped_instances[service_type]
            
            return self._container.get_service(service_type)
    
    def dispose(self):
        """释放作用域"""
        self._disposed = True
        self._scoped_instances.clear()


# 全局容器实例
container = DIContainer()

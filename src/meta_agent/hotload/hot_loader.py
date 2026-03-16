"""
热加载器 - 核心实现
"""

import importlib
import importlib.util
import sys
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LoadedComponent:
    """已加载组件"""
    name: str
    module_name: str
    module_path: Path
    component_type: Type[Any]
    instance: Optional[Any] = None
    loaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class HotLoader:
    """组件热加载器"""
    
    def __init__(self, watch_dirs: Optional[List[Path]] = None):
        self._components: Dict[str, LoadedComponent] = {}
        self._watch_dirs = watch_dirs or []
        self._lock = threading.RLock()
        self._module_cache: Dict[str, Any] = {}
    
    def load_component(
        self,
        component_path: Path,
        component_name: Optional[str] = None,
        autoload: bool = True
    ) -> LoadedComponent:
        """
        加载组件
        
        Args:
            component_path: 组件文件路径
            component_name: 组件名称
            autoload: 是否自动实例化
            
        Returns:
            LoadedComponent: 加载的组件
        """
        with self._lock:
            if not component_path.exists():
                raise FileNotFoundError(f"组件文件不存在: {component_path}")
            
            if component_path.suffix != ".py":
                raise ValueError(f"组件必须是Python文件: {component_path}")
            
            module_name = component_path.stem
            name = component_name or module_name
            
            if name in self._components:
                logger.warning(f"组件已存在，将被覆盖: {name}")
            
            spec = importlib.util.spec_from_file_location(module_name, component_path)
            if not spec or not spec.loader:
                raise ImportError(f"无法加载模块: {component_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            component_class = self._find_component_class(module)
            if not component_class:
                raise ImportError(f"未找到组件类: {component_path}")
            
            instance = None
            if autoload:
                instance = self._instantiate_component(component_class)
            
            loaded_component = LoadedComponent(
                name=name,
                module_name=module_name,
                module_path=component_path,
                component_type=component_class,
                instance=instance
            )
            
            self._components[name] = loaded_component
            self._module_cache[module_name] = module
            
            logger.info(f"组件加载成功: {name} from {component_path}")
            return loaded_component
    
    def _find_component_class(self, module: Any) -> Optional[Type[Any]]:
        """从模块中查找组件类"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, '__is_component__') or name.endswith('Component'):
                return obj
        
        classes = [obj for _, obj in inspect.getmembers(module, inspect.isclass)]
        if classes:
            return classes[0]
        
        return None
    
    def _instantiate_component(self, component_class: Type[Any]) -> Any:
        """实例化组件"""
        try:
            constructor = inspect.signature(component_class.__init__)
            params = list(constructor.parameters.values())[1:]
            
            if not params:
                return component_class()
            
            dependencies = []
            for param in params:
                if hasattr(param.annotation, '__name__'):
                    dep_name = param.annotation.__name__.lower()
                    if dep_name in self._components:
                        dependencies.append(self._components[dep_name].instance)
                    else:
                        dependencies.append(None)
                else:
                    dependencies.append(None)
            
            return component_class(*dependencies)
            
        except Exception as e:
            logger.error(f"组件实例化失败: {e}")
            raise
    
    def reload_component(self, component_name: str) -> LoadedComponent:
        """
        重新加载组件
        
        Args:
            component_name: 组件名称
            
        Returns:
            LoadedComponent: 重新加载的组件
        """
        with self._lock:
            if component_name not in self._components:
                raise ValueError(f"组件不存在: {component_name}")
            
            component = self._components[component_name]
            logger.info(f"重新加载组件: {component_name}")
            
            return self.load_component(
                component_path=component.module_path,
                component_name=component_name,
                autoload=True
            )
    
    def unload_component(self, component_name: str) -> bool:
        """
        卸载组件
        
        Args:
            component_name: 组件名称
            
        Returns:
            bool: 是否成功卸载
        """
        with self._lock:
            if component_name not in self._components:
                logger.warning(f"组件不存在，无法卸载: {component_name}")
                return False
            
            component = self._components[component_name]
            
            if component.module_name in sys.modules:
                del sys.modules[component.module_name]
            
            if component.module_name in self._module_cache:
                del self._module_cache[component.module_name]
            
            del self._components[component_name]
            
            logger.info(f"组件卸载成功: {component_name}")
            return True
    
    def get_component(self, component_name: str) -> Optional[LoadedComponent]:
        """获取组件"""
        with self._lock:
            return self._components.get(component_name)
    
    def get_component_instance(self, component_name: str) -> Optional[Any]:
        """获取组件实例"""
        component = self.get_component(component_name)
        return component.instance if component else None
    
    def list_components(self) -> List[Dict[str, Any]]:
        """列出所有组件"""
        with self._lock:
            return [
                {
                    "name": comp.name,
                    "module_path": str(comp.module_path),
                    "loaded_at": comp.loaded_at.isoformat(),
                    "version": comp.version,
                    "has_instance": comp.instance is not None
                }
                for comp in self._components.values()
            ]


# 全局热加载器实例
hot_loader = HotLoader()


def component(cls: Type[Any]) -> Type[Any]:
    """组件装饰器"""
    cls.__is_component__ = True
    return cls

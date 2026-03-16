"""
动态注册表 - 企业级实现
管理动态加载的组件，支持版本管理和回滚
"""

import threading
import importlib
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ComponentVersion:
    """组件版本"""
    version: str
    component_path: Path
    component_type_name: str
    component_module_name: str
    loaded_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False


@dataclass
class RegisteredComponent:
    """已注册组件"""
    name: str
    component_type: Type[Any]
    current_version: str
    versions: Dict[str, ComponentVersion] = field(default_factory=dict)
    instance: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DynamicRegistry:
    """动态注册表"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self._components: Dict[str, RegisteredComponent] = {}
        self._lock = threading.Lock()
        self._storage_path = storage_path or Path("./data/component_registry.json")
        self._load_from_storage()
    
    def register(
        self,
        name: str,
        component_type: Type[Any],
        version: str,
        component_path: Path,
        instance: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """注册组件"""
        with self._lock:
            now = datetime.now(timezone.utc).timestamp()
            
            if name not in self._components:
                self._components[name] = RegisteredComponent(
                    name=name,
                    component_type=component_type,
                    current_version=version,
                    metadata=metadata or {},
                )
            
            component = self._components[name]
            
            component_version = ComponentVersion(
                version=version,
                component_path=component_path,
                component_type_name=component_type.__name__,
                component_module_name=component_type.__module__,
                loaded_at=now,
                metadata=metadata or {},
                is_active=True,
            )
            
            for ver in component.versions.values():
                ver.is_active = False
            
            component.versions[version] = component_version
            component.current_version = version
            component.instance = instance
            
            logger.info(f"组件注册成功: {name} v{version}")
            self._save_to_storage()
    
    def unregister(self, name: str) -> bool:
        """注销组件"""
        with self._lock:
            if name not in self._components:
                logger.warning(f"组件不存在，无法注销: {name}")
                return False
            
            del self._components[name]
            logger.info(f"组件注销成功: {name}")
            self._save_to_storage()
            return True
    
    def get(self, name: str) -> Optional[RegisteredComponent]:
        """获取组件"""
        with self._lock:
            return self._components.get(name)
    
    def get_instance(self, name: str) -> Optional[Any]:
        """获取组件实例"""
        with self._lock:
            component = self._components.get(name)
            return component.instance if component else None
    
    def get_version(self, name: str, version: str) -> Optional[ComponentVersion]:
        """获取组件指定版本"""
        with self._lock:
            component = self._components.get(name)
            return component.versions.get(version) if component else None
    
    def list_versions(self, name: str) -> List[str]:
        """列出组件所有版本"""
        with self._lock:
            component = self._components.get(name)
            return list(component.versions.keys()) if component else []
    
    def rollback(self, name: str, version: str) -> bool:
        """回滚到指定版本"""
        with self._lock:
            component = self._components.get(name)
            if not component:
                logger.warning(f"组件不存在，无法回滚: {name}")
                return False
            
            if version not in component.versions:
                logger.warning(f"版本不存在，无法回滚: {name} v{version}")
                return False
            
            for ver in component.versions.values():
                ver.is_active = False
            
            component.versions[version].is_active = True
            component.current_version = version
            
            logger.info(f"组件回滚成功: {name} v{version}")
            self._save_to_storage()
            return True
    
    def list_all(self) -> Dict[str, RegisteredComponent]:
        """列出所有组件"""
        with self._lock:
            return self._components.copy()
    
    def _save_to_storage(self) -> None:
        """保存到存储"""
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for name, component in self._components.items():
                data[name] = {
                    "name": component.name,
                    "component_type": component.component_type.__name__,
                    "component_module": component.component_type.__module__,
                    "current_version": component.current_version,
                    "metadata": component.metadata,
                    "versions": {
                        ver: {
                            "version": cv.version,
                            "component_path": str(cv.component_path),
                            "component_type_name": cv.component_type_name,
                            "component_module_name": cv.component_module_name,
                            "loaded_at": cv.loaded_at,
                            "metadata": cv.metadata,
                            "is_active": cv.is_active,
                        }
                        for ver, cv in component.versions.items()
                    },
                }
            
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"保存组件注册表失败: {e}")
    
    def _load_from_storage(self) -> None:
        """从存储加载"""
        if not self._storage_path.exists():
            return
        
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.info(f"从存储加载了 {len(data)} 个组件记录")
            
            for name, component_data in data.items():
                try:
                    module_name = component_data.get("component_module")
                    type_name = component_data.get("component_type")
                    
                    if module_name and type_name:
                        module = importlib.import_module(module_name)
                        component_type = getattr(module, type_name)
                        
                        current_version = component_data.get("current_version")
                        versions = component_data.get("versions", {})
                        
                        registered_component = RegisteredComponent(
                            name=name,
                            component_type=component_type,
                            current_version=current_version,
                            metadata=component_data.get("metadata", {}),
                        )
                        
                        for ver, ver_data in versions.items():
                            component_version = ComponentVersion(
                                version=ver,
                                component_path=Path(ver_data.get("component_path")),
                                component_type_name=ver_data.get("component_type_name"),
                                component_module_name=ver_data.get("component_module_name"),
                                loaded_at=ver_data.get("loaded_at"),
                                metadata=ver_data.get("metadata", {}),
                                is_active=ver_data.get("is_active", False),
                            )
                            registered_component.versions[ver] = component_version
                        
                        self._components[name] = registered_component
                        logger.info(f"组件恢复成功: {name}")
                
                except Exception as e:
                    logger.warning(f"恢复组件失败: {name}, error={e}")
        
        except Exception as e:
            logger.error(f"加载组件注册表失败: {e}")


# 全局动态注册表实例
dynamic_registry = DynamicRegistry()

"""
MetaAgent 主入口
启动和管理 MetaAgent 系统
"""

from typing import Optional

from meta_agent import __version__
from meta_agent.agent import MetaAgent
from meta_agent.core import (
    Config,
    get_config,
    container,
    service_registry,
    StateManager,
    IStateManager,
    get_logger,
)

logger = get_logger(__name__)


class MetaAgentSystem:
    """MetaAgent 系统
    
    完整的 MetaAgent 系统管理
    """
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """初始化 MetaAgent 系统
        
        Args:
            config: 系统配置
        """
        self.config = config or get_config()
        self._agent: Optional[MetaAgent] = None
        self._state_manager: Optional[StateManager] = None
        self._initialized = False
        
        logger.info(f"MetaAgent 系统 v{__version__} 初始化中...")
    
    def initialize(self) -> None:
        """初始化系统"""
        if self._initialized:
            logger.warning("系统已经初始化")
            return
        
        logger.info("开始初始化系统组件...")
        
        self._state_manager = StateManager()
        container.register_singleton(IStateManager, self._state_manager)
        
        service_registry.register(
            name="state_manager",
            service_type=IStateManager,
            implementation_type=StateManager,
            version="1.0.0",
            tags=["core", "state"]
        )
        
        self._agent = MetaAgent(config=self.config)
        container.register_singleton(MetaAgent, self._agent)
        
        service_registry.register(
            name="meta_agent",
            service_type=MetaAgent,
            version="1.0.0",
            tags=["core", "agent"]
        )
        
        self._initialized = True
        logger.info("系统初始化完成")
    
    def start(self) -> None:
        """启动系统"""
        if not self._initialized:
            self.initialize()
        
        if self._agent:
            self._agent.run()
        
        if self._state_manager:
            self._state_manager.update_state(status=self._state_manager.get_current_state().status)
        
        logger.info("MetaAgent 系统已启动")
    
    def stop(self) -> None:
        """停止系统"""
        if self._agent and self._agent.is_running:
            self._agent.stop()
        
        if self._state_manager:
            self._state_manager.update_state(
                status=self._state_manager.get_current_state().status
            )
        
        logger.info("MetaAgent 系统已停止")
    
    def get_status(self) -> dict:
        """获取系统状态
        
        Returns:
            系统状态字典
        """
        if not self._state_manager:
            return {"status": "not_initialized"}
        
        state = self._state_manager.get_current_state()
        return {
            "version": __version__,
            "initialized": self._initialized,
            "agent_running": self._agent.is_running if self._agent else False,
            "system_status": state.status.name,
            "utility_score": state.utility_score,
            "security_status": state.security_status.name,
            "uptime_seconds": state.uptime.total_seconds(),
        }
    
    def create_snapshot(self, reason: str, version: str) -> dict:
        """创建状态快照
        
        Args:
            reason: 快照原因
            version: 版本号
            
        Returns:
            快照信息字典
        """
        if not self._state_manager:
            raise RuntimeError("系统未初始化")
        
        snapshot = self._state_manager.create_snapshot(reason=reason, version=version)
        return {
            "snapshot_id": snapshot.snapshot_id,
            "version": snapshot.version,
            "reason": snapshot.reason,
            "created_at": snapshot.created_at,
        }
    
    @property
    def agent(self) -> Optional[MetaAgent]:
        """获取 MetaAgent 实例"""
        return self._agent
    
    @property
    def state_manager(self) -> Optional[StateManager]:
        """获取状态管理器实例"""
        return self._state_manager


_global_system: Optional[MetaAgentSystem] = None


def get_system() -> MetaAgentSystem:
    """获取全局系统实例
    
    Returns:
        MetaAgent 系统实例
    """
    global _global_system
    if _global_system is None:
        _global_system = MetaAgentSystem()
    return _global_system


def set_system(system: MetaAgentSystem) -> None:
    """设置全局系统实例
    
    Args:
        system: MetaAgent 系统实例
    """
    global _global_system
    _global_system = system


if __name__ == "__main__":
    import sys
    
    system = get_system()
    system.initialize()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print("系统状态:")
        for key, value in system.get_status().items():
            print(f"  {key}: {value}")
    else:
        print(f"MetaAgent 系统 v{__version__}")
        print("使用 'python -m meta_agent.main status' 查看状态")

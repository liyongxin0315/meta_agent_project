"""
MetaAgent 主类
系统的核心控制器
"""

from typing import Optional
from datetime import datetime

from meta_agent.core.config import Config
from meta_agent.core.logging import get_logger
from meta_agent.models.state import SystemState, SystemStatus

logger = get_logger(__name__)


class MetaAgent:
    """MetaAgent 主类
    
    系统的核心控制器，负责管理系统状态、协调各模块工作
    
    Attributes:
        config: 系统配置
        _state: 当前系统状态
        _start_time: 启动时间戳
        _is_running: 运行状态标志
    """
    
    def __init__(self, config: Config) -> None:
        """初始化 MetaAgent
        
        Args:
            config: 系统配置对象
        """
        self.config = config
        self._state: Optional[SystemState] = None
        self._start_time: Optional[float] = None
        self._is_running: bool = False
        logger.info("MetaAgent 初始化完成")
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"MetaAgent(is_running={self._is_running})"
    
    def run(self) -> None:
        """运行 MetaAgent
        
        启动系统并初始化状态
        """
        if self._is_running:
            logger.warning("MetaAgent 已经在运行中")
            return
        
        logger.info("MetaAgent 开始运行")
        self._is_running = True
        self._start_time = datetime.now().timestamp()
        
        if self._state is None:
            self._state = SystemState(
                status=SystemStatus.RUNNING
            )
        
        logger.info("MetaAgent 运行中")
    
    def stop(self) -> None:
        """停止 MetaAgent
        
        停止系统并更新状态
        """
        if not self._is_running:
            logger.warning("MetaAgent 已经停止")
            return
        
        logger.info("MetaAgent 停止运行")
        self._is_running = False
        
        if self._state is not None:
            object.__setattr__(self._state, 'status', SystemStatus.STOPPED)
    
    def get_state(self) -> Optional[SystemState]:
        """获取当前系统状态
        
        Returns:
            当前系统状态对象，如果未初始化则返回 None
        """
        return self._state
    
    def set_state(self, state: SystemState) -> None:
        """设置系统状态
        
        Args:
            state: 新的系统状态对象
        """
        self._state = state
        logger.debug("系统状态已更新")
    
    @property
    def is_running(self) -> bool:
        """获取运行状态
        
        Returns:
            True 如果系统正在运行，否则 False
        """
        return self._is_running
    
    @property
    def uptime(self) -> Optional[float]:
        """获取运行时长
        
        Returns:
            运行时长（秒），如果未启动则返回 None
        """
        if self._start_time is None:
            return None
        return datetime.now().timestamp() - self._start_time

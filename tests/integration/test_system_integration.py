"""
系统集成测试
测试新增模块与主系统的集成
"""

import pytest
from datetime import timedelta

from meta_agent import MetaAgentSystem, get_system, set_system
from meta_agent.core import (
    container,
    service_registry,
    StateManager,
    IStateManager,
)
from meta_agent.models import (
    SystemState,
    SystemStatus,
    SecurityStatus,
    LearningStatus,
    Defect,
    StateSnapshot,
)
from meta_agent.agent import MetaAgent


@pytest.fixture
def clean_system():
    """清理全局系统实例"""
    set_system(None)
    yield
    set_system(None)


class TestMetaAgentSystem:
    """测试 MetaAgent 系统"""
    
    def test_system_initialization(self, clean_system):
        """测试系统初始化"""
        system = get_system()
        assert system is not None
        assert system.agent is None
        assert system.state_manager is None
    
    def test_system_initialize(self, clean_system):
        """测试系统初始化流程"""
        system = get_system()
        system.initialize()
        
        assert system.agent is not None
        assert system.state_manager is not None
        assert isinstance(system.agent, MetaAgent)
        assert isinstance(system.state_manager, StateManager)
    
    def test_system_start_stop(self, clean_system):
        """测试系统启动和停止"""
        system = get_system()
        system.initialize()
        
        system.start()
        assert system.agent.is_running
        
        system.stop()
        assert not system.agent.is_running
    
    def test_get_status(self, clean_system):
        """测试获取系统状态"""
        system = get_system()
        system.initialize()
        
        status = system.get_status()
        assert "version" in status
        assert "initialized" in status
        assert "agent_running" in status
        assert "system_status" in status
        assert status["initialized"] is True
    
    def test_create_snapshot(self, clean_system):
        """测试创建状态快照"""
        system = get_system()
        system.initialize()
        
        snapshot_info = system.create_snapshot(
            reason="test_snapshot",
            version="1.0.0"
        )
        
        assert "snapshot_id" in snapshot_info
        assert snapshot_info["reason"] == "test_snapshot"
        assert snapshot_info["version"] == "1.0.0"


class TestStateManagerIntegration:
    """测试状态管理器集成"""
    
    def test_state_manager_in_di_container(self, clean_system):
        """测试状态管理器在依赖注入容器中"""
        system = get_system()
        system.initialize()
        
        state_manager = container.get_service(IStateManager)
        assert state_manager is not None
        assert isinstance(state_manager, StateManager)
    
    def test_state_manager_in_service_registry(self, clean_system):
        """测试状态管理器在服务注册表中"""
        system = get_system()
        system.initialize()
        
        service_meta = service_registry.get("state_manager")
        assert service_meta is not None
        assert service_meta.service_type == IStateManager
    
    def test_update_system_state(self, clean_system):
        """测试更新系统状态"""
        system = get_system()
        system.initialize()
        
        state_manager = system.state_manager
        
        state_manager.update_state(
            utility_score=0.8,
            security_status=SecurityStatus.WARNING,
            learning_status=LearningStatus.ENABLED
        )
        
        current_state = state_manager.get_current_state()
        assert current_state.utility_score == 0.8
        assert current_state.security_status == SecurityStatus.WARNING
        assert current_state.learning_status == LearningStatus.ENABLED


class TestModelsIntegration:
    """测试数据模型集成"""
    
    def test_defect_model(self):
        """测试缺陷模型"""
        defect = Defect(
            defect_id="test_001",
            component="test_component",
            description="test_description",
            severity=0.5
        )
        
        assert defect.defect_id == "test_001"
        assert defect.component == "test_component"
        assert defect.description == "test_description"
        assert defect.severity == 0.5
    
    def test_system_state_model(self):
        """测试系统状态模型"""
        state = SystemState(
            status=SystemStatus.RUNNING,
            utility_score=0.9
        )
        
        assert state.status == SystemStatus.RUNNING
        assert state.utility_score == 0.9
        assert state.security_status == SecurityStatus.NORMAL
    
    def test_frozen_dataclasses(self):
        """测试数据类的不可变性"""
        state = SystemState()
        
        with pytest.raises(FrozenInstanceError):
            state.utility_score = 1.0


class TestAgentIntegration:
    """测试 Agent 集成"""
    
    def test_agent_with_config(self, clean_system):
        """测试 Agent 与配置集成"""
        system = get_system()
        system.initialize()
        
        agent = system.agent
        assert agent.config is not None
    
    def test_agent_state_management(self, clean_system):
        """测试 Agent 状态管理"""
        system = get_system()
        system.initialize()
        
        agent = system.agent
        assert agent.get_state() is None
        
        from meta_agent.models import SystemState
        new_state = SystemState()
        agent.set_state(new_state)
        
        assert agent.get_state() is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

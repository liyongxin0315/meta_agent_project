"""
测试配置与夹具
提供企业级测试基础设施，包含测试数据库、测试沙箱、Mock客户端等
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator, Optional
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from meta_agent.core.config import Config, EvolutionConfig, UtilityConfig
from meta_agent.core.logging import setup_logging, get_logger
from meta_agent.models.state import SystemState, VersionInfo, ResourceUsage
from meta_agent.agent.meta_agent import MetaAgent
from meta_agent.core.security import set_original_module_hashes

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def temp_project_root() -> Generator[Path, None, None]:
    """
    会话级临时项目根目录夹具
    
    Yields:
        Path: 临时项目根目录路径
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="metaagent_test_"))
    (temp_dir / "src" / "meta_agent").mkdir(parents=True, exist_ok=True)
    (temp_dir / "tests").mkdir(parents=True, exist_ok=True)
    (temp_dir / "config").mkdir(parents=True, exist_ok=True)
    (temp_dir / "data" / "logs").mkdir(parents=True, exist_ok=True)
    (temp_dir / "data" / "snapshots").mkdir(parents=True, exist_ok=True)
    
    yield temp_dir
    
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"清理临时目录失败: {e}")


@pytest.fixture(scope="function")
def temp_test_dir(temp_project_root: Path) -> Generator[Path, None, None]:
    """
    函数级临时测试目录夹具
    
    Args:
        temp_project_root: 会话级临时项目根目录
        
    Yields:
        Path: 函数级临时测试目录路径
    """
    test_dir = temp_project_root / f"test_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    yield test_dir
    
    try:
        shutil.rmtree(test_dir)
    except Exception as e:
        logger.warning(f"清理测试目录失败: {e}")


@pytest.fixture(scope="function")
def test_config() -> Config:
    """
    测试配置夹具
    
    Returns:
        Config: 测试用配置对象
    """
    return Config(
        evolution=EvolutionConfig(
            defect_threshold=0.8,
            min_gain_delta=0.01,
            max_retries=3,
            snapshot_history=5,
            sandbox_timeout=60,
            max_memory_mb=256,
            llm_learning_enabled=False
        ),
        utility=UtilityConfig(
            weights={
                "task_success": 0.5,
                "efficiency": 0.3,
                "resource_usage": 0.2
            },
            baseline_window=5
        ),
        log_level="DEBUG"
    )


@pytest.fixture(scope="function")
def test_system_state() -> SystemState:
    """
    测试系统状态夹具
    
    Returns:
        SystemState: 测试用系统状态对象
    """
    return SystemState(
        status="running",
        version_info=VersionInfo(
            current_version="1.0.0",
            latest_evolution_version="1.0.0",
            evolution_count=0
        ),
        resource_usage=ResourceUsage(
            cpu=0.3,
            memory=0.4,
            disk=0.2
        ),
        utility_score=0.85,
        security_status="normal",
        learning_status="disabled",
        last_updated=datetime.utcnow(),
        uptime=timedelta(hours=1)
    )


@pytest.fixture(scope="function")
def mock_openai_client() -> Generator[MagicMock, None, None]:
    """
    Mock OpenAI客户端夹具
    
    Yields:
        MagicMock: Mock的OpenAI客户端
    """
    with patch("openai.OpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = """1. 缺陷修复应优先考虑安全性
2. 代码修改需遵循现有架构模式
3. 学习点提取应关注可复用模式"""
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client


@pytest.fixture(scope="function")
def mock_sandbox() -> Generator[MagicMock, None, None]:
    """
    Mock沙箱夹具
    
    Yields:
        MagicMock: Mock的沙箱对象
    """
    with patch("meta_agent.utils.sandbox.Sandbox") as mock_sandbox_class:
        mock_sandbox = MagicMock()
        mock_sandbox_class.return_value = mock_sandbox
        
        mock_sandbox.execute.return_value = {
            "status": "success",
            "result": "mock_execution_result",
            "execution_time": 0.1
        }
        
        yield mock_sandbox


@pytest.fixture(scope="function")
def meta_agent_test_instance(
    test_config: Config,
    test_system_state: SystemState,
    mock_sandbox: MagicMock
) -> MetaAgent:
    """
    MetaAgent测试实例夹具
    
    Args:
        test_config: 测试配置
        test_system_state: 测试系统状态
        mock_sandbox: Mock沙箱
        
    Returns:
        MetaAgent: MetaAgent测试实例
    """
    with patch("meta_agent.core.security.check_controller_permission"):
        with patch("meta_agent.core.security.check_module_integrity"):
            set_original_module_hashes({})
            agent = MetaAgent(config=test_config)
            agent._state = test_system_state
            return agent


class TestDataBuilder:
    """测试数据构建器，用于快速创建各种测试数据"""
    
    @staticmethod
    def create_defect(
        component: str = "utility",
        description: str = "测试缺陷",
        severity: float = 0.5,
        related_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建缺陷测试数据
        
        Args:
            component: 组件类型
            description: 缺陷描述
            severity: 严重程度
            related_code: 关联代码路径
            
        Returns:
            Dict[str, Any]: 缺陷数据
        """
        return {
            "id": f"defect_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "component": component,
            "description": description,
            "severity": severity,
            "related_code": related_code or f"src/meta_agent/{component}/",
            "detected_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_modification(
        action: str = "modify",
        component: str = "utility",
        description: str = "测试修改"
    ) -> Dict[str, Any]:
        """
        创建修改测试数据
        
        Args:
            action: 操作类型
            component: 组件类型
            description: 修改描述
            
        Returns:
            Dict[str, Any]: 修改数据
        """
        return {
            "id": f"mod_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "action": action,
            "component": component,
            "description": description,
            "content": {"test": "data"},
            "created_at": datetime.utcnow().isoformat()
        }


@pytest.fixture(scope="function")
def test_data_builder() -> TestDataBuilder:
    """测试数据构建器夹具"""
    return TestDataBuilder()


def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line(
        "markers", "unit: 标记为单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试"
    )
    config.addinivalue_line(
        "markers", "performance: 标记为性能测试"
    )
    config.addinivalue_line(
        "markers", "security: 标记为安全测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试"
    )
    
    setup_logging(log_level="WARNING", structured=False)


def pytest_collection_modifyitems(config, items):
    """测试收集修改钩子，自动添加标记"""
    for item in items:
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "security" in item.nodeid:
            item.add_marker(pytest.mark.security)

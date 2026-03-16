# -*- coding: utf-8 -*-
"""
pytest 测试配置

提供全局的 fixtures 和配置。
"""

import pytest
import os
import sys

# 添加 src 路径到 sys.path（适配 src 布局）
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return {
        "environment": "test",
        "debug": True,
        "log_level": "DEBUG",
    }


@pytest.fixture
def sample_task():
    """示例任务"""
    from meta_agent.models.task import Task, TaskStatus
    
    return Task(
        task_id="test_001",
        content="Test task content",
        priority=5,
        status=TaskStatus.PENDING,
    )


@pytest.fixture
def mock_llm_client():
    """Mock LLM 客户端"""
    class MockLLMClient:
        def generate(self, prompt: str) -> str:
            return f"Mock response for: {prompt}"
    
    return MockLLMClient()


@pytest.fixture(autouse=True)
def setup_test_env():
    """自动设置测试环境变量"""
    os.environ["META_AGENT_ENV"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield
    # 清理环境变量
    os.environ.pop("META_AGENT_ENV", None)

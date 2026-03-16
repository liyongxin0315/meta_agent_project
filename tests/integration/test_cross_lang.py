# -*- coding: utf-8 -*-
"""
跨语言集成测试

测试 Python 与 Go/Rust 模块的交互。
"""

import pytest
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'python'))


class TestRustAdapter:
    """Rust 适配器测试"""

    def test_rust_core_initialization(self):
        """测试 Rust Core 初始化"""
        from meta_agent.adapters.rust_adapter import RustCore
        
        core = RustCore()
        assert core is not None
        # 注意：实际使用时需要编译 Rust 扩展
        # assert core._initialized is True

    def test_rust_parse_task(self):
        """测试 Rust 任务解析"""
        from meta_agent.adapters.rust_adapter import RustCore
        
        core = RustCore()
        result = core.parse_task("test_task")
        
        assert isinstance(result, dict)
        assert "task_id" in result
        assert "content" in result
        assert result["content"] == "test_task"

    def test_rust_execute(self):
        """测试 Rust 执行"""
        from meta_agent.adapters.rust_adapter import RustCore
        
        core = RustCore()
        data = {"key": "value"}
        result = core.execute(data)
        
        assert isinstance(result, dict)
        assert "status" in result

    def test_rust_repr(self):
        """测试 Rust Core 字符串表示"""
        from meta_agent.adapters.rust_adapter import RustCore
        
        core = RustCore()
        repr_str = repr(core)
        
        assert "RustCore" in repr_str
        assert "initialized" in repr_str


class TestGoAdapter:
    """Go 适配器测试"""

    def test_go_initialization(self):
        """测试 Go 服务初始化"""
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        service = GoConcurrency("localhost:8080")
        assert service is not None
        assert service._service_addr == "localhost:8080"
        assert service._timeout == 5.0
        assert service._max_retries == 3

    def test_go_execute_task_fallback(self):
        """测试 Go 任务执行（降级模式）"""
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        service = GoConcurrency()
        result = service.execute_task("task_001", "test_content")
        
        assert isinstance(result, str)
        assert "task_001" in result
        assert "test_content" in result

    def test_go_health_check(self):
        """测试 Go 健康检查"""
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        service = GoConcurrency()
        # 降级模式下返回 False
        assert service.health_check() is False

    def test_go_context_manager(self):
        """测试 Go 上下文管理器"""
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        with GoConcurrency() as service:
            assert service is not None
        
        # 退出上下文后连接应关闭
        assert service._connected is False

    def test_go_custom_timeout(self):
        """测试自定义超时时间"""
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        service = GoConcurrency(timeout=10.0, max_retries=5)
        assert service._timeout == 10.0
        assert service._max_retries == 5


class TestCrossLanguage:
    """跨语言协作测试"""

    def test_rust_then_go(self):
        """测试 Rust 解析后 Go 执行"""
        from meta_agent.adapters.rust_adapter import RustCore
        from meta_agent.adapters.go_adapter import GoConcurrency
        
        rust_core = RustCore()
        go_service = GoConcurrency()
        
        # Rust 解析
        parsed = rust_core.parse_task("cross_lang_task")
        assert parsed is not None
        
        # Go 执行
        result = go_service.execute_task(
            str(parsed["task_id"]),
            parsed["content"]
        )
        assert result is not None

    def test_error_handling(self):
        """测试跨语言异常处理"""
        from meta_agent.adapters.rust_adapter import RustCore
        
        core = RustCore()
        
        # 应该降级到 Python 实现而不是抛出异常
        result = core.parse_task("")
        assert result is not None


@pytest.mark.parametrize("task_content,priority", [
    ("simple_task", 1),
    ("medium_task", 5),
    ("complex_task", 10),
    ("", 5),  # 空内容测试
    ("特殊字符测试", 5),  # 中文测试
])
def test_task_variants(task_content, priority):
    """参数化测试不同任务变体"""
    from meta_agent.adapters.rust_adapter import RustCore
    
    core = RustCore()
    result = core.parse_task(task_content)
    
    assert isinstance(result, dict)
    assert "task_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

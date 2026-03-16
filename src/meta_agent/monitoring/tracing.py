"""
分布式追踪 - 企业级实现
集成 OpenTelemetry 进行分布式追踪
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)

_HAS_OPENTELEMETRY = False
_trace = None
_TracerProvider = None
_BatchSpanProcessor = None
_ConsoleSpanExporter = None
_OTLPSpanExporter = None
_Resource = None

try:
    from opentelemetry import trace as _trace
    from opentelemetry.sdk.trace import TracerProvider as _TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor as _BatchSpanProcessor,
        ConsoleSpanExporter as _ConsoleSpanExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as _OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource as _Resource
    _HAS_OPENTELEMETRY = True
except ImportError:
    pass


@dataclass
class TracingConfig:
    """追踪配置"""
    enable_tracing: bool = True
    service_name: str = "metaagent"
    service_version: str = "1.0.0"
    otlp_endpoint: Optional[str] = None
    console_exporter: bool = False


class Tracer:
    """分布式追踪器"""
    
    def __init__(self, config: Optional[TracingConfig] = None):
        self.config = config or TracingConfig()
        self._initialized = False
        self._tracer = None
        
        if _HAS_OPENTELEMETRY and self.config.enable_tracing:
            self._init_opentelemetry()
    
    def _init_opentelemetry(self) -> None:
        """初始化 OpenTelemetry"""
        if self._initialized or not _HAS_OPENTELEMETRY:
            return
        
        assert _Resource is not None
        assert _TracerProvider is not None
        assert _BatchSpanProcessor is not None
        assert _ConsoleSpanExporter is not None
        assert _trace is not None
        
        resource = _Resource.create({
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
        })
        
        provider = _TracerProvider(resource=resource)
        
        if self.config.otlp_endpoint and _OTLPSpanExporter is not None:
            otlp_exporter = _OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
            processor = _BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(processor)
        
        if self.config.console_exporter:
            console_processor = _BatchSpanProcessor(_ConsoleSpanExporter())
            provider.add_span_processor(console_processor)
        
        _trace.set_tracer_provider(provider)
        self._tracer = _trace.get_tracer(self.config.service_name, self.config.service_version)
        self._initialized = True
        logger.info("OpenTelemetry tracing initialized")
    
    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """创建 span 上下文"""
        if not _HAS_OPENTELEMETRY or not self._tracer:
            yield
            return
        
        with self._tracer.start_as_current_span(name, attributes=attributes or {}):
            yield
    
    def trace(self, name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
        """追踪装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                span_name = name or func.__name__
                with self.span(span_name, attributes):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """添加事件"""
        if not _HAS_OPENTELEMETRY or not self._tracer or _trace is None:
            return
        
        current_span = _trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes=attributes or {})
    
    def set_attribute(self, key: str, value: Any) -> None:
        """设置属性"""
        if not _HAS_OPENTELEMETRY or not self._tracer or _trace is None:
            return
        
        current_span = _trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)


# 全局追踪器实例
tracer = Tracer()

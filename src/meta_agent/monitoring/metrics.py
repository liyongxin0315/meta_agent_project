"""
指标监控 - 企业级实现
集成 Prometheus 进行指标收集
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        start_http_server,
    )
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


@dataclass
class MetricsConfig:
    """指标配置"""
    enable_prometheus: bool = True
    http_port: int = 9090
    namespace: str = "metaagent"


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        self.config = config or MetricsConfig()
        self._initialized = False
        self._counters: Dict[str, Any] = {}
        self._gauges: Dict[str, Any] = {}
        self._histograms: Dict[str, Any] = {}
        
        if HAS_PROMETHEUS and self.config.enable_prometheus:
            self._init_prometheus()
    
    def _init_prometheus(self) -> None:
        """初始化 Prometheus 指标"""
        if self._initialized:
            return
        
        ns = self.config.namespace
        
        self._counters["evolution_total"] = Counter(
            f"{ns}_evolution_total",
            "Total number of evolutions",
            ["status"]
        )
        
        self._counters["llm_calls_total"] = Counter(
            f"{ns}_llm_calls_total",
            "Total number of LLM calls",
            ["model", "cached", "success"]
        )
        
        self._histograms["evolution_duration_seconds"] = Histogram(
            f"{ns}_evolution_duration_seconds",
            "Evolution duration in seconds",
            buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 120]
        )
        
        self._histograms["llm_latency_seconds"] = Histogram(
            f"{ns}_llm_latency_seconds",
            "LLM call latency in seconds",
            ["model"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30]
        )
        
        self._gauges["cache_hit_rate"] = Gauge(
            f"{ns}_cache_hit_rate",
            "Cache hit rate"
        )
        
        self._initialized = True
        logger.info("Prometheus metrics initialized")
    
    def start_http_server(self, port: Optional[int] = None) -> None:
        """启动 Prometheus HTTP 服务"""
        if not HAS_PROMETHEUS:
            logger.warning("prometheus-client not installed, cannot start HTTP server")
            return
        
        actual_port = port or self.config.http_port
        start_http_server(actual_port)
        logger.info(f"Prometheus metrics server started on port {actual_port}")
    
    def record_evolution_start(self) -> None:
        """记录进化开始"""
    
    def record_evolution_complete(
        self, success: bool, duration_seconds: float
    ) -> None:
        """记录进化完成"""
        if HAS_PROMETHEUS and self._initialized:
            status = "success" if success else "failure"
            self._counters["evolution_total"].labels(status=status).inc()
            self._histograms["evolution_duration_seconds"].observe(duration_seconds)
    
    def record_llm_call(
        self, model: str, cached: bool, success: bool, latency_seconds: float
    ) -> None:
        """记录 LLM 调用"""
        if HAS_PROMETHEUS and self._initialized:
            cached_str = "true" if cached else "false"
            success_str = "true" if success else "false"
            self._counters["llm_calls_total"].labels(
                model=model, cached=cached_str, success=success_str
            ).inc()
            self._histograms["llm_latency_seconds"].labels(model=model).observe(latency_seconds)
    
    def set_cache_hit_rate(self, rate: float) -> None:
        """设置缓存命中率"""
        if HAS_PROMETHEUS and self._initialized:
            self._gauges["cache_hit_rate"].set(rate)


# 全局指标收集器实例
metrics_collector = MetricsCollector()

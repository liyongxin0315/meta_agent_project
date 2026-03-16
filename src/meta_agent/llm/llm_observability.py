"""
LLM可观测性 - 企业级实现
提供LLM调用的指标收集、追踪和分析
优化：解析 LLM API 返回的 usage 字段，不再硬编码为 0
"""

import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import threading
from functools import wraps

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMMetrics:
    """LLM调用指标"""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_seconds: float
    cached: bool
    success: bool
    timestamp: float
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ModelMetrics:
    """模型级指标"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    cached_calls: int = 0
    total_latency: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)


class LLMObservability:
    """LLM可观测性"""
    
    def __init__(self, max_history: int = 10000):
        self._metrics_history: List[LLMMetrics] = []
        self._model_metrics: Dict[str, ModelMetrics] = defaultdict(ModelMetrics)
        self._lock = threading.Lock()
        self._max_history = max_history
        self._callbacks: List[Callable[[LLMMetrics], None]] = []
    
    def record_call(
        self, metrics: LLMMetrics) -> None:
        """记录LLM调用"""
        with self._lock:
            self._metrics_history.append(metrics)
            
            if len(self._metrics_history) > self._max_history:
                self._metrics_history = self._metrics_history[-self._max_history:]
            
            model_metrics = self._model_metrics[metrics.model]
            model_metrics.total_calls += 1
            model_metrics.total_latency += metrics.latency_seconds
            model_metrics.total_prompt_tokens += metrics.prompt_tokens
            model_metrics.total_completion_tokens += metrics.completion_tokens
            
            if metrics.success:
                model_metrics.successful_calls += 1
            else:
                model_metrics.failed_calls += 1
                if metrics.error_type:
                    model_metrics.error_counts[metrics.error_type] = \
                        model_metrics.error_counts.get(metrics.error_type, 0) + 1
            
            if metrics.cached:
                model_metrics.cached_calls += 1
        
        for callback in self._callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")
    
    def record_call_from_response(
        self,
        model: str,
        response: Any,
        latency_seconds: float,
        cached: bool = False,
    ) -> None:
        """从 LLM 响应记录指标 - 解析实际 usage 字段"""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        success = True
        error_type = None
        error_message = None
        
        try:
            if hasattr(response, 'usage'):
                usage = response.usage
                prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                completion_tokens = getattr(usage, 'completion_tokens', 0)
                total_tokens = getattr(usage, 'total_tokens', 0)
        except Exception as e:
            logger.warning(f"解析 usage 字段失败: {e}")
        
        metrics = LLMMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_seconds=latency_seconds,
            cached=cached,
            success=success,
            timestamp=time.time(),
            error_type=error_type,
            error_message=error_message,
        )
        self.record_call(metrics)
    
    def get_model_summary(self, model: str) -> Optional[Dict[str, Any]]:
        """获取模型指标摘要"""
        with self._lock:
            if model not in self._model_metrics:
                return None
            
            mm = self._model_metrics[model]
            avg_latency = mm.total_latency / mm.total_calls if mm.total_calls > 0 else 0.0
            success_rate = mm.successful_calls / mm.total_calls if mm.total_calls > 0 else 0.0
            cache_hit_rate = mm.cached_calls / mm.total_calls if mm.total_calls > 0 else 0.0
            
            return {
                "model": model,
                "total_calls": mm.total_calls,
                "successful_calls": mm.successful_calls,
                "failed_calls": mm.failed_calls,
                "cached_calls": mm.cached_calls,
                "success_rate": success_rate,
                "cache_hit_rate": cache_hit_rate,
                "avg_latency_seconds": avg_latency,
                "total_prompt_tokens": mm.total_prompt_tokens,
                "total_completion_tokens": mm.total_completion_tokens,
                "total_tokens": mm.total_prompt_tokens + mm.total_completion_tokens,
                "error_counts": dict(mm.error_counts),
            }
    
    def get_all_models_summary(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """获取所有模型指标摘要"""
        with self._lock:
            return {
                model: self.get_model_summary(model) for model in self._model_metrics
            }
    
    def get_overall_summary(self) -> Dict[str, Any]:
        """获取总体指标摘要"""
        with self._lock:
            total_calls = sum(mm.total_calls for mm in self._model_metrics.values())
            total_successful = sum(mm.successful_calls for mm in self._model_metrics.values())
            total_cached = sum(mm.cached_calls for mm in self._model_metrics.values())
            total_latency = sum(mm.total_latency for mm in self._model_metrics.values())
            total_prompt = sum(mm.total_prompt_tokens for mm in self._model_metrics.values())
            total_completion = sum(mm.total_completion_tokens for mm in self._model_metrics.values())
            
            avg_latency = total_latency / total_calls if total_calls > 0 else 0.0
            success_rate = total_successful / total_calls if total_calls > 0 else 0.0
            cache_hit_rate = total_cached / total_calls if total_calls > 0 else 0.0
            
            return {
                "total_calls": total_calls,
                "successful_calls": total_successful,
                "failed_calls": total_calls - total_successful,
                "cached_calls": total_cached,
                "success_rate": success_rate,
                "cache_hit_rate": cache_hit_rate,
                "avg_latency_seconds": avg_latency,
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_tokens": total_prompt + total_completion,
            }
    
    def add_callback(self, callback: Callable[[LLMMetrics], None]) -> None:
        """添加指标回调"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[LLMMetrics], None]) -> bool:
        """移除指标回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False
    
    def clear(self) -> None:
        """清除所有指标"""
        with self._lock:
            self._metrics_history.clear()
            self._model_metrics.clear()


def observe_llm_call(observability: LLMObservability):
    """LLM调用观测装饰器 - 解析实际 usage 字段"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            model = kwargs.get("model", "unknown")
            cached = kwargs.get("cached", False)
            success = False
            error_type = None
            error_message = None
            response = None
            
            try:
                response = func(*args, **kwargs)
                success = True
                return response
            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                raise
            finally:
                latency = time.time() - start_time
                prompt_tokens = 0
                completion_tokens = 0
                
                if response is not None and success:
                    try:
                        if hasattr(response, 'usage'):
                            usage = response.usage
                            prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                            completion_tokens = getattr(usage, 'completion_tokens', 0)
                    except Exception as e:
                        logger.warning(f"解析 usage 字段失败: {e}")
                
                metrics = LLMMetrics(
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    latency_seconds=latency,
                    cached=cached,
                    success=success,
                    timestamp=time.time(),
                    error_type=error_type,
                    error_message=error_message,
                )
                observability.record_call(metrics)
        
        return wrapper
    return decorator


# 全局LLM可观测性实例
llm_observability = LLMObservability()

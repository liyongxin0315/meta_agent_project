"""
LLM客户端包装器 - 核心实现（集成蒸馏原理优化
包含前置元思考、记忆存储、对话蒸馏、自我进化
"""

import time
import threading
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from meta_agent.core.logging import get_logger
from meta_agent.core.exceptions import NetworkError
from meta_agent.llm.llm_cache import llm_cache, LLMCache
from meta_agent.llm.rate_limiter import rate_limiter, RateLimiter
from meta_agent.llm.dialog_memory import DialogMemoryStore, dialog_memory
from meta_agent.llm.meta_thinker import MetaThinker, meta_thinker
from meta_agent.llm.distill_evolver import DistillEvolver, distill_evolver

logger = get_logger(__name__)


@dataclass
class LLMCallMetrics:
    """LLM调用指标"""
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_seconds: float
    cached: bool
    success: bool
    timestamp: float


class LLMClientWrapper:
    """LLM客户端包装器（集成蒸馏原理优化）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cache: Optional[LLMCache] = None,
        limiter: Optional[RateLimiter] = None,
        enable_cache: bool = True,
        enable_rate_limit: bool = True,
        enable_retry: bool = True,
        enable_meta_think: bool = True,
        enable_dialog_memory: bool = True,
        enable_auto_evolve: bool = True,
        dialog_memory_store: Optional[DialogMemoryStore] = None,
        meta_thinker_instance: Optional[MetaThinker] = None,
        distill_evolver_instance: Optional[DistillEvolver] = None
    ):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.cache = cache or llm_cache
        self.limiter = limiter or rate_limiter
        self.enable_cache = enable_cache
        self.enable_rate_limit = enable_rate_limit
        self.enable_retry = enable_retry
        self.metrics: List[LLMCallMetrics] = []
        self._metrics_lock = threading.Lock()
        
        self.enable_meta_think = enable_meta_think
        self.enable_dialog_memory = enable_dialog_memory
        self.enable_auto_evolve = enable_auto_evolve
        self.dialog_memory = dialog_memory_store or dialog_memory
        self.meta_thinker = meta_thinker_instance or meta_thinker
        self.distill_evolver = distill_evolver_instance or distill_evolver
    
    def _record_metrics(self, metrics: LLMCallMetrics) -> None:
        """记录调用指标"""
        self.metrics.append(metrics)
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: int = 30,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
        enable_meta_think: Optional[bool] = None,
        enable_memory_save: Optional[bool] = None,
        enable_auto_evolve: Optional[bool] = None
    ) -> str:
        """
        发送聊天请求（集成蒸馏原理优化）
        完整流程：前置元思考 → 拼接进化知识 → API调用 → 存储对话 → 后台蒸馏进化
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 超时时间
            use_cache: 是否使用缓存
            cache_ttl: 缓存TTL（秒）
            enable_meta_think: 是否启用前置元思考（覆盖默认配置）
            enable_memory_save: 是否保存对话记忆（覆盖默认配置）
            enable_auto_evolve: 是否启用自动蒸馏进化（覆盖默认配置）
            
        Returns:
            str: 模型响应
        """
        start_time = time.time()
        
        use_meta_think = enable_meta_think if enable_meta_think is not None else self.enable_meta_think
        use_memory_save = enable_memory_save if enable_memory_save is not None else self.enable_dialog_memory
        use_auto_evolve = enable_auto_evolve if enable_auto_evolve is not None else self.enable_auto_evolve
        
        user_input = ""
        history = []
        meta_think_result = None
        
        if use_meta_think and messages:
            user_input, history = self._extract_user_input_and_history(messages)
            if user_input:
                meta_think_result = self._do_meta_think(user_input, history, model)
        
        augmented_messages = messages
        if meta_think_result:
            augmented_messages = self._augment_messages_with_evolution(messages)
        
        try:
            if self.enable_cache and use_cache:
                cached_response = self.cache.get(augmented_messages, model, temperature)
                if cached_response:
                    logger.debug("缓存命中，直接返回")
                    self._record_metrics(LLMCallMetrics(
                        model=model,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        latency_seconds=time.time() - start_time,
                        cached=True,
                        success=True,
                        timestamp=time.time()
                    ))
                    return cached_response
            
            if self.enable_rate_limit:
                if not self.limiter.check_rate_limit(f"llm_{model}"):
                    raise NetworkError("请求被限流，请稍后再试")
            
            if self.enable_retry:
                response = self._chat_with_retry(
                    augmented_messages, model, temperature, max_tokens, timeout
                )
            else:
                response = self._chat_once(
                    augmented_messages, model, temperature, max_tokens, timeout
                )
            
            content = response.choices[0].message.content.strip()
            
            if self.enable_cache and use_cache:
                self.cache.set(augmented_messages, model, temperature, content, cache_ttl)
            
            usage = response.usage
            self._record_metrics(LLMCallMetrics(
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                latency_seconds=time.time() - start_time,
                cached=False,
                success=True,
                timestamp=time.time()
            ))
            
            if use_memory_save:
                quality_score = meta_think_result.confidence if meta_think_result else 0.8
                self.dialog_memory.save_dialog(augmented_messages, content, quality_score)
            
            if use_auto_evolve and meta_think_result and meta_think_result.need_evolve:
                self.distill_evolver.evolve_async(
                    self._simple_chat,
                    self.dialog_memory,
                    model=model
                )
            
            return content
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            self._record_metrics(LLMCallMetrics(
                model=model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_seconds=time.time() - start_time,
                cached=False,
                success=False,
                timestamp=time.time()
            ))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.Timeout
        ))
    )
    def _chat_with_retry(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        timeout: int
    ) -> Any:
        """带重试的聊天请求"""
        return self._chat_once(messages, model, temperature, max_tokens, timeout)
    
    def _chat_once(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        timeout: int
    ) -> Any:
        """单次聊天请求"""
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics:
            return {"total_calls": 0}
        
        successful = [m for m in self.metrics if m.success]
        cached = [m for m in self.metrics if m.cached]
        latencies = [m.latency_seconds for m in self.metrics if m.success]
        
        return {
            "total_calls": len(self.metrics),
            "successful_calls": len(successful),
            "success_rate": len(successful) / len(self.metrics),
            "cached_calls": len(cached),
            "cache_hit_rate": len(cached) / len(self.metrics) if self.metrics else 0,
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            "total_prompt_tokens": sum(m.prompt_tokens for m in self.metrics),
            "total_completion_tokens": sum(m.completion_tokens for m in self.metrics),
            "total_tokens": sum(m.total_tokens for m in self.metrics)
        }
    
    def _extract_user_input_and_history(self, messages: List[Dict[str, str]]):
        """从消息列表中提取用户输入和历史对话"""
        user_input = ""
        history = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                user_input = content
            elif role in ["user", "assistant"]:
                history.append(msg)
        
        return user_input, history[:-1] if history else []
    
    def _do_meta_think(self, user_input: str, history: List[Dict[str, str]], model: str):
        """执行前置元思考"""
        try:
            think_prompt = self.meta_thinker.build_think_prompt(user_input, history)
            think_messages = [{"role": "user", "content": think_prompt}]
            think_response = self._simple_chat(think_messages, model, 0.1)
            return self.meta_thinker.parse_think_result(think_response)
        except Exception as e:
            logger.warning(f"元思考失败: {e}")
            return None
    
    def _augment_messages_with_evolution(self, messages: List[Dict[str, str]]):
        """用进化知识增强消息"""
        evolution_prompt = self.distill_evolver.get_evolution_system_prompt()
        if not evolution_prompt:
            return messages
        
        augmented = []
        found_system = False
        
        for msg in messages:
            if msg.get("role") == "system":
                new_content = msg.get("content", "") + "\n\n" + evolution_prompt
                augmented.append({"role": "system", "content": new_content})
                found_system = True
            else:
                augmented.append(msg)
        
        if not found_system:
            augmented.insert(0, {"role": "system", "content": evolution_prompt})
        
        return augmented
    
    def _simple_chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
        """简单的聊天调用（用于内部功能，不经过缓存等）"""
        response = self._chat_once(messages, model, temperature, None, 60)
        return response.choices[0].message.content.strip()

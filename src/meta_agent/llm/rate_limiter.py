"""
限流器 - 核心实现
"""

import time
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass
from collections import deque
from enum import Enum, auto

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitStrategy(Enum):
    """限流策略"""
    TOKEN_BUCKET = auto()
    FIXED_WINDOW = auto()
    SLIDING_WINDOW = auto()


@dataclass
class RateLimitConfig:
    """限流配置"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET


class TokenBucket:
    """令牌桶算法"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def try_consume(self, tokens: int = 1) -> bool:
        """尝试消费令牌"""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate
            )
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class SlidingWindow:
    """滑动窗口算法"""
    
    def __init__(self, window_size_seconds: int, max_requests: int):
        self.window_size = window_size_seconds
        self.max_requests = max_requests
        self.requests: deque = deque()
        self._lock = threading.Lock()
    
    def try_acquire(self) -> bool:
        """尝试获取请求许可"""
        with self._lock:
            now = time.time()
            
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False


class RateLimiter:
    """限流器"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._token_buckets: Dict[str, TokenBucket] = {}
        self._sliding_windows: Dict[str, SlidingWindow] = {}
        self._lock = threading.Lock()
        self._rejected = 0
        self._allowed = 0
    
    def _get_token_bucket(self, key: str) -> TokenBucket:
        """获取或创建令牌桶"""
        with self._lock:
            if key not in self._token_buckets:
                refill_rate = self.config.requests_per_minute / 60.0
                self._token_buckets[key] = TokenBucket(
                    capacity=self.config.burst_size,
                    refill_rate=refill_rate
                )
            return self._token_buckets[key]
    
    def _get_sliding_window(self, key: str) -> SlidingWindow:
        """获取或创建滑动窗口"""
        with self._lock:
            if key not in self._sliding_windows:
                self._sliding_windows[key] = SlidingWindow(
                    window_size_seconds=60,
                    max_requests=self.config.requests_per_minute
                )
            return self._sliding_windows[key]
    
    def check_rate_limit(self, key: str = "default") -> bool:
        """检查是否超过限流"""
        if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            bucket = self._get_token_bucket(key)
            allowed = bucket.try_consume()
        elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            window = self._get_sliding_window(key)
            allowed = window.try_acquire()
        else:
            allowed = True
        
        if allowed:
            self._allowed += 1
            logger.debug(f"请求允许: key={key}, allowed={self._allowed}")
        else:
            self._rejected += 1
            logger.warning(f"请求被限流: key={key}, rejected={self._rejected}")
        
        return allowed
    
    def get_stats(self) -> Dict[str, Any]:
        """获取限流统计"""
        total = self._allowed + self._rejected
        reject_rate = self._rejected / total if total > 0 else 0.0
        
        return {
            "allowed": self._allowed,
            "rejected": self._rejected,
            "reject_rate": reject_rate,
            "strategy": self.config.strategy.name
        }


# 全局限流器实例
rate_limiter = RateLimiter()

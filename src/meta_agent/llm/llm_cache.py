"""
LLM缓存层 - 核心实现
"""

import hashlib
import json
from typing import Any, Dict, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = auto()
    TTL = auto()
    HYBRID = auto()


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LLMCache:
    """LLM缓存层"""
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        strategy: CacheStrategy = CacheStrategy.HYBRID
    ):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._strategy = strategy
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, messages: list, model: str, temperature: float) -> str:
        """生成缓存键"""
        key_data = {
            "messages": messages,
            "model": model,
            "temperature": round(temperature, 2)
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_json.encode()).hexdigest()
    
    def get(
        self,
        messages: list,
        model: str,
        temperature: float
    ) -> Optional[str]:
        """获取缓存"""
        key = self._generate_key(messages, model, temperature)
        entry = self._cache.get(key)
        
        if not entry:
            self._misses += 1
            return None
        
        if entry.expires_at and entry.expires_at < datetime.now(timezone.utc):
            del self._cache[key]
            self._misses += 1
            return None
        
        entry.access_count += 1
        entry.last_accessed = datetime.now(timezone.utc)
        self._hits += 1
        
        logger.debug(f"缓存命中: key={key[:16]}..., hits={self._hits}, misses={self._misses}")
        return entry.value
    
    def set(
        self,
        messages: list,
        model: str,
        temperature: float,
        value: str,
        ttl: Optional[int] = None
    ) -> None:
        """设置缓存"""
        key = self._generate_key(messages, model, temperature)
        
        if len(self._cache) >= self._max_size:
            self._evict()
        
        expires_at = None
        if ttl or self._default_ttl:
            ttl_seconds = ttl or self._default_ttl
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        self._cache[key] = entry
        
        logger.debug(f"缓存设置: key={key[:16]}..., size={len(self._cache)}")
    
    def _evict(self) -> None:
        """淘汰缓存条目"""
        if self._strategy == CacheStrategy.LRU:
            sorted_entries = sorted(
                self._cache.values(),
                key=lambda x: x.last_accessed
            )
            key_to_remove = sorted_entries[0].key
        elif self._strategy == CacheStrategy.TTL:
            sorted_entries = sorted(
                self._cache.values(),
                key=lambda x: x.expires_at or datetime.max
            )
            key_to_remove = sorted_entries[0].key
        else:
            sorted_entries = sorted(
                self._cache.values(),
                key=lambda x: (x.last_accessed, x.access_count)
            )
            key_to_remove = sorted_entries[0].key
        
        del self._cache[key_to_remove]
        logger.debug(f"缓存淘汰: key={key_to_remove[:16]}...")
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "strategy": self._strategy.name
        }


# 全局缓存实例
llm_cache = LLMCache()

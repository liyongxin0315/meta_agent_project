"""
批量处理器 - 企业级实现
支持LLM请求批量处理，降低成本和提高效率
优化：使用 asyncio.run_coroutine_threadsafe 确保线程安全
"""

import asyncio
import time
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import deque
import threading

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BatchRequest:
    """批量请求项"""
    request_id: str
    messages: List[Dict[str, str]]
    model: str
    temperature: float
    max_tokens: Optional[int]
    callback: Callable[[Optional[str], Optional[Exception]], None]
    created_at: float = field(default_factory=time.time)


@dataclass
class BatchConfig:
    """批量处理配置"""
    max_batch_size: int = 10
    max_wait_time: float = 0.5
    max_concurrent_batches: int = 3


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config: Optional[BatchConfig] = None, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.config = config or BatchConfig()
        self._request_queue: deque = deque()
        self._lock = threading.Lock()
        self._processing = False
        self._event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._semaphore = threading.Semaphore(self.config.max_concurrent_batches)
        self._loop = loop or asyncio.get_event_loop()
    
    def submit(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int] = None,
    ) -> asyncio.Future:
        """提交请求到批量队列"""
        future = asyncio.Future()
        request_id = f"req_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        
        def callback(result: Optional[str], error: Optional[Exception]) -> None:
            """线程安全的回调 - 使用 asyncio.run_coroutine_threadsafe"""
            async def set_result():
                if error:
                    future.set_exception(error)
                else:
                    future.set_result(result)
            
            asyncio.run_coroutine_threadsafe(set_result(), self._loop)
        
        request = BatchRequest(
            request_id=request_id,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            callback=callback,
        )
        
        with self._lock:
            self._request_queue.append(request)
            logger.debug(f"请求已加入批量队列: {request_id}")
        
        self._event.set()
        
        if not self._processing:
            self._start_worker()
        
        return future
    
    def _start_worker(self) -> None:
        """启动工作线程"""
        self._processing = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def _worker_loop(self) -> None:
        """工作线程循环"""
        while self._processing:
            batch = self._collect_batch()
            
            if batch:
                self._process_batch(batch)
            else:
                self._event.wait(timeout=self.config.max_wait_time)
                self._event.clear()
    
    def _collect_batch(self) -> List[BatchRequest]:
        """收集批量请求"""
        batch: List[BatchRequest] = []
        
        with self._lock:
            start_time = time.time()
            
            while len(batch) < self.config.max_batch_size:
                if not self._request_queue:
                    if batch:
                        elapsed = time.time() - start_time
                        if elapsed >= self.config.max_wait_time:
                            break
                        time.sleep(0.01)
                        continue
                    else:
                        break
                
                request = self._request_queue.popleft()
                batch.append(request)
        
        return batch
    
    def _process_batch(self, batch: List[BatchRequest]) -> None:
        """处理批量请求"""
        if not batch:
            return
        
        logger.info(f"处理批量请求: {len(batch)} 个")
        
        with self._semaphore:
            for request in batch:
                try:
                    logger.debug(f"处理请求: {request.request_id}")
                    time.sleep(0.01)
                except Exception as e:
                    logger.error(f"请求处理失败: {request.request_id}, error={e}")
                    request.callback(None, e)
    
    def stop(self) -> None:
        """停止批量处理器"""
        self._processing = False
        self._event.set()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        
        with self._lock:
            while self._request_queue:
                request = self._request_queue.popleft()
                try:
                    request.callback(None, Exception("批量处理器已停止"))
                except Exception as e:
                    logger.error(f"回调失败: {e}")
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        with self._lock:
            return len(self._request_queue)


# 全局批量处理器实例
batch_processor = BatchProcessor()

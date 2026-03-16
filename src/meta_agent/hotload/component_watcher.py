"""
组件监视器 - 企业级实现
监控文件变化并自动触发热加载
"""
# pyright: reportGeneralTypeIssues=false
# pyright: reportRedeclaration=false

import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class WatchEvent(Enum):
    """监控事件类型"""
    CREATED = auto()
    MODIFIED = auto()
    DELETED = auto()


@dataclass
class WatchConfig:
    """监控配置"""
    watch_dirs: List[Path]
    file_extensions: Set[str] = field(default_factory=lambda: {".py"})
    debounce_seconds: float = 1.0
    auto_reload: bool = True


try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None
    FileSystemEventHandler = object


class _ComponentFileHandlerBase:
    """文件变化处理器基类"""
    
    def __init__(
        self,
        watcher: "ComponentWatcher",
        debounce_seconds: float = 1.0,
    ):
        self.watcher = watcher
        self.debounce_seconds = debounce_seconds
        self._pending_changes: Dict[Path, float] = {}
        self._lock = threading.Lock()
        self._debounce_thread: Optional[threading.Thread] = None
        self._running = False
    
    def _handle_change(self, file_path: Path, event_type: WatchEvent) -> None:
        """处理文件变化"""
        with self._lock:
            self._pending_changes[file_path] = time.time()
            
            if not self._running:
                self._start_debounce_thread()
    
    def _start_debounce_thread(self) -> None:
        """启动防抖线程"""
        self._running = True
        self._debounce_thread = threading.Thread(target=self._debounce_loop, daemon=True)
        self._debounce_thread.start()
    
    def _debounce_loop(self) -> None:
        """防抖处理循环"""
        while self._running:
            time.sleep(0.1)
            
            with self._lock:
                now = time.time()
                changes_to_process: List[Path] = []
                
                for file_path, change_time in list(self._pending_changes.items()):
                    if now - change_time >= self.debounce_seconds:
                        changes_to_process.append(file_path)
                
                for file_path in changes_to_process:
                    del self._pending_changes[file_path]
                
                if not self._pending_changes:
                    self._running = False
            
            for file_path in changes_to_process:
                try:
                    self.watcher._on_file_changed(file_path)
                except Exception as e:
                    logger.error(f"处理文件变化失败: {file_path}, error={e}")


class _ComponentFileHandlerWatchdog(_ComponentFileHandlerBase, FileSystemEventHandler):
    """文件变化处理器 - watchdog 版本"""
    
    def on_modified(self, event: Any) -> None:
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self._handle_change(file_path, WatchEvent.MODIFIED)
    
    def on_created(self, event: Any) -> None:
        """文件创建事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self._handle_change(file_path, WatchEvent.CREATED)
    
    def on_deleted(self, event: Any) -> None:
        """文件删除事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self._handle_change(file_path, WatchEvent.DELETED)


class _ComponentFileHandlerBasic(_ComponentFileHandlerBase):
    """文件变化处理器 - 基础版本"""


ComponentFileHandler: Any
if HAS_WATCHDOG:
    ComponentFileHandler = _ComponentFileHandlerWatchdog
else:
    ComponentFileHandler = _ComponentFileHandlerBasic


class ComponentWatcher:
    """组件监视器"""
    
    def __init__(
        self,
        config: WatchConfig,
        hot_loader: Optional[Any] = None,
    ):
        self.config = config
        self.hot_loader = hot_loader
        self._observer: Optional[Any] = None
        self._handler: Optional[Any] = None
        self._callbacks: List[Callable[[Path, WatchEvent], None]] = []
        self._watched_files: Set[Path] = set()
    
    def start(self) -> None:
        """启动监视器"""
        if not HAS_WATCHDOG or Observer is None:
            logger.warning("watchdog 库未安装，监视器不可用")
            return
        
        if self._observer and hasattr(self._observer, 'is_alive') and self._observer.is_alive():
            logger.warning("监视器已在运行")
            return
        
        self._observer = Observer()
        self._handler = ComponentFileHandler(self, self.config.debounce_seconds)
        
        for watch_dir in self.config.watch_dirs:
            watch_dir.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(self._handler, str(watch_dir), recursive=True)
            logger.info(f"开始监控目录: {watch_dir}")
        
        self._observer.start()
        logger.info("组件监视器已启动")
    
    def stop(self) -> None:
        """停止监视器"""
        if self._observer and hasattr(self._observer, 'is_alive') and self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=5.0)
            logger.info("组件监视器已停止")
    
    def add_callback(self, callback: Callable[[Path, WatchEvent], None]) -> None:
        """添加文件变化回调"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Path, WatchEvent], None]) -> bool:
        """移除文件变化回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False
    
    def watch_file(self, file_path: Path) -> None:
        """监控指定文件"""
        self._watched_files.add(file_path)
    
    def unwatch_file(self, file_path: Path) -> bool:
        """取消监控指定文件"""
        if file_path in self._watched_files:
            self._watched_files.remove(file_path)
            return True
        return False
    
    def _on_file_changed(self, file_path: Path) -> None:
        """文件变化处理"""
        if file_path.suffix not in self.config.file_extensions:
            return
        
        if self._watched_files and file_path not in self._watched_files:
            return
        
        logger.info(f"检测到文件变化: {file_path}")
        
        component_name = None
        if self.config.auto_reload and self.hot_loader:
            try:
                component_name = file_path.stem
                existing = self.hot_loader.get_component(component_name)
                if existing:
                    self.hot_loader.reload_component(component_name)
                    logger.info(f"组件已自动重新加载: {component_name}")
            except Exception as e:
                logger.error(f"自动重新加载失败: {component_name}, error={e}")
        
        for callback in self._callbacks:
            try:
                callback(file_path, WatchEvent.MODIFIED)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")


# 全局组件监视器实例（未启动，需手动配置和启动）
component_watcher: Optional[ComponentWatcher] = None

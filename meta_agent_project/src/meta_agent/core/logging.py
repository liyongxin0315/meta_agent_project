"""
日志系统模块 - 企业级实现
支持结构化日志、日志轮转、上下文关联
"""

import logging
import logging.handlers
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, fmt: str = "%(asctime)s %(levelname)s %(name)s %(message)s"):
        if HAS_JSON_LOGGER:
            self._json_formatter = jsonlogger.JsonFormatter(
                fmt, rename_fields={"levelname": "level", "asctime": "timestamp"}
            )
        else:
            self._json_formatter = None
        super().__init__(fmt)
    
    def format(self, record: logging.LogRecord) -> str:
        if self._json_formatter:
            return self._json_formatter.format(record)
        return super().format(record)


class ContextFilter(logging.Filter):
    """日志上下文过滤器"""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}
        if "request_id" not in self.context:
            self.context["request_id"] = str(uuid.uuid4())
    
    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
    
    def update_context(self, **kwargs: Any) -> None:
        """更新上下文"""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """清除上下文"""
        self.context.clear()
        self.context["request_id"] = str(uuid.uuid4())


_loggers: Dict[str, logging.Logger] = {}
_context_filter: Optional[ContextFilter] = None


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """
    设置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        structured: 是否使用结构化日志
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的备份文件数量
    """
    global _context_filter
    _context_filter = ContextFilter()
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()
    
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s"
        )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    if _context_filter:
        console_handler.addFilter(_context_filter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        if _context_filter:
            file_handler.addFilter(_context_filter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    return _loggers[name]


def update_log_context(**kwargs: Any) -> None:
    """更新日志上下文"""
    if _context_filter:
        _context_filter.update_context(**kwargs)


def clear_log_context() -> None:
    """清除日志上下文"""
    if _context_filter:
        _context_filter.clear_context()

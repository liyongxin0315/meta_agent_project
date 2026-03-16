# -*- coding: utf-8 -*-
"""
工具函数模块

提供常用的辅助函数。
"""

from datetime import datetime, timezone
from typing import Optional
import hashlib


def format_datetime(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间

    Args:
        dt: 日期时间对象，默认为当前 UTC 时间
        fmt: 格式化字符串

    Returns:
        格式化后的日期时间字符串
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime(fmt)


def generate_id(content: str) -> str:
    """
    生成唯一 ID

    Args:
        content: 用于生成 ID 的内容

    Returns:
        SHA256 哈希值（前 16 位）
    """
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def parse_bool(value: str) -> bool:
    """
    解析布尔值

    Args:
        value: 字符串值

    Returns:
        布尔值
    """
    return value.lower() in ("true", "1", "yes", "on")

# -*- coding: utf-8 -*-
"""
数据验证器
"""

from typing import Any, Optional


def validate_input(value: Any, required: bool = True, min_length: Optional[int] = None) -> bool:
    """
    验证输入值

    Args:
        value: 要验证的值
        required: 是否必填
        min_length: 最小长度（针对字符串）

    Returns:
        验证是否通过
    """
    if required and value is None:
        return False
    
    if min_length is not None and isinstance(value, str):
        return len(value) >= min_length
    
    return True

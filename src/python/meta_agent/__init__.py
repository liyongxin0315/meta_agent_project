"""
MetaAgent Python 核心包

提供跨语言调用的统一接口层。
"""

__version__ = "1.0.0"
__author__ = "liyongxin0315"

from .adapters.rust_adapter import RustCore
from .adapters.go_adapter import GoConcurrency

__all__ = ["RustCore", "GoConcurrency"]

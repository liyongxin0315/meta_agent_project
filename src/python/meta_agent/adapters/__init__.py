"""
跨语言适配器模块

提供与 Go/Rust/C++ 等语言的统一交互接口。
"""

from .rust_adapter import RustCore
from .go_adapter import GoConcurrency

__all__ = ["RustCore", "GoConcurrency"]

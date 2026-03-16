"""
配置加载模块

读取配置文件和环境变量。
"""

from .loader import load_config, Config

__all__ = ["load_config", "Config"]

# -*- coding: utf-8 -*-
"""
配置加载器 - 支持多环境

从 config/{env}/app.toml 读取配置，支持环境变量覆盖。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class Config:
    """配置数据类"""
    # 应用配置
    app_name: str = "MetaAgent"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # LLM 配置
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_timeout: int = 30
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


def load_config(env: Optional[str] = None, config_dir: Optional[str] = None) -> Config:
    """
    加载配置

    Args:
        env: 环境名称（default/prod/test），默认从 META_AGENT_ENV 环境变量读取
        config_dir: 配置文件目录，默认为项目根目录的 config/

    Returns:
        Config 对象

    Raises:
        FileNotFoundError: 配置文件不存在时
        tomllib.TOMLDecodeError: TOML 格式错误时
    """
    # 确定环境
    environment = env or os.getenv("META_AGENT_ENV", "default")
    
    # 确定配置目录
    if config_dir is None:
        # 尝试从项目根目录查找
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / environment
    else:
        config_path = Path(config_dir) / environment
    
    # 查找配置文件
    config_file = config_path / "app.toml"
    
    if not config_file.exists():
        # 降级到 default 配置
        config_file = config_path.parent / "default" / "app.toml"
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在：{config_file}")
    
    # 读取 TOML 配置
    with open(config_file, "rb") as f:
        toml_config = tomllib.load(f)
    
    # 合并环境变量覆盖
    env_config = _load_env_config()
    
    # 创建 Config 对象
    return Config(
        app_name=_get_nested(toml_config, "app.name", env_config.get("APP_NAME")),
        version=_get_nested(toml_config, "app.version", env_config.get("APP_VERSION")),
        environment=environment,
        debug=_get_nested(toml_config, "app.debug", False),
        log_level=_get_nested(toml_config, "logging.level", env_config.get("LOG_LEVEL", "INFO")),
        log_format=_get_nested(toml_config, "logging.format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
        llm_api_key=env_config.get("LLM_API_KEY"),
        llm_base_url=_get_nested(toml_config, "llm.base_url", env_config.get("LLM_BASE_URL")),
        llm_model=_get_nested(toml_config, "llm.model", "gpt-4"),
        llm_timeout=_get_nested(toml_config, "llm.timeout", 30),
        redis_host=_get_nested(toml_config, "redis.host", env_config.get("REDIS_HOST", "localhost")),
        redis_port=_get_nested(toml_config, "redis.port", int(env_config.get("REDIS_PORT", "6379"))),
        redis_db=_get_nested(toml_config, "redis.db", 0),
        redis_password=env_config.get("REDIS_PASSWORD"),
        host=_get_nested(toml_config, "server.host", "0.0.0.0"),
        port=_get_nested(toml_config, "server.port", 8000),
        workers=_get_nested(toml_config, "server.workers", 1),
    )


def _load_env_config() -> Dict[str, Any]:
    """从环境变量加载配置"""
    return {
        "APP_NAME": os.getenv("APP_NAME"),
        "APP_VERSION": os.getenv("APP_VERSION"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL"),
        "LLM_API_KEY": os.getenv("LLM_API_KEY"),
        "LLM_BASE_URL": os.getenv("LLM_BASE_URL"),
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD"),
    }


def _get_nested(data: Dict, key: str, default: Any = None) -> Any:
    """
    获取嵌套字典的值

    Args:
        data: 字典
        key: 点分隔的键路径（如 "app.name"）
        default: 默认值

    Returns:
        值或默认值
    """
    keys = key.split(".")
    value = data
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


# 全局配置实例（延迟加载）
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(env: Optional[str] = None) -> Config:
    """重新加载配置"""
    global _config
    _config = load_config(env)
    return _config

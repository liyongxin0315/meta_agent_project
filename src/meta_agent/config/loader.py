# -*- coding: utf-8 -*-
"""
配置加载器
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """配置数据类"""
    app_name: str = "MetaAgent"
    version: str = "1.0.0"
    log_level: str = "INFO"
    environment: str = "development"
    
    # LLM 配置
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000


def load_config(env: Optional[str] = None) -> Config:
    """
    加载配置

    Args:
        env: 环境名称（development/production/test），默认从环境变量读取

    Returns:
        Config 对象
    """
    environment = env or os.getenv("META_AGENT_ENV", "development")
    
    return Config(
        app_name=os.getenv("APP_NAME", "MetaAgent"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=environment,
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_base_url=os.getenv("LLM_BASE_URL"),
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )

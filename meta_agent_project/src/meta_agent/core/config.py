"""
配置管理模块 - 企业级实现
使用 Pydantic 进行类型安全的配置管理
支持多环境配置和环境变量覆盖
"""

from pathlib import Path
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, field

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

from meta_agent.core.exceptions import ConfigError
from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class EvolutionConfig:
    """进化配置"""
    defect_threshold: float = 0.8
    min_gain_delta: float = 0.01
    max_retries: int = 3
    snapshot_history: int = 5
    sandbox_timeout: int = 60
    max_memory_mb: int = 256
    llm_learning_enabled: bool = True


@dataclass
class UtilityConfig:
    """效用函数配置"""
    weights: Dict[str, float] = field(default_factory=lambda: {
        "task_success": 0.5,
        "efficiency": 0.3,
        "resource_usage": 0.2
    })
    baseline_window: int = 5


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    enable_cache: bool = True
    enable_rate_limit: bool = True


@dataclass
class CacheConfig:
    """缓存配置"""
    max_size: int = 1000
    default_ttl: int = 3600
    strategy: str = "HYBRID"
    redis_url: Optional[str] = None


@dataclass
class RateLimitConfig:
    """限流配置"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    strategy: str = "TOKEN_BUCKET"


@dataclass
class SecurityConfig:
    """安全配置"""
    enable_sandbox: bool = True
    enable_code_validation: bool = True
    max_execution_timeout: int = 300
    allowed_modules: List[str] = field(default_factory=list)


@dataclass
class MonitoringConfig:
    """监控配置"""
    enable_metrics: bool = True
    enable_tracing: bool = True
    prometheus_port: int = 9090
    otlp_endpoint: Optional[str] = None


class Config(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="META_AGENT_",
        extra="ignore"
    )

    environment: Environment = Field(default=Environment.DEVELOPMENT)
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    log_level: str = "INFO"

    evolution: EvolutionConfig = Field(default_factory=EvolutionConfig)
    utility: UtilityConfig = Field(default_factory=UtilityConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    @field_validator("project_root")
    @classmethod
    def resolve_project_root(cls, v: Any) -> Path:
        """解析项目根目录"""
        if isinstance(v, str):
            return Path(v).resolve()
        return v.resolve()

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        """从 YAML 文件加载配置"""
        try:
            import yaml
        except ImportError:
            raise ConfigError("PyYAML 未安装，请使用 pip install pyyaml")
        
        if not config_path.exists():
            return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            
            return cls(**config_data)
        except yaml.YAMLError as e:
            raise ConfigError(f"YAML 配置文件解析失败: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "environment": self.environment.value,
            "project_root": str(self.project_root),
            "log_level": self.log_level,
            "evolution": {
                "defect_threshold": self.evolution.defect_threshold,
                "min_gain_delta": self.evolution.min_gain_delta,
                "max_retries": self.evolution.max_retries,
                "snapshot_history": self.evolution.snapshot_history,
                "sandbox_timeout": self.evolution.sandbox_timeout,
                "max_memory_mb": self.evolution.max_memory_mb,
                "llm_learning_enabled": self.evolution.llm_learning_enabled,
            },
            "llm": {
                "default_model": self.llm.default_model,
                "default_temperature": self.llm.default_temperature,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries,
                "enable_cache": self.llm.enable_cache,
                "enable_rate_limit": self.llm.enable_rate_limit,
            },
        }


_global_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config) -> None:
    """设置全局配置"""
    global _global_config
    _global_config = config

"""
异常体系模块 - 企业级实现
定义完整的异常层级结构和错误码
"""

from typing import Optional, Any, Dict
from enum import Enum
from dataclasses import dataclass


class ErrorCode(Enum):
    """错误码枚举"""
    CONFIG_ERROR = "E001"
    SECURITY_ERROR = "E002"
    EVOLUTION_FAILED = "E003"
    LLM_CALL_FAILED = "E004"
    RATE_LIMIT_EXCEEDED = "E005"
    CACHE_ERROR = "E006"
    HOTLOAD_ERROR = "E007"
    DEPENDENCY_INJECTION_ERROR = "E008"
    SANDBOX_ERROR = "E009"
    NETWORK_ERROR = "E010"
    TIMEOUT_ERROR = "E011"
    VALIDATION_ERROR = "E012"
    INTERNAL_ERROR = "E999"


@dataclass
class ErrorContext:
    """错误上下文信息"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0


class MetaAgentError(Exception):
    """MetaAgent 基础异常"""
    
    def __init__(
        self, message: str, code: ErrorCode = ErrorCode.INTERNAL_ERROR, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
        }


class ConfigError(MetaAgentError):
    """配置错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.CONFIG_ERROR, details)


class SecurityError(MetaAgentError):
    """安全错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.SECURITY_ERROR, details)


class EvolutionError(MetaAgentError):
    """进化错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.EVOLUTION_FAILED, details)


class LLMCallError(MetaAgentError):
    """LLM 调用错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.LLM_CALL_FAILED, details)


class RateLimitError(MetaAgentError):
    """限流错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED, details)


class CacheError(MetaAgentError):
    """缓存错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.CACHE_ERROR, details)


class HotLoadError(MetaAgentError):
    """热加载错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.HOTLOAD_ERROR, details)


class DependencyInjectionError(MetaAgentError):
    """依赖注入错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.DEPENDENCY_INJECTION_ERROR, details)


class SandboxError(MetaAgentError):
    """沙箱错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.SANDBOX_ERROR, details)


class NetworkError(MetaAgentError):
    """网络错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.NETWORK_ERROR, details)


class TimeoutError(MetaAgentError):
    """超时错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.TIMEOUT_ERROR, details)


class ValidationError(MetaAgentError):
    """验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)

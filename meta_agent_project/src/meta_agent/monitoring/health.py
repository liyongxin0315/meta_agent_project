"""
健康检查 - 企业级实现
提供健康检查端点和探针机制
"""

import threading
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """健康检查项"""
    name: str
    check_func: Callable[[], bool]
    timeout_seconds: float = 5.0
    critical: bool = True
    last_check_time: Optional[float] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None


@dataclass
class HealthResult:
    """健康检查结果"""
    status: HealthStatus
    checks: Dict[str, Dict[str, Any]]
    timestamp: float
    version: str


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self._checks: Dict[str, HealthCheck] = {}
        self._lock = threading.Lock()
    
    def add_check(
        self,
        name: str,
        check_func: Callable[[], bool],
        timeout_seconds: float = 5.0,
        critical: bool = True,
    ) -> None:
        """添加健康检查"""
        with self._lock:
            self._checks[name] = HealthCheck(
                name=name,
                check_func=check_func,
                timeout_seconds=timeout_seconds,
                critical=critical,
            )
            logger.info(f"添加健康检查: {name}")
    
    def remove_check(self, name: str) -> bool:
        """移除健康检查"""
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                logger.info(f"移除健康检查: {name}")
                return True
            return False
    
    def check_liveness(self) -> bool:
        """检查存活状态"""
        try:
            result = self._run_checks()
            return result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        except Exception as e:
            logger.error(f"存活检查失败: {e}")
            return False
    
    def check_readiness(self) -> bool:
        """检查就绪状态"""
        try:
            result = self._run_checks()
            return result.status == HealthStatus.HEALTHY
        except Exception as e:
            logger.error(f"就绪检查失败: {e}")
            return False
    
    def _run_checks(self) -> HealthResult:
        """运行所有检查"""
        checks_result: Dict[str, Dict[str, Any]] = {}
        healthy_count = 0
        critical_failed = False
        
        with self._lock:
            checks_to_run = list(self._checks.items())
        
        for name, check in checks_to_run:
            try:
                start_time = datetime.now(timezone.utc).timestamp()
                is_healthy = check.check_func()
                duration = datetime.now(timezone.utc).timestamp() - start_time
                
                status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
                
                with self._lock:
                    check.last_status = status
                    check.last_check_time = datetime.now(timezone.utc).timestamp()
                    check.last_error = None
                
                if is_healthy:
                    healthy_count += 1
                elif check.critical:
                    critical_failed = True
                
                checks_result[name] = {
                    "status": status.value,
                    "duration_seconds": duration,
                    "healthy": is_healthy,
                    "critical": check.critical,
                }
            except Exception as e:
                with self._lock:
                    check.last_status = HealthStatus.UNHEALTHY
                    check.last_check_time = datetime.now(timezone.utc).timestamp()
                    check.last_error = str(e)
                
                if check.critical:
                    critical_failed = True
                
                checks_result[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "healthy": False,
                    "critical": check.critical,
                    "error": str(e),
                }
        
        if critical_failed:
            overall_status = HealthStatus.UNHEALTHY
        elif healthy_count == len(checks_to_run):
            overall_status = HealthStatus.HEALTHY
        elif healthy_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        return HealthResult(
            status=overall_status,
            checks=checks_result,
            timestamp=datetime.now(timezone.utc).timestamp(),
            version=self.version,
        )
    
    def get_health(self) -> HealthResult:
        """获取健康状态"""
        return self._run_checks()
    
    def get_health_dict(self) -> Dict[str, Any]:
        """获取健康状态字典"""
        result = self.get_health()
        return {
            "status": result.status.value,
            "version": result.version,
            "timestamp": result.timestamp,
            "checks": result.checks,
        }


# 全局健康检查器实例
health_checker = HealthChecker()

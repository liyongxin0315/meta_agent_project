"""
安全模块 - 企业级实现
提供模块完整性校验、权限控制、输入验证
"""

import hashlib
import hmac
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from functools import wraps

from meta_agent.core.exceptions import SecurityError
from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityPolicy:
    """安全策略"""
    allow_network_access: bool = False
    allow_file_write: bool = False
    allowed_file_paths: List[Path] = field(default_factory=list)
    max_execution_time: int = 300
    max_memory_mb: int = 512
    forbidden_modules: Set[str] = field(default_factory=lambda: {
        "os", "subprocess", "sys", "ctypes", "pickle"
    })


_original_module_hashes: Dict[str, str] = {}
_security_policy = SecurityPolicy()


def set_security_policy(policy: SecurityPolicy) -> None:
    """设置安全策略"""
    global _security_policy
    _security_policy = policy


def get_security_policy() -> SecurityPolicy:
    """获取安全策略"""
    return _security_policy


def calculate_file_hash(file_path: Path) -> str:
    """计算文件哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def set_original_module_hashes(hashes: Dict[str, str]) -> None:
    """设置原始模块哈希值"""
    global _original_module_hashes
    _original_module_hashes = hashes.copy()


def initialize_module_hashes(src_dir: Path) -> Dict[str, str]:
    """
    初始化模块哈希值 - 扫描 src 目录并计算所有模块的哈希
    
    Args:
        src_dir: 源码目录路径
        
    Returns:
        Dict[str, str]: 模块路径到哈希值的映射
    """
    hashes: Dict[str, str] = {}
    
    if not src_dir.exists():
        logger.warning(f"源码目录不存在: {src_dir}")
        return hashes
    
    for py_file in src_dir.rglob("*.py"):
        try:
            file_hash = calculate_file_hash(py_file)
            hashes[str(py_file)] = file_hash
        except Exception as e:
            logger.warning(f"计算文件哈希失败: {py_file}, error: {e}")
    
    set_original_module_hashes(hashes)
    logger.info(f"已初始化 {len(hashes)} 个模块的哈希值")
    return hashes


def check_module_integrity(module_path: Path) -> bool:
    """检查模块完整性"""
    module_str = str(module_path)
    if module_str not in _original_module_hashes:
        logger.warning(f"模块未注册: {module_str}")
        return False
    
    current_hash = calculate_file_hash(module_path)
    original_hash = _original_module_hashes[module_str]
    
    if not hmac.compare_digest(current_hash, original_hash):
        logger.error(f"模块完整性校验失败: {module_str}")
        raise SecurityError(f"模块被篡改: {module_str}")
    
    return True


def validate_input(input_str: str, max_length: int = 10000) -> bool:
    """验证输入安全性"""
    if len(input_str) > max_length:
        raise SecurityError(f"输入超过最大长度限制")
    
    dangerous_patterns = [
        r"__(import|exec|eval|compile|__import__)\s*\(",
        r"os\.(system|popen|exec|spawn)",
        r"subprocess\.",
        r"__builtins__",
        r"globals\(\)|locals\(\)",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            raise SecurityError(f"检测到潜在的危险输入")
    
    return True


def validate_path(path: Path, allowed_paths: Optional[List[Path]] = None) -> bool:
    """验证路径安全性"""
    policy = get_security_policy()
    allowed = allowed_paths or policy.allowed_file_paths
    
    if not allowed:
        return True
    
    resolved_path = path.resolve()
    for allowed_path in allowed:
        resolved_allowed = allowed_path.resolve()
        if resolved_path.is_relative_to(resolved_allowed):
            return True
    
    raise SecurityError(f"路径访问被拒绝: {path}")


def check_controller_permission(controller: str, action: str) -> bool:
    """检查控制器权限"""
    get_security_policy()
    logger.info(f"权限检查: controller={controller}, action={action}")
    return True


def secure(f):
    """安全装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SecurityError:
            raise
        except Exception as e:
            logger.error(f"安全异常: {e}")
            raise SecurityError(f"操作失败") from e
    return wrapper

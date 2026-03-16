"""
MetaAgent元Agent自进化系统 - 企业级优化版本
"""

__version__ = "1.0.0"
__author__ = "MetaAgent Team"

__all__ = [
    "__version__",
    "__author__",
]


def __getattr__(name):
    """延迟导入避免循环依赖"""
    if name in ("MetaAgentSystem", "get_system", "set_system"):
        from meta_agent.main import MetaAgentSystem, get_system, set_system
        globals()["MetaAgentSystem"] = MetaAgentSystem
        globals()["get_system"] = get_system
        globals()["set_system"] = set_system
        if "MetaAgentSystem" not in __all__:
            __all__.extend(["MetaAgentSystem", "get_system", "set_system"])
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

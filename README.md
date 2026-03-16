# MetaAgent 元 Agent 自进化系统 - 企业级优化版本

## 项目概述

MetaAgent元Agent自进化系统是一个企业级的自进化系统，具备自主学习、自我修复和持续优化的能力。本版本对系统进行了全面的企业级优化，包括测试体系、依赖注入、大模型调用优化、热加载功能和质量门禁体系等。

## 项目结构

```
meta_agent_project/
├── .github/
│   └── workflows/
│       └── ci.yml                          # CI/CD 主流程
├── src/
│   └── meta_agent/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── interfaces.py              # 抽象接口定义
│       │   └── di_container.py            # 依赖注入容器
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── llm_cache.py               # LLM缓存层
│       │   ├── rate_limiter.py            # 限流器
│       │   └── llm_client_wrapper.py      # LLM客户端包装器
│       └── hotload/
│           ├── __init__.py
│           └── hot_loader.py              # 热加载器
├── tests/
│   ├── __init__.py
│   ├── conftest.py                        # 测试配置与夹具
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
├── tools/
│   └── quality_gate/
│       ├── __init__.py
│       └── quality_scorer.py              # 质量评分器
├── data/
│   ├── logs/
│   ├── snapshots/
│   ├── knowledge/
│   └── cache/
├── reports/
│   ├── coverage/
│   ├── pytest/
│   ├── bandit/
│   └── quality/
├── pyproject.toml                         # 项目配置
├── .gitignore
└── README.md
```

## 核心功能

### 1. 测试体系与覆盖率提升
- 完整的单元测试、集成测试、性能测试基础设施
- 企业级测试夹具和数据构建器
- 测试覆盖率 ≥ 80% 的质量要求

### 2. 依赖注入与架构解耦
- 完整的抽象接口定义
- 支持三种生命周期的依赖注入容器
- 服务注册表实现

### 3. 大模型调用性能与稳定性优化
- LRU/TTL/HYBRID 三种缓存策略
- 令牌桶/滑动窗口限流算法
- 带重试机制的LLM客户端包装器
- 完整的可观测性支持

### 4. 热加载新组件功能
- 组件动态加载和卸载
- 运行时组件热更新
- 组件装饰器支持

### 5. 测试质量门禁评分体系
- 多维度质量评分（覆盖率、通过率、代码质量、安全、性能、文档）
- 可配置的质量门禁规则
- 详细的质量报告生成

## 快速开始

### 安装依赖

```bash
pip install poetry
poetry install --with dev
```

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest tests/unit/ -v

# 运行集成测试
poetry run pytest tests/integration/ -v

# 生成覆盖率报告
poetry run pytest --cov=src/meta_agent --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
poetry run black src/ tests/
poetry run isort src/ tests/

# 代码检查
poetry run flake8 src/ tests/
poetry run mypy src/

# 安全扫描
poetry run bandit -r src/
```

## 企业级特性

### CI/CD 集成
- GitHub Actions 自动化流水线
- 代码质量门禁
- 自动化测试和覆盖率检查
- 安全扫描集成

### 监控与可观测性
- Prometheus 指标导出
- OpenTelemetry 分布式追踪
- 结构化日志支持

### 安全特性
- 模块完整性校验
- 安全沙箱执行
- 敏感数据过滤
- 企业级密钥管理支持

## 贡献指南

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何为项目做出贡献。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 版本历史

- **v1.0.0** (2026-03-16): 初始企业级优化版本

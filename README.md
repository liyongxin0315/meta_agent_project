# MetaAgent 元 Agent 自进化系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **企业级自进化系统** - 具备自主学习、自我修复和持续优化能力

---

## 📖 目录

- [项目概述](#-项目概述)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
- [Docker 部署](#-docker-部署)
- [配置说明](#-配置说明)
- [开发指南](#-开发指南)
- [测试](#-测试)
- [监控](#-监控)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📋 项目概述

MetaAgent 是一个企业级的元 Agent 自进化系统，具备以下特性：

- **🧠 自主学习** - 从任务执行中持续学习和优化
- **🔧 自我修复** - 自动检测和修复系统问题
- **📈 持续优化** - 基于反馈循环不断改进
- **🔌 热加载** - 支持运行时动态加载新组件
- **🛡️ 安全合规** - 企业级安全控制和审计

### 技术栈

- **Python 3.10+** - 核心运行时
- **Poetry** - 依赖管理
- **Redis** - 缓存和消息队列
- **Prometheus + Grafana** - 监控和可视化
- **OpenTelemetry** - 分布式追踪

---

## ✨ 核心功能

### 1. 测试体系与覆盖率

- ✅ 完整的单元测试、集成测试、性能测试
- ✅ 企业级测试夹具和数据构建器
- ✅ 测试覆盖率 ≥ 80%

### 2. 依赖注入与架构解耦

- ✅ 完整的抽象接口定义
- ✅ 支持三种生命周期的 DI 容器
- ✅ 服务注册表

### 3. 大模型调用优化

- ✅ LRU/TTL/HYBRID 三种缓存策略
- ✅ 令牌桶/滑动窗口限流
- ✅ 带重试机制的 LLM 客户端
- ✅ 完整的可观测性支持

### 4. 热加载功能

- ✅ 组件动态加载/卸载
- ✅ 运行时热更新
- ✅ 组件装饰器支持

### 5. 质量门禁体系

- ✅ 多维度质量评分
- ✅ 可配置的门禁规则
- ✅ 详细的质量报告

---

## 🚀 快速开始

### 前置要求

- Python 3.10+ ([版本说明](README_PYTHON_VERSION.md))
- Poetry 1.5+
- Redis 7+ (可选，用于缓存)

### 安装依赖

```bash
# 安装 Poetry（如未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 克隆仓库
git clone https://github.com/liyongxin0315/meta_agent_project.git
cd meta_agent_project

# 安装依赖
poetry install --with dev
```

### 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填写 API 密钥等配置
# 至少需要配置 OPENAI_API_KEY
```

### 运行应用

```bash
# 开发模式
poetry run python -m meta_agent

# 生产模式
poetry run python -m meta_agent --environment production
```

---

## 🐳 Docker 部署

### 快速启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f metaagent

# 停止服务
docker-compose down
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| MetaAgent | 9090 | Prometheus 指标 |
| Redis | 6379 | 缓存服务 |
| Prometheus | 9091 | 监控面板 |
| Grafana | 3000 | 可视化面板 (admin/admin123) |

### 自定义配置

```bash
# 使用自定义配置启动
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `META_AGENT_ENVIRONMENT` | 运行环境 | `production` |
| `META_AGENT_LOG_LEVEL` | 日志级别 | `INFO` |
| `REDIS_HOST` | Redis 主机 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |

详细配置请参考 [.env.example](.env.example)。

---

## 🛠️ 开发指南

### 代码格式化

```bash
# 格式化代码
poetry run black src/ tests/

# 排序导入
poetry run isort src/ tests/
```

### 代码检查

```bash
# 静态检查
poetry run flake8 src/ tests/

# 类型检查
poetry run mypy src/

# 安全扫描
poetry run bandit -r src/
```

### 添加新组件

```python
# 1. 创建新组件
from meta_agent.hotload import component

@component
class MyComponent:
    """我的自定义组件"""
    
    def execute(self, data: dict) -> dict:
        return {"result": "success"}

# 2. 组件会自动被热加载器发现
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest tests/unit/ -v

# 运行集成测试
poetry run pytest tests/integration/ -v

# 运行特定测试
poetry run pytest tests/unit/test_llm_cache.py -v
```

### 生成覆盖率报告

```bash
# 终端报告
poetry run pytest --cov=src/meta_agent

# HTML 报告
poetry run pytest --cov=src/meta_agent --cov-report=html

# XML 报告（CI 集成）
poetry run pytest --cov=src/meta_agent --cov-report=xml
```

### 测试质量门禁

```bash
# 运行质量检查
poetry run python tools/quality_gate/quality_scorer.py
```

---

## 📊 监控

### Prometheus 指标

访问 `http://localhost:9090/metrics` 查看指标。

### Grafana 面板

1. 访问 `http://localhost:3000`
2. 登录：`admin` / `admin123`
3. 添加 Prometheus 数据源：`http://prometheus:9090`
4. 导入预设仪表板

### 关键指标

- `meta_agent_requests_total` - 请求总数
- `meta_agent_request_duration_seconds` - 请求延迟
- `meta_agent_llm_cache_hits_total` - LLM 缓存命中
- `meta_agent_component_loads_total` - 组件加载次数

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [PEP 8](https://pep8.org/) 代码规范
- 使用 [Black](https://black.readthedocs.io/) 格式化代码
- 编写单元测试覆盖新功能
- 更新文档

详细贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

```
Copyright (c) 2024 liyongxin0315

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 📞 联系方式

- **作者**: liyongxin0315
- **GitHub**: https://github.com/liyongxin0315
- **Issues**: https://github.com/liyongxin0315/meta_agent_project/issues

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者们！

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

[⬆ 返回顶部](#metaagent-元-agent-自进化系统)

</div>

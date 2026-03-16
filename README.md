# MetaAgent 元 Agent 自进化系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **企业级自进化系统** - 具备自主学习、自我修复和持续优化能力

---

## 📖 目录

- [快速开始](#-快速开始)
- [目录结构](#-目录结构)
- [配置说明](#-配置说明)
- [开发指南](#-开发指南)
- [测试](#-测试)
- [部署](#-部署)
- [贡献指南](#-贡献指南)

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Poetry 1.5+
- Redis 7+ (可选)

### 安装

```bash
# 克隆仓库
git clone https://github.com/liyongxin0315/meta_agent_project.git
cd meta_agent_project

# 安装依赖
poetry install --with dev

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写 API 密钥等配置
```

### 运行

```bash
# 开发模式
poetry run python -m meta_agent

# 生产模式
META_AGENT_ENV=production poetry run python -m meta_agent
```

---

## 📁 目录结构

```
meta_agent_project/
├── src/
│   └── meta_agent/          # 核心源代码
│       ├── __init__.py
│       ├── core/            # 核心逻辑（Agent 调度、任务处理）
│       ├── utils/           # 通用工具函数
│       ├── models/          # 数据模型
│       ├── api/             # 接口层（HTTP/gRPC/CLI）
│       └── config/          # 配置加载逻辑
├── tests/
│   ├── conftest.py         # pytest 配置
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
├── config/
│   ├── default/            # 开发环境配置
│   ├── prod/               # 生产环境配置
│   └── test/               # 测试环境配置
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── start.sh
├── docs/
│   ├── api/                # API 文档
│   └── design/             # 设计文档
├── scripts/                # 运维脚本
├── tools/                  # 工程化工具
├── .env.example            # 环境变量模板
├── pyproject.toml          # Python 项目配置
└── README.md
```

### 核心模块说明

| 目录 | 用途 | 说明 |
|------|------|------|
| `src/meta_agent/core` | 核心逻辑 | Agent 调度、任务处理、决策 |
| `src/meta_agent/utils` | 工具函数 | 时间、字符串、验证等 |
| `src/meta_agent/models` | 数据模型 | 实体类、DTO、数据库模型 |
| `src/meta_agent/api` | 接口层 | HTTP/gRPC/CLI 接口 |
| `src/meta_agent/config` | 配置 | 配置加载逻辑 |
| `config/` | 配置文件 | 按环境拆分的配置文件 |
| `tests/` | 测试 | 单元/集成/端到端测试 |

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `META_AGENT_ENV` | 运行环境 | `development` |
| `LLM_API_KEY` | LLM API 密钥 | 必填 |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.openai.com/v1` |
| `REDIS_HOST` | Redis 主机 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `PORT` | 服务端口 | `8000` |

详细配置请参考 [.env.example](.env.example)。

### 配置文件

配置文件位于 `config/` 目录，按环境拆分：

- `config/default/` - 开发环境默认配置
- `config/prod/` - 生产环境配置
- `config/test/` - 测试环境配置

---

## 🛠️ 开发指南

### 代码规范

遵循 [PEP 8](https://pep8.org/) 规范：

```bash
# 格式化代码
poetry run black src/ tests/

# 排序导入
poetry run isort src/ tests/

# 代码检查
poetry run flake8 src/ tests/
```

### 类型检查

```bash
# 运行 mypy
poetry run mypy src/
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

# 生成覆盖率报告
poetry run pytest --cov=src/meta_agent --cov-report=html
```

### 测试结构

| 目录 | 用途 |
|------|------|
| `tests/unit/` | 单元测试（单个模块） |
| `tests/integration/` | 集成测试（模块间交互） |
| `tests/e2e/` | 端到端测试（完整流程） |

---

## 🐳 部署

### Docker 部署

```bash
# 构建镜像
docker build -f docker/Dockerfile -t meta_agent:latest .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境

```bash
# 使用生产配置
META_AGENT_ENV=production poetry run python -m meta_agent

# 或使用 Docker
docker-compose -f docker/compose.prod.yml up -d
```

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详细贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **作者**: liyongxin0315
- **GitHub**: https://github.com/liyongxin0315
- **Issues**: https://github.com/liyongxin0315/meta_agent_project/issues

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

[⬆ 返回顶部](#metaagent-元-agent-自进化系统)

</div>

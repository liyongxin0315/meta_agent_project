# =============================================================================
# MetaAgent Dockerfile - 生产环境
# =============================================================================
# 多阶段构建，优化镜像体积和安全性
# 基础镜像：Python 3.10-slim（固定版本，避免版本漂移）
# =============================================================================

FROM python:3.10-slim as base

WORKDIR /app

# 安装系统依赖（最小化安装）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry - 使用官方推荐方式
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

# =============================================================================
# 构建阶段 - 安装依赖
# =============================================================================
FROM base as builder

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# =============================================================================
# 生产阶段 - 最小化运行环境
# =============================================================================
FROM base as production

# 复制虚拟环境
COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

# 复制源代码和配置
COPY src/ ./src/
COPY config/ ./config/

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -u 1000 metaagent
RUN chown -R metaagent:metaagent /app
USER metaagent

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 暴露 Prometheus 监控端口
EXPOSE 9090

# 启动命令
CMD ["python", "-m", "meta_agent"]

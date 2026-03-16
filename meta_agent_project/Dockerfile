# 多阶段构建 - 生产环境
FROM python:3.10-slim as base

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry - 使用官方推荐方式
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

# 构建阶段
FROM base as builder

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# 生产阶段
FROM base as production

COPY --from=builder /app/.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/
COPY config/ ./config/

# 创建非 root 用户
RUN useradd -m -u 1000 metaagent
RUN chown -R metaagent:metaagent /app
USER metaagent

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 暴露 Prometheus 端口
EXPOSE 9090

CMD ["python", "-m", "meta_agent"]

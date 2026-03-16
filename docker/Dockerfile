# =============================================================================
# MetaAgent Dockerfile - 生产环境
# =============================================================================
# 基于 Python 3.10-slim，适配新目录结构
# =============================================================================

FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

# 复制项目文件（适配新目录结构）
COPY pyproject.toml poetry.lock* ./
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY docker/start.sh ./scripts/

# 安装 Python 依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -u 1000 metaagent
RUN chown -R metaagent:metaagent /app
USER metaagent

# 设置环境变量
ENV META_AGENT_ENV=production
ENV PYTHONPATH=/app/src:$PYTHONPATH

# 暴露端口
EXPOSE 8000 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "from meta_agent.config import load_config; load_config()" || exit 1

# 启动命令
CMD ["python", "-m", "meta_agent"]

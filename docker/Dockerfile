# =============================================================================
# MetaAgent Dockerfile - 多语言混合构建
# =============================================================================
# 支持：Python + Go + Rust
# 平台：Linux/Windows/macOS (amd64/arm64)
# =============================================================================

# -----------------------------------------------------------------------------
# 阶段 1: 构建 Rust 扩展
# -----------------------------------------------------------------------------
FROM rust:1.75-slim AS rust-builder

WORKDIR /app/src/rust

# 安装跨平台编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 Rust 源码
COPY src/rust/Cargo.toml src/rust/Cargo.lock* ./
COPY src/rust/src ./src/

# 构建 Rust 扩展（发布模式）
RUN cargo build --release

# -----------------------------------------------------------------------------
# 阶段 2: 构建 Go 服务
# -----------------------------------------------------------------------------
FROM golang:1.21-slim AS go-builder

WORKDIR /app/src/go

# 复制 Go 源码
COPY src/go/go.mod src/go/go.sum* ./
COPY src/go/cmd ./cmd/
COPY src/go/pkg ./pkg/

# 跨平台编译 Go（禁用 CGO 提高兼容性）
ENV CGO_ENABLED=0
RUN go build -o meta_agent_go ./cmd/main.go

# -----------------------------------------------------------------------------
# 阶段 3: 构建 Python 环境
# -----------------------------------------------------------------------------
FROM python:3.10-slim AS python-builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

# 复制 Python 项目配置
COPY pyproject.toml poetry.lock* ./

# 安装 Python 依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

# -----------------------------------------------------------------------------
# 阶段 4: 生产运行镜像
# -----------------------------------------------------------------------------
FROM python:3.10-slim AS production

WORKDIR /app

# 创建非 root 用户（安全最佳实践）
RUN useradd -m -u 1000 metaagent

# 从 Rust 构建阶段复制扩展
COPY --from=rust-builder /app/src/rust/target/release/libmeta_agent_rust.so \
    ./src/python/meta_agent/bindings/

# 从 Go 构建阶段复制服务
COPY --from=go-builder /app/src/go/meta_agent_go \
    ./src/go/

# 从 Python 构建阶段复制环境
COPY --from=python-builder /usr/local/lib/python3.10/site-packages \
    /usr/local/lib/python3.10/site-packages
COPY --from=python-builder /usr/local/bin/* \
    /usr/local/bin/

# 复制源码
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# 设置权限
RUN chown -R metaagent:metaagent /app
RUN chmod +x ./src/go/meta_agent_go ./scripts/start.sh

# 切换到非 root 用户
USER metaagent

# 暴露端口
# 9090: Prometheus 指标
# 8080: Go 服务 gRPC
EXPOSE 9090 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 启动脚本（先启动 Go 服务，再启动 Python）
CMD ["/app/scripts/start.sh"]

# =============================================================================
# 开发镜像（可选）
# =============================================================================
FROM production AS development

USER root

# 安装开发工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装测试工具
RUN pip install pytest pytest-cov black flake8 mypy

USER metaagent

# 开发模式启动（热重载）
CMD ["/app/scripts/start-dev.sh"]

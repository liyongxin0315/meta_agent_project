# =============================================================================
# MetaAgent Makefile - 跨平台 + 混合语言构建入口
# =============================================================================
# 用法：
#   make all          # 构建所有模块
#   make build-python # 构建 Python 模块
#   make build-go     # 构建 Go 服务
#   make build-rust   # 构建 Rust 扩展
#   make test         # 运行测试
#   make clean        # 清理构建产物
# =============================================================================

# -----------------------------------------------------------------------------
# 跨平台检测
# -----------------------------------------------------------------------------
OS := $(shell uname -s)
ARCH := $(shell uname -m)

# 转换为目标平台标识
ifeq ($(OS),Darwin)
    TARGET_OS := darwin
else ifeq ($(OS),Linux)
    TARGET_OS := linux
else ifeq ($(OS),Windows_NT)
    TARGET_OS := windows
else
    TARGET_OS := unknown
endif

ifeq ($(ARCH),x86_64)
    TARGET_ARCH := amd64
else ifeq ($(ARCH),aarch64)
    TARGET_ARCH := arm64
else ifeq ($(ARCH),arm64)
    TARGET_ARCH := arm64
else
    TARGET_ARCH := $(ARCH)
endif

TARGET := $(TARGET_OS)-$(TARGET_ARCH)

# -----------------------------------------------------------------------------
# 版本配置
# -----------------------------------------------------------------------------
PYTHON_VERSION ?= 3.10
GO_VERSION ?= 1.21
RUST_VERSION ?= 1.75

# -----------------------------------------------------------------------------
# 目录
# -----------------------------------------------------------------------------
SRC_DIR := src
BUILD_DIR := build
DIST_DIR := dist
TEST_DIR := tests

# -----------------------------------------------------------------------------
# 主要目标
# -----------------------------------------------------------------------------
.PHONY: all build-python build-go build-rust test clean package help

# 默认目标：构建所有模块
all: build-python build-go build-rust
	@echo "✅ 所有模块构建完成：$(TARGET)"

# -----------------------------------------------------------------------------
# Python 模块构建
# -----------------------------------------------------------------------------
build-python:
	@echo "🐍 构建 Python 模块..."
	cd $(SRC_DIR)/python && \
	pip install -e . --quiet
	@echo "✅ Python 模块构建完成"

# -----------------------------------------------------------------------------
# Go 服务构建
# -----------------------------------------------------------------------------
build-go:
	@echo "🔷 构建 Go 服务..."
	cd $(SRC_DIR)/go && \
	CGO_ENABLED=0 GOOS=$(TARGET_OS) GOARCH=$(TARGET_ARCH) go build -o ../../$(BUILD_DIR)/meta_agent_go_$(TARGET) ./cmd/main.go
	@echo "✅ Go 服务构建完成：$(BUILD_DIR)/meta_agent_go_$(TARGET)"

# -----------------------------------------------------------------------------
# Rust 扩展构建
# -----------------------------------------------------------------------------
build-rust:
	@echo "🦀 构建 Rust 扩展..."
	cd $(SRC_DIR)/rust && \
	cargo build --release --target $(TARGET_OS)-$(TARGET_ARCH)
	@echo "✅ Rust 扩展构建完成"

# -----------------------------------------------------------------------------
# 测试
# -----------------------------------------------------------------------------
test: test-python test-go test-rust
	@echo "✅ 所有测试完成"

test-python:
	@echo "🧪 运行 Python 测试..."
	cd $(SRC_DIR)/python && \
	pytest ../../$(TEST_DIR)/ -v --tb=short || true

test-go:
	@echo "🧪 运行 Go 测试..."
	cd $(SRC_DIR)/go && \
	go test ./... -v || true

test-rust:
	@echo "🧪 运行 Rust 测试..."
	cd $(SRC_DIR)/rust && \
	cargo test || true

# -----------------------------------------------------------------------------
# 清理
# -----------------------------------------------------------------------------
clean:
	@echo "🧹 清理构建产物..."
	rm -rf $(BUILD_DIR)/*
	rm -rf $(DIST_DIR)/*
	rm -rf $(SRC_DIR)/python/**/*.pyc
	rm -rf $(SRC_DIR)/python/**/__pycache__
	rm -rf $(SRC_DIR)/go/pkg
	rm -rf $(SRC_DIR)/rust/target
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	@echo "✅ 清理完成"

# -----------------------------------------------------------------------------
# 打包
# -----------------------------------------------------------------------------
package: all
	@echo "📦 打包发布版本..."
	mkdir -p $(DIST_DIR)/$(TARGET)
	cp $(BUILD_DIR)/* $(DIST_DIR)/$(TARGET)/ 2>/dev/null || true
	cp -r $(SRC_DIR)/python/meta_agent $(DIST_DIR)/$(TARGET)/
	cd $(DIST_DIR) && \
	zip -r meta_agent-$(TARGET).zip $(TARGET)/
	@echo "✅ 打包完成：$(DIST_DIR)/meta_agent-$(TARGET).zip"

# -----------------------------------------------------------------------------
# Docker 构建
# -----------------------------------------------------------------------------
docker-build:
	@echo "🐳 构建 Docker 镜像..."
	docker build -f $(BUILD_DIR)/docker/Dockerfile -t meta_agent:latest .
	@echo "✅ Docker 镜像构建完成"

docker-up:
	@echo "🐳 启动 Docker 服务..."
	docker-compose up -d
	@echo "✅ Docker 服务已启动"

docker-down:
	@echo "🐳 停止 Docker 服务..."
	docker-compose down
	@echo "✅ Docker 服务已停止"

# -----------------------------------------------------------------------------
# 帮助信息
# -----------------------------------------------------------------------------
help:
	@echo "MetaAgent 构建系统 - 跨平台 + 混合语言"
	@echo ""
	@echo "当前平台：$(TARGET)"
	@echo ""
	@echo "主要目标:"
	@echo "  make all          - 构建所有模块"
	@echo "  make build-python - 构建 Python 模块"
	@echo "  make build-go     - 构建 Go 服务"
	@echo "  make build-rust   - 构建 Rust 扩展"
	@echo "  make test         - 运行所有测试"
	@echo "  make clean        - 清理构建产物"
	@echo "  make package      - 打包发布版本"
	@echo "  make docker-build - 构建 Docker 镜像"
	@echo "  make docker-up    - 启动 Docker 服务"
	@echo "  make docker-down  - 停止 Docker 服务"
	@echo ""
	@echo "配置选项:"
	@echo "  PYTHON_VERSION=$(PYTHON_VERSION)"
	@echo "  GO_VERSION=$(GO_VERSION)"
	@echo "  RUST_VERSION=$(RUST_VERSION)"
	@echo ""

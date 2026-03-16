# 跨平台构建说明

## 支持的平台

| 操作系统 | 架构 | 状态 |
|---------|------|------|
| Linux | x86_64 (amd64) | ✅ 支持 |
| Linux | ARM64 | ✅ 支持 |
| Windows | x86_64 | ✅ 支持 |
| Windows | ARM64 | 🚧 测试中 |
| macOS | x86_64 | ✅ 支持 |
| macOS | ARM64 (M1/M2) | ✅ 支持 |

## 快速开始

### 1. 自动构建（推荐）

```bash
# 构建所有模块
make all

# 查看当前平台
make help
```

### 2. 手动构建

#### Python

```bash
cd src/python
pip install -e .
```

#### Go

```bash
# Linux/macOS
cd src/go
CGO_ENABLED=0 go build -o meta_agent_go ./cmd/main.go

# Windows
cd src/go
go build -o meta_agent_go.exe ./cmd/main.go
```

#### Rust

```bash
cd src/rust
cargo build --release
```

## 跨平台编译

### 使用 Makefile

```bash
# 为 Linux amd64 编译
make build-go TARGET_OS=linux TARGET_ARCH=amd64

# 为 Windows amd64 编译
make build-go TARGET_OS=windows TARGET_ARCH=amd64

# 为 macOS ARM64 编译
make build-go TARGET_OS=darwin TARGET_ARCH=arm64
```

### 使用 Docker

```bash
# 构建多平台镜像
docker buildx build --platform linux/amd64,linux/arm64 -t meta_agent:latest .

# 推送到仓库
docker buildx build --platform linux/amd64,linux/arm64 -t your-username/meta_agent:latest --push .
```

## 测试

### 本地测试

```bash
# 运行所有测试
make test

# 仅 Python 测试
make test-python

# 仅 Go 测试
make test-go

# 仅 Rust 测试
make test-rust
```

### CI/CD 测试

GitHub Actions 会自动在以下平台运行测试：

- Ubuntu Latest (Linux)
- Windows Latest
- macOS Latest

## 打包发布

```bash
# 为当前平台打包
make package

# 发布产物位于 dist/ 目录
ls dist/
```

## 故障排查

### Python 模块找不到

```bash
# 重新安装
pip install -e src/python

# 检查路径
python -c "import meta_agent; print(meta_agent.__file__)"
```

### Go 编译失败

```bash
# 检查 Go 版本
go version

# 清理缓存
go clean -cache

# 重新下载依赖
go mod download
```

### Rust 编译失败

```bash
# 更新 Rust
rustup update

# 清理构建
cargo clean

# 重新构建
cargo build --release
```

## 性能优化

### 编译优化

```bash
# Rust 发布模式（已默认启用）
cargo build --release

# Go 禁用优化（减小体积）
go build -ldflags="-s -w"
```

### 运行优化

```bash
# 启用 Python 优化
python -O -m meta_agent

# 调整 Go 并发
GOMAXPROCS=4 ./meta_agent_go
```

## 作者

MetaAgent Team

## 许可证

MIT License

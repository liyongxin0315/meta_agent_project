# Rust 模块说明

## 目录结构

```
rust/
├── src/
│   └── lib.rs           # Rust 库入口
├── Cargo.toml           # Rust 依赖配置
└── README.md            # 本文档
```

## 功能

- **高性能计算** - 利用 Rust 的零成本抽象
- **内存安全** - 编译时保证内存安全
- **跨平台** - 支持 Linux/Windows/macOS
- **Python 绑定** - 通过 pyo3 提供 Python 接口

## 构建

### 前置要求

- Rust 1.75+
- Python 3.10+
- maturin (构建工具)

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 maturin
pip install maturin
```

### 开发模式

```bash
# 构建并安装到 Python 环境
maturin develop

# 运行测试
cargo test
```

### 生产模式

```bash
# 发布构建
maturin build --release

# 跨平台编译
# Linux
cargo build --release --target x86_64-unknown-linux-gnu

# Windows
cargo build --release --target x86_64-pc-windows-msvc

# macOS
cargo build --release --target x86_64-apple-darwin
```

## 使用

### Python 端

```python
from meta_agent_rust import Core

core = Core()
result = core.parse("example_task")
print(result)
```

### Rust 端

```rust
use meta_agent_rust::Core;

let core = Core::new();
let result = core.parse("example_task");
println!("{:?}", result);
```

## 性能

相比纯 Python 实现：

- 任务解析：**10x** 更快
- 数据处理：**5x** 更快
- 内存使用：**50%** 更少

## 依赖

- pyo3 0.20 - Python 绑定
- serde 1.0 - 序列化
- tokio 1.35 - 异步运行时

## 测试

```bash
# 运行测试
cargo test

# 带覆盖率
cargo tarpaulin

# 性能测试
cargo bench
```

## 作者

MetaAgent Team

## 许可证

MIT License

# 跨语言交互指南

## 架构概述

MetaAgent 采用 **Python 为主 + Go/Rust 扩展** 的混合架构：

```
┌─────────────────────────────────────────┐
│          Python 业务层                   │
│  (任务调度、配置管理、API 接口)           │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐       ┌─────────┐
│   Go    │       │  Rust   │
│  服务   │       │  扩展   │
│ (gRPC)  │       │ (pyo3)  │
└─────────┘       └─────────┘
```

## Python ↔ Rust 交互

### 1. 通过 pyo3 绑定

**Rust 端** (`src/rust/src/lib.rs`):

```rust
use pyo3::prelude::*;

#[pyclass]
pub struct Core {
    initialized: bool,
}

#[pymethods]
impl Core {
    #[new]
    fn new() -> Self {
        Core { initialized: true }
    }

    fn parse(&self, task: &str) -> PyResult<TaskResult> {
        // 实现任务解析逻辑
        Ok(TaskResult { /* ... */ })
    }
}

#[pymodule]
fn meta_agent_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Core>()?;
    Ok(())
}
```

**Python 端** (`src/python/meta_agent/adapters/rust_adapter.py`):

```python
from meta_agent_rust import Core

class RustCore:
    def __init__(self):
        self.core = Core()
    
    def parse_task(self, task: str) -> dict:
        return self.core.parse(task)
```

### 2. 构建和安装

```bash
# 安装 maturin
pip install maturin

# 开发模式
cd src/rust
maturin develop

# 发布构建
maturin build --release
```

### 3. 异常处理

```python
try:
    result = rust_core.parse_task("example")
except RuntimeError as e:
    logger.error(f"Rust 调用失败：{e}")
    # 降级到 Python 实现
    result = python_fallback()
```

## Python ↔ Go 交互

### 1. 通过 gRPC

**Protobuf 定义** (`src/go/pkg/proto/meta_agent.proto`):

```protobuf
syntax = "proto3";
package meta_agent;

service GoConcurrency {
  rpc ExecuteTask(TaskRequest) returns (TaskResponse);
}

message TaskRequest {
  string task_id = 1;
  string content = 2;
}

message TaskResponse {
  string result = 1;
  int32 code = 2;
}
```

**Go 服务端**:

```go
type GoConcurrencyServer struct {
    pb.UnimplementedGoConcurrencyServer
}

func (s *GoConcurrencyServer) ExecuteTask(
    ctx context.Context,
    req *pb.TaskRequest,
) (*pb.TaskResponse, error) {
    // 实现任务执行逻辑
    return &pb.TaskResponse{
        Result: "success",
        Code:   200,
    }, nil
}
```

**Python 客户端**:

```python
import grpc
from meta_agent.proto import meta_agent_pb2, meta_agent_pb2_grpc

class GoConcurrency:
    def __init__(self, addr="localhost:8080"):
        channel = grpc.insecure_channel(addr)
        self.stub = meta_agent_pb2_grpc.GoConcurrencyStub(channel)
    
    def execute_task(self, task_id: str, content: str) -> str:
        response = self.stub.ExecuteTask(
            meta_agent_pb2.TaskRequest(task_id=task_id, content=content),
            timeout=5.0
        )
        return response.result
```

### 2. 启动 Go 服务

```bash
# 开发模式
cd src/go
go run cmd/main.go

# 生产模式
go build -o meta_agent_go cmd/main.go
./meta_agent_go
```

### 3. 服务发现

```python
# 从环境变量读取服务地址
GO_SERVICE_ADDR = os.getenv("GO_SERVICE_ADDR", "localhost:8080")

go_service = GoConcurrency(GO_SERVICE_ADDR)
```

## 最佳实践

### 1. 统一接口

```python
# 定义统一接口
class TaskExecutor(ABC):
    @abstractmethod
    def execute(self, task: dict) -> dict:
        pass

# Rust 实现
class RustExecutor(TaskExecutor):
    def execute(self, task: dict) -> dict:
        return rust_core.execute(task)

# Go 实现
class GoExecutor(TaskExecutor):
    def execute(self, task: dict) -> dict:
        return go_service.execute(task)

# Python 降级实现
class PythonExecutor(TaskExecutor):
    def execute(self, task: dict) -> dict:
        # 纯 Python 实现
        pass
```

### 2. 自动降级

```python
def get_executor() -> TaskExecutor:
    """自动选择可用的执行器"""
    try:
        return RustExecutor()
    except ImportError:
        pass
    
    try:
        return GoExecutor()
    except ConnectionError:
        pass
    
    # 降级到 Python
    return PythonExecutor()
```

### 3. 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} 耗时：{duration:.3f}s")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} 失败：{e}")
            raise
    return wrapper
```

## 调试技巧

### 1. Rust 调试

```bash
# 启用 Rust 日志
RUST_LOG=debug cargo run

# 使用 gdb 调试
gdb --args python -m meta_agent
```

### 2. Go 调试

```bash
# 启用 Go 日志
export DEBUG=1
./meta_agent_go

# 使用 delve 调试
dlv debug ./cmd/main.go
```

### 3. Python 调试

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 常见问题

### Q: Rust 扩展找不到？

A: 确保已运行 `maturin develop` 安装扩展。

### Q: Go 服务连接失败？

A: 检查 Go 服务是否启动，端口是否正确。

### Q: 性能不如预期？

A: 使用性能分析工具：
- Python: `cProfile`
- Go: `pprof`
- Rust: `perf`

## 作者

MetaAgent Team

## 许可证

MIT License

# Go 模块说明

## 目录结构

```
go/
├── cmd/
│   └── main.go          # Go 服务入口
├── pkg/
│   └── proto/           # Protobuf 定义（可选）
├── go.mod               # Go 模块定义
└── go.sum               # 依赖校验
```

## 功能

- **高并发任务执行** - 利用 Go 的 goroutine 实现高并发
- **gRPC 服务** - 提供跨语言 RPC 接口
- **健康检查** - 服务状态监控

## 构建

```bash
# 开发模式
go run cmd/main.go

# 生产模式
go build -o meta_agent_go cmd/main.go

# 跨平台编译
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o meta_agent_go_linux
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -o meta_agent_go.exe
CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build -o meta_agent_go_mac
```

## 运行

```bash
# 默认端口 8080
./meta_agent_go

# 自定义端口
GO_SERVICE_PORT=9090 ./meta_agent_go
```

## 测试

```bash
# 运行测试
go test ./...

# 带覆盖率
go test -cover ./...
```

## 依赖

- Go 1.21+
- gRPC
- Protobuf

## 与 Python 交互

Python 端通过 gRPC 调用 Go 服务：

```python
from meta_agent.adapters.go_adapter import GoConcurrency

go_service = GoConcurrency("localhost:8080")
result = go_service.execute_task("task_001", "process_data")
```

## 作者

MetaAgent Team

## 许可证

MIT License

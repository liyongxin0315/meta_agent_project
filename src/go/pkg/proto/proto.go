// Package proto 包含 MetaAgent 的 gRPC 服务定义
package proto

//go:generate protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative proto/meta_agent.proto

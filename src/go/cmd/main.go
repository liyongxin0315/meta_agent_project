// MetaAgent Go 并发服务 - 完整实现
// 提供高性能任务执行和 gRPC 服务

package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"
)

// TaskExecutorServer 任务执行服务实现
type TaskExecutorServer struct {
	// 任务计数器
	taskCount   uint64
	countMutex  sync.Mutex
	
	// 服务状态
	healthServer *health.Server
}

// ExecuteTask 执行单个任务
func (s *TaskExecutorServer) ExecuteTask(
	ctx context.Context,
	req *TaskRequest,
) (*TaskResponse, error) {
	startTime := time.Now()
	
	// 验证请求
	if err := s.validateTask(req); err != nil {
		return &TaskResponse{
			Success:      false,
			TaskId:       req.GetTaskId(),
			ErrorMessage: err.Error(),
		}, nil
	}

	// 设置超时
	if req.GetTimeoutMs() > 0 {
		ctx, _ = context.WithTimeout(ctx, time.Duration(req.GetTimeoutMs())*time.Millisecond)
	}

	// 执行任务
	result, err := s.processTask(ctx, req)
	processingTime := time.Since(startTime).Milliseconds()

	if err != nil {
		log.Printf("任务执行失败 [task_id=%s]: %v", req.GetTaskId(), err)
		return &TaskResponse{
			Success:         false,
			TaskId:          req.GetTaskId(),
			ErrorMessage:    err.Error(),
			ProcessingTimeMs: uint64(processingTime),
		}, nil
	}

	// 更新计数器
	s.countMutex.Lock()
	s.taskCount++
	taskCount := s.taskCount
	s.countMutex.Unlock()

	log.Printf("任务执行成功 [task_id=%s, count=%d, time=%dms]", 
		req.GetTaskId(), taskCount, processingTime)

	return &TaskResponse{
		Success:         true,
		TaskId:          req.GetTaskId(),
		Result:          result,
		ProcessingTimeMs: uint64(processingTime),
		Metadata: map[string]string{
			"processed_by": "go_service",
			"version":      "1.0.0",
		},
	}, nil
}

// ExecuteTaskBatch 批量执行任务
func (s *TaskExecutorServer) ExecuteTaskBatch(
	ctx context.Context,
	req *TaskBatchRequest,
) (*TaskBatchResponse, error) {
	startTime := time.Now()
	
	tasks := req.GetTasks()
	if len(tasks) == 0 {
		return &TaskBatchResponse{
			TotalTimeMs: 0,
			SuccessCount: 0,
			FailedCount:  0,
		}, nil
	}

	var responses []*TaskResponse
	successCount := 0
	failedCount := 0

	// 并行执行
	if req.GetParallel() {
		var wg sync.WaitGroup
		resultChan := make(chan *TaskResponse, len(tasks))

		for _, task := range tasks {
			wg.Add(1)
			go func(t *TaskRequest) {
				defer wg.Done()
				resp, _ := s.ExecuteTask(ctx, t)
				resultChan <- resp
			}(task)
		}

		// 等待所有任务完成
		go func() {
			wg.Wait()
			close(resultChan)
		}()

		// 收集结果
		for resp := range resultChan {
			responses = append(responses, resp)
			if resp.GetSuccess() {
				successCount++
			} else {
				failedCount++
			}
		}
	} else {
		// 串行执行
		for _, task := range tasks {
			resp, _ := s.ExecuteTask(ctx, task)
			responses = append(responses, resp)
			if resp.GetSuccess() {
				successCount++
			} else {
				failedCount++
			}
		}
	}

	totalTime := time.Since(startTime).Milliseconds()

	log.Printf("批量任务完成 [total=%d, success=%d, failed=%d, time=%dms]",
		len(tasks), successCount, failedCount, totalTime)

	return &TaskBatchResponse{
		Responses:    responses,
		TotalTimeMs:  uint64(totalTime),
		SuccessCount: uint32(successCount),
		FailedCount:  uint32(failedCount),
	}, nil
}

// ExecuteTaskStream 流式任务执行
func (s *TaskExecutorServer) ExecuteTaskStream(
	stream TaskExecutor_ExecuteTaskStreamServer,
) error {
	for {
		req, err := stream.Recv()
		if err != nil {
			if err.Error() == "EOF" {
				return nil
			}
			return err
		}

		resp, err := s.ExecuteTask(stream.Context(), req)
		if err != nil {
			return err
		}

		if err := stream.Send(resp); err != nil {
			return err
		}
	}
}

// HealthCheck 健康检查
func (s *TaskExecutorServer) HealthCheck(
	ctx context.Context,
	req *HealthCheckRequest,
) (*HealthCheckResponse, error) {
	return &HealthCheckResponse{
		Status:    healthpb.HealthCheckResponse_SERVING,
		Message:   "Service is healthy",
		Timestamp: uint64(time.Now().Unix()),
	}, nil
}

// validateTask 验证任务请求
func (s *TaskExecutorServer) validateTask(req *TaskRequest) error {
	if req.GetTaskId() == "" {
		return status.Error(codes.InvalidArgument, "task_id 不能为空")
	}
	if req.GetContent() == "" {
		return status.Error(codes.InvalidArgument, "content 不能为空")
	}
	return nil
}

// processTask 处理任务核心逻辑
func (s *TaskExecutorServer) processTask(ctx context.Context, req *TaskRequest) (string, error) {
	// 模拟业务处理
	select {
	case <-ctx.Done():
		return "", status.Error(codes.DeadlineExceeded, "任务超时")
	default:
		// 实际业务逻辑
		result := fmt.Sprintf("Processed: %s (priority: %d)", 
			req.GetContent(), req.GetPriority())
		return result, nil
	}
}

func main() {
	// 获取服务端口
	port := os.Getenv("GO_SERVICE_PORT")
	if port == "" {
		port = "8080"
	}

	// 创建 gRPC 服务器
	grpcServer := grpc.NewServer(
		grpc.MaxConcurrentStreams(100),
		grpc.MaxRecvMsgSize(10*1024*1024), // 10MB
		grpc.MaxSendMsgSize(10*1024*1024),
	)

	// 创建服务实例
	taskServer := &TaskExecutorServer{
		taskCount:    0,
		healthServer: health.NewServer(),
	}

	// 注册服务
	RegisterTaskExecutorServer(grpcServer, taskServer)
	grpc_health_v1.RegisterHealthServer(grpcServer, taskServer.healthServer)

	// 启用反射
	reflection.Register(grpcServer)

	// 监听端口
	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatalf("无法监听端口 %s: %v", port, err)
	}

	log.Printf("==============================================")
	log.Printf("MetaAgent Go 并发服务启动")
	log.Printf("==============================================")
	log.Printf("端口：%s", port)
	log.Printf("时间：%s", time.Now().Format("2006-01-02 15:04:05"))
	log.Printf("==============================================")

	// 优雅关闭
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
		sig := <-sigChan
		log.Printf("收到信号 %v，优雅关闭服务...", sig)
		
		// 设置服务状态为 NOT_SERVING
		taskServer.healthServer.Shutdown()
		
		// 优雅停止 gRPC 服务器
		grpcServer.GracefulStop()
		log.Println("Go 并发服务已关闭")
	}()

	// 启动服务
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("服务启动失败：%v", err)
	}
}

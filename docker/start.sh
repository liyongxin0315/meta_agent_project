#!/bin/bash
# =============================================================================
# MetaAgent 启动脚本 - 多语言服务编排
# =============================================================================
# 功能：
#   1. 启动 Go 并发服务（后台）
#   2. 启动 Python 主应用（前台）
#   3. 优雅关闭所有服务
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 清理函数
cleanup() {
    log_info "收到终止信号，正在关闭服务..."
    
    if [ -n "$GO_SERVICE_PID" ] && kill -0 "$GO_SERVICE_PID" 2>/dev/null; then
        log_info "停止 Go 服务 (PID: $GO_SERVICE_PID)"
        kill -TERM "$GO_SERVICE_PID" 2>/dev/null || true
        wait "$GO_SERVICE_PID" 2>/dev/null || true
    fi
    
    log_info "所有服务已关闭"
    exit 0
}

# 注册信号处理
trap cleanup SIGINT SIGTERM

# 启动 Go 服务
start_go_service() {
    local go_service="$APP_DIR/src/go/meta_agent_go"
    
    if [ ! -f "$go_service" ]; then
        log_warn "Go 服务未编译，跳过启动"
        return 0
    fi
    
    log_info "启动 Go 并发服务..."
    
    # 设置环境变量
    export GO_SERVICE_PORT="${GO_SERVICE_PORT:-8080}"
    
    # 后台启动
    "$go_service" &
    GO_SERVICE_PID=$!
    
    log_info "Go 服务已启动 (PID: $GO_SERVICE_PID, 端口：$GO_SERVICE_PORT)"
}

# 启动 Python 应用
start_python_app() {
    log_info "启动 Python 主应用..."
    
    # 设置环境变量
    export META_AGENT_ENVIRONMENT="${META_AGENT_ENVIRONMENT:-production}"
    export META_AGENT_LOG_LEVEL="${META_AGENT_LOG_LEVEL:-INFO}"
    
    # 前台运行
    cd "$APP_DIR/src/python"
    python -m meta_agent
}

# 主函数
main() {
    log_info "=============================================="
    log_info "MetaAgent 启动 - 多语言混合服务"
    log_info "=============================================="
    log_info "平台：$(uname -s)-$(uname -m)"
    log_info "时间：$(date)"
    log_info ""
    
    # 启动 Go 服务
    start_go_service
    
    # 启动 Python 应用
    start_python_app
}

# 执行主函数
main "$@"

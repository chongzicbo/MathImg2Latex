#!/bin/bash

# 定义端口号和工作目录
PORT=17800
WORK_DIR="/data/bocheng/dev/mywork/MathImg2Latex/flask_math2latex"
PYTHON_CMD="/data/bocheng/software/installed/miniconda3/envs/test/bin/python mathocr_server.py"
LOG_FILE="logs/mathocr.log"

# 检查端口是否被占用
is_port_in_use() {
    netstat -tuln | grep ":$PORT "
}

# 查找并杀死名称包含 "mathocr_server.py" 的进程
kill_mathocr_processes() {
    pids=$(pgrep -f "mathocr_server.py")
    if [ -n "$pids" ]; then
        echo "Killing processes: $pids"
        kill -9 $pids
    fi
}

# 启动服务
start_service() {
    cd "$WORK_DIR" || exit 1
    nohup $PYTHON_CMD >"$LOG_FILE" 2>&1 &
    echo "Service started and logs will be saved to $LOG_FILE"
}

# 主逻辑
while true; do
    if ! is_port_in_use; then
        echo "Process not running on port $PORT, checking for mathocr_server.py processes..."
        kill_mathocr_processes
        echo "Starting service..."
        start_service
    else
        echo "Process is running on port $PORT."
    fi
    sleep 60 # 每隔60秒检查一次
done

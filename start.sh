#!/bin/bash

# Job Planner Assistant 启动脚本

echo "=== 求职规划助手启动脚本 ==="

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "警告: OPENAI_API_KEY 环境变量未设置"
fi

if [ -z "$SERPER_API_KEY" ]; then
    echo "警告: SERPER_API_KEY 环境变量未设置"
fi

# 创建必要的目录
echo "创建数据目录..."
mkdir -p data/logs data/chromadb

# 复制环境变量模板
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑 .env 文件并设置必要的API密钥"
fi

# 选择启动模式
echo "请选择启动模式:"
echo "1. 开发模式 (本地运行)"
echo "2. Docker模式 (容器运行)"
echo "3. 仅后端"
echo "4. 仅前端"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "启动开发模式..."
        
        # 启动后端
        echo "启动后端服务..."
        cd backend
        python -m pip install -r ../requirements.txt
        python main.py &
        BACKEND_PID=$!
        cd ..
        
        # 等待后端启动
        sleep 5
        
        # 启动前端
        echo "启动前端服务..."
        cd frontend
        npm install
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        
        echo "服务已启动:"
        echo "- 后端: http://localhost:8000"
        echo "- 前端: http://localhost:3000"
        echo "- API文档: http://localhost:8000/docs"
        
        # 等待用户中断
        echo "按 Ctrl+C 停止服务"
        trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
        wait
        ;;
        
    2)
        echo "启动Docker模式..."
        
        # 检查Docker
        if ! command -v docker &> /dev/null; then
            echo "错误: Docker 未安装"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo "错误: Docker Compose 未安装"
            exit 1
        fi
        
        # 启动服务
        docker-compose up --build
        ;;
        
    3)
        echo "启动后端服务..."
        cd backend
        python -m pip install -r ../requirements.txt
        python main.py
        ;;
        
    4)
        echo "启动前端服务..."
        cd frontend
        npm install
        npm run dev
        ;;
        
    *)
        echo "无效选择"
        exit 1
        ;;
esac


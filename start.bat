@echo off
chcp 65001 >nul
echo === 求职规划助手启动脚本 (Windows) ===

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python 未安装或未添加到PATH
    echo 请安装Python 3.11+并添加到系统PATH
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Node.js 未安装或未添加到PATH
    echo 请安装Node.js 20+并添加到系统PATH
    pause
    exit /b 1
)

REM 检查环境变量
if "%OPENAI_API_KEY%"=="" (
    echo 警告: OPENAI_API_KEY 环境变量未设置
)

if "%SERPER_API_KEY%"=="" (
    echo 警告: SERPER_API_KEY 环境变量未设置
)

REM 创建必要的目录
echo 创建数据目录...
if not exist "data" mkdir data
if not exist "data\logs" mkdir data\logs
if not exist "data\chromadb" mkdir data\chromadb

REM 复制环境变量模板
if not exist ".env" (
    echo 创建环境变量文件...
    copy ".env.example" ".env"
    echo 请编辑 .env 文件并设置必要的API密钥
)

echo.
echo 请选择启动模式:
echo 1. 开发模式 (本地运行)
echo 2. 仅后端
echo 3. 仅前端
echo 4. 安装依赖
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" goto dev_mode
if "%choice%"=="2" goto backend_only
if "%choice%"=="3" goto frontend_only
if "%choice%"=="4" goto install_deps
echo 无效选择
pause
exit /b 1

:dev_mode
echo 启动开发模式...

REM 启动后端
echo 启动后端服务...
cd backend
start "Backend Server" cmd /k "python -m pip install -r ../requirements.txt && python main.py"
cd ..

REM 等待后端启动
echo 等待后端启动...
timeout /t 5 /nobreak >nul

REM 启动前端
echo 启动前端服务...
cd frontend
start "Frontend Server" cmd /k "npm install && npm run dev"
cd ..

echo.
echo 服务已启动:
echo - 后端: http://localhost:8000
echo - 前端: http://localhost:3000
echo - API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭...
pause
goto :eof

:backend_only
echo 启动后端服务...
cd backend
python -m pip install -r ../requirements.txt
python main.py
cd ..
pause
goto :eof

:frontend_only
echo 启动前端服务...
cd frontend
npm install
npm run dev
cd ..
pause
goto :eof

:install_deps
echo 安装依赖...
echo 安装Python依赖...
python -m pip install -r requirements.txt

echo 安装Node.js依赖...
cd frontend
npm install
cd ..

echo 依赖安装完成!
pause
goto :eof


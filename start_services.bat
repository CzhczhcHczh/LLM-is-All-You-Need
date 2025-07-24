@echo off
echo Starting LLM Job Application System...
echo.

echo Starting backend service...
cd /d "d:\作业\暑期实训\LLM-is-All-You-Need-main\backend"
start cmd /k "conda activate jpa && python main.py"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend service...
cd /d "d:\作业\暑期实训\LLM-is-All-You-Need-main\frontend"
start cmd /k "npm run dev"

echo.
echo Services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause

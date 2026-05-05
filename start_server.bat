@echo off
echo Starting Serene Habits Server...
echo.

:: 启动静态文件服务 (端口90)
start "Static Server" python3-64.exe back/app.py

:: 等待1秒确保第一个服务启动
timeout /t 1 /nobreak >nul

:: 启动API服务 (端口5000)
start "API Server" python3-64.exe back/api.py

echo.
echo Both servers started successfully!
echo Static Files: http://localhost:90
echo API: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul
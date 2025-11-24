@echo off
chcp 65001 >nul
title 10U战神滚仓策略 - 启动脚本

echo ========================================
echo   10U战神滚仓策略 - 快速启动
echo ========================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] 建议以管理员身份运行此脚本
    echo.
    timeout /t 3 >nul
)

REM 切换到项目目录
cd /d "%~dp0"

echo [1/5] 检查 PM2 是否安装...
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] PM2 未安装
    echo 请运行: npm install -g pm2
    pause
    exit /b 1
)
echo [√] PM2 已安装
echo.

echo [2/5] 检查配置文件...
if not exist ".env" (
    echo [错误] .env 文件不存在
    echo 请先复制 .env.example 为 .env 并配置
    pause
    exit /b 1
)
echo [√] 配置文件存在
echo.

echo [3/5] 停止旧的服务...
pm2 delete all >nul 2>&1
echo [√] 已清理旧服务
echo.

echo [4/5] 启动服务...
echo   - Web Dashboard (端口 3000)
pm2 start ecosystem.config.js --only trading-dashboard
echo   - WebSocket 服务器 (端口 8765)
pm2 start ecosystem.config.js --only websocket-server
echo.

echo [5/5] 保存 PM2 配置...
pm2 save
echo [√] 配置已保存
echo.

echo ========================================
echo   服务启动完成！
echo ========================================
echo.

REM 获取本机 IP 地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo 访问地址: http://!IP!:3000
)
echo 访问地址: http://localhost:3000
echo.

echo 常用命令:
echo   查看状态: pm2 list
echo   查看日志: pm2 logs
echo   重启服务: pm2 restart all
echo   停止服务: pm2 stop all
echo.

echo 下一步:
echo   1. 在浏览器中访问上述地址
echo   2. 检查 Dashboard 是否正常显示
echo   3. 如需启动交易机器人，请运行: start_trading_bot.bat
echo.

pause

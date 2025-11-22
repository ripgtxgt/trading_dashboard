@echo off
chcp 65001 >nul
title 10U战神滚仓策略 - 交易系统

echo ========================================
echo   10U战神滚仓策略 - 交易系统启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python！
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [✓] Python已安装
python --version
echo.

REM 检查必需的Python包
echo [检查] 正在检查Python依赖包...
python -c "import mysql.connector" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 mysql-connector-python...
    pip install mysql-connector-python
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 requests...
    pip install requests
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 pandas...
    pip install pandas
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 numpy...
    pip install numpy
)

echo [✓] 所有依赖包已安装
echo.

REM 检查配置文件
if not exist "config.env" (
    echo [警告] 未找到配置文件 config.env
    echo 正在创建配置文件模板...
    call create_config.bat
    echo.
    echo [重要] 请先编辑 config.env 文件，填入你的配置信息！
    echo 配置完成后，再次运行本脚本。
    pause
    exit /b 1
)

echo [✓] 配置文件已找到
echo.

REM 加载配置文件
echo [加载] 正在加载配置...
for /f "usebackq tokens=1,* delims==" %%a in ("config.env") do (
    set "%%a=%%b"
)

REM 检查必需配置
if "%DATABASE_URL%"=="" (
    echo [错误] 缺少配置: DATABASE_URL
    echo 请编辑 config.env 文件
    pause
    exit /b 1
)

if "%KUCOIN_API_KEY%"=="" (
    echo [错误] 缺少配置: KUCOIN_API_KEY
    echo 请编辑 config.env 文件
    pause
    exit /b 1
)

echo [✓] 配置加载完成
echo.

REM 显示配置摘要
echo ========================================
echo   配置摘要
echo ========================================
echo 数据库: %DATABASE_URL:~0,30%...
echo KuCoin API: %KUCOIN_API_KEY:~0,10%...
echo 初始资金: %INITIAL_CAPITAL% USDT
echo 沙盒模式: %KUCOIN_SANDBOX%
if not "%TELEGRAM_BOT_TOKEN%"=="" (
    echo Telegram: 已配置
) else (
    echo Telegram: 未配置
)
echo ========================================
echo.

echo [启动] 正在启动交易系统...
echo 按 Ctrl+C 可以停止系统
echo.

REM 启动交易系统
python start_trading_system.py

echo.
echo ========================================
echo   交易系统已停止
echo ========================================
pause

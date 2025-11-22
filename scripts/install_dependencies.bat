@echo off
chcp 65001 >nul
title 依赖安装工具

echo ========================================
echo   10U战神滚仓策略 - 依赖安装
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python！
    echo.
    echo 请先安装Python 3.8或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载最新的Python 3.x版本
    echo 3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [✓] Python已安装
python --version
echo.

REM 升级pip
echo [1/5] 升级pip到最新版本...
python -m pip install --upgrade pip
echo.

REM 安装mysql-connector-python
echo [2/5] 安装 mysql-connector-python...
pip install mysql-connector-python
echo.

REM 安装requests
echo [3/5] 安装 requests...
pip install requests
echo.

REM 安装pandas
echo [4/5] 安装 pandas...
pip install pandas
echo.

REM 安装numpy
echo [5/5] 安装 numpy...
pip install numpy
echo.

echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 已安装的包:
pip list | findstr /C:"mysql-connector-python" /C:"requests" /C:"pandas" /C:"numpy"
echo.
echo 下一步:
echo 1. 运行 create_config.bat 创建配置文件
echo 2. 编辑 config.env 填入你的配置
echo 3. 运行 check_environment.bat 检查环境
echo 4. 运行 start_trading.bat 启动交易系统
echo.

pause

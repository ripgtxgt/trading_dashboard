@echo off
chcp 65001 >nul
title 环境检查工具

echo ========================================
echo   10U战神滚仓策略 - 环境检查
echo ========================================
echo.

set ERROR_COUNT=0

REM 检查Python
echo [1/5] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python未安装
    echo     请从 https://www.python.org/downloads/ 下载安装
    set /a ERROR_COUNT+=1
) else (
    echo [✓] Python已安装
    python --version
)
echo.

REM 检查pip
echo [2/5] 检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [✗] pip未安装
    set /a ERROR_COUNT+=1
) else (
    echo [✓] pip已安装
    pip --version
)
echo.

REM 检查Python包
echo [3/5] 检查Python依赖包...
set MISSING_PACKAGES=0

python -c "import mysql.connector" >nul 2>&1
if errorlevel 1 (
    echo [✗] mysql-connector-python 未安装
    set /a MISSING_PACKAGES+=1
) else (
    echo [✓] mysql-connector-python 已安装
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [✗] requests 未安装
    set /a MISSING_PACKAGES+=1
) else (
    echo [✓] requests 已安装
)

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [✗] pandas 未安装
    set /a MISSING_PACKAGES+=1
) else (
    echo [✓] pandas 已安装
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [✗] numpy 未安装
    set /a MISSING_PACKAGES+=1
) else (
    echo [✓] numpy 已安装
)

if %MISSING_PACKAGES% gtr 0 (
    echo.
    echo [提示] 发现 %MISSING_PACKAGES% 个缺失的包
    echo 运行 install_dependencies.bat 可以自动安装
    set /a ERROR_COUNT+=1
)
echo.

REM 检查配置文件
echo [4/5] 检查配置文件...
if not exist "config.env" (
    echo [✗] 配置文件不存在
    echo     运行 create_config.bat 创建配置文件
    set /a ERROR_COUNT+=1
) else (
    echo [✓] 配置文件存在
    
    REM 检查配置内容
    findstr /C:"DATABASE_URL=mysql://" config.env >nul
    if errorlevel 1 (
        echo [!] 警告: DATABASE_URL 可能未配置
    )
    
    findstr /C:"KUCOIN_API_KEY=你的" config.env >nul
    if not errorlevel 1 (
        echo [!] 警告: KUCOIN_API_KEY 需要修改
    )
)
echo.

REM 检查数据库连接
echo [5/5] 检查数据库连接...
if exist "config.env" (
    python -c "import sys; sys.path.insert(0, '.'); from db_sync import DatabaseSync; db = DatabaseSync(); result = db.connect(); db.disconnect(); sys.exit(0 if result else 1)" >nul 2>&1
    if errorlevel 1 (
        echo [✗] 数据库连接失败
        echo     请检查 DATABASE_URL 配置是否正确
        set /a ERROR_COUNT+=1
    ) else (
        echo [✓] 数据库连接成功
    )
) else (
    echo [跳过] 配置文件不存在
)
echo.

REM 总结
echo ========================================
echo   检查结果
echo ========================================
if %ERROR_COUNT%==0 (
    echo [✓] 所有检查通过！
    echo 你可以运行 start_trading.bat 启动交易系统
) else (
    echo [✗] 发现 %ERROR_COUNT% 个问题
    echo 请根据上述提示解决问题后再启动系统
)
echo ========================================
echo.

pause

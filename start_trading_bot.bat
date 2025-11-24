@echo off
chcp 65001 >nul
title 10U战神滚仓策略 - 启动交易机器人

echo ========================================
echo   10U战神滚仓策略 - 启动交易机器人
echo ========================================
echo.

REM 切换到项目目录
cd /d "%~dp0"

echo [警告] 即将启动交易机器人
echo.
echo 请确认:
echo   1. 已在 .env 中配置正确的 KuCoin API 密钥
echo   2. 已充分测试策略参数
echo   3. 已设置合理的止损止盈
echo   4. 账户余额充足
echo.

set /p confirm="确认启动交易机器人? (输入 YES 继续): "
if /i not "%confirm%"=="YES" (
    echo 已取消启动
    pause
    exit /b 0
)

echo.
echo [1/3] 检查 PM2 是否安装...
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] PM2 未安装
    echo 请运行: npm install -g pm2
    pause
    exit /b 1
)
echo [√] PM2 已安装
echo.

echo [2/3] 检查交易脚本...
if not exist "scripts\kucoin_api.py" (
    echo [错误] 交易脚本不存在: scripts\kucoin_api.py
    pause
    exit /b 1
)
echo [√] 交易脚本存在
echo.

echo [3/3] 启动交易机器人...
pm2 start ecosystem.config.js --only trading-bot
if %errorLevel% neq 0 (
    echo [错误] 启动失败
    echo 请查看日志: pm2 logs trading-bot
    pause
    exit /b 1
)
echo [√] 交易机器人已启动
echo.

echo 保存 PM2 配置...
pm2 save
echo.

echo ========================================
echo   交易机器人启动成功！
echo ========================================
echo.

echo 常用命令:
echo   查看状态: pm2 list
echo   查看日志: pm2 logs trading-bot
echo   停止机器人: pm2 stop trading-bot
echo   重启机器人: pm2 restart trading-bot
echo.

echo 重要提示:
echo   - 请密切关注交易日志
echo   - 建议启用 Telegram 通知
echo   - 定期检查账户余额和持仓
echo   - 遇到异常立即停止: pm2 stop trading-bot
echo.

pause

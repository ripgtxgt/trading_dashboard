@echo off
chcp 65001 >nul

echo 正在创建配置文件模板...

(
echo # 10U战神滚仓策略 - 配置文件
echo # 请根据实际情况填写以下配置
echo.
echo # ========== 必需配置 ==========
echo.
echo # 数据库连接字符串
echo # 格式: mysql://用户名:密码@服务器地址:端口/数据库名
echo # 示例: mysql://root:123456@localhost:3306/trading
echo DATABASE_URL=mysql://root:password@localhost:3306/trading_dashboard
echo.
echo # KuCoin API配置
echo # 在 KuCoin 网站获取: https://www.kucoin.com/account/api
echo KUCOIN_API_KEY=你的API_KEY
echo KUCOIN_API_SECRET=你的API_SECRET  
echo KUCOIN_API_PASSPHRASE=你的API_PASSPHRASE
echo.
echo # ========== 可选配置 ==========
echo.
echo # Telegram通知配置（可选）
echo # 配置方法见 TELEGRAM_SETUP.md
echo TELEGRAM_BOT_TOKEN=
echo TELEGRAM_CHAT_ID=
echo.
echo # 交易配置
echo INITIAL_CAPITAL=10.0
echo KUCOIN_SANDBOX=false
echo.
) > config.env

echo [✓] 配置文件已创建: config.env
echo.
echo 请使用记事本打开 config.env 文件，填入你的配置信息。

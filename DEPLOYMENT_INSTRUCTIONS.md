# 部署说明

## 📦 项目包内容

此压缩包包含修复后的完整项目，已删除 `node_modules`，需要重新安装依赖。

## 🔧 修复内容总结

### 关键Bug修复
1. ✅ **live_strategy_engine_rolling.py** - 修复 `get_current_price()` 缺少参数问题
2. ✅ **db_sync.py** - 修复数据库字段名不匹配问题
3. ✅ **start_trading_system.py** - 修复 `update_bot_state()` 参数错误
4. ✅ **ecosystem.config.cjs** - 修复websocket服务路径错误

### 清理内容
- 删除所有临时修复脚本
- 删除测试和示例文件
- 删除旧备份文件
- 保留17个核心Python文件

详细修复内容请查看 `FIXES_APPLIED.md`

## 🚀 Windows服务器部署步骤

### 1. 解压项目

```cmd
# 解压到 C:\trading_dashboard\
tar -xzf trading_dashboard_fixed_20251125.tar.gz
cd C:\trading_dashboard\trading_dashboard_fixed
```

### 2. 安装Node.js依赖

```cmd
pnpm install
```

**注意：** 这一步会下载约2.6GB的依赖，需要一些时间。

### 3. 安装Python依赖

```cmd
pip install -r requirements.txt
```

### 4. 配置环境变量

编辑 `.env` 文件，填入以下配置：

```env
# KuCoin API配置
KUCOIN_API_KEY=your_api_key
KUCOIN_API_SECRET=your_api_secret
KUCOIN_API_PASSPHRASE=your_passphrase
KUCOIN_SANDBOX=false

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=trading
DB_PASSWORD=your_password
DB_NAME=trading_dashboard

# Telegram配置
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 其他配置
LEVERAGE=100
INITIAL_CAPITAL=10
```

### 5. 初始化数据库

```cmd
mysql -u root -p < database/schema.sql
```

### 6. 启动服务

#### 使用PM2启动所有服务（推荐）

```cmd
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup
```

#### 或者单独启动

```cmd
# Web Dashboard
pnpm dev

# Trading Bot
python scripts\start_trading_system.py

# Telegram Bot
python scripts\telegram_bot.py

# WebSocket Server
python scripts\websocket_pusher.py

# Daily Report
python scripts\daily_report.py
```

### 7. 查看服务状态

```cmd
pm2 list
pm2 logs
```

### 8. 访问Web Dashboard

打开浏览器访问：`http://localhost:3000`

## 📋 服务说明

### 1. trading-dashboard (Node.js)
- **端口：** 3000
- **说明：** Web前端和tRPC API服务器
- **日志：** `logs/dashboard-*.log`

### 2. trading-bot (Python)
- **说明：** 主交易机器人，执行10U战神滚仓策略
- **日志：** `logs/trading-bot-*.log`

### 3. telegram-bot (Python)
- **说明：** Telegram通知机器人
- **日志：** `logs/telegram-bot-*.log`

### 4. websocket-server (Python)
- **说明：** WebSocket实时数据推送服务
- **日志：** `logs/websocket-*.log`

### 5. daily-report (Python)
- **说明：** 每日报告生成器（每天0点自动运行）
- **日志：** `logs/daily-report-*.log`

## ⚠️ 注意事项

### 1. 环境要求
- Windows Server 2019+
- Python 3.11+
- Node.js 22+
- MySQL 8.0+
- PM2 (全局安装)

### 2. 防火墙配置
确保以下端口开放：
- 3000 (Web Dashboard)
- 3306 (MySQL)
- 8080 (WebSocket，如果需要)

### 3. 安全建议
- 不要将 `.env` 文件提交到版本控制
- 定期更新API密钥
- 定期备份数据库
- 监控日志文件大小

### 4. 常见问题

#### Q: PM2启动失败
A: 检查Python和Node.js是否在PATH中，确保所有依赖已安装

#### Q: 数据库连接失败
A: 检查 `.env` 中的数据库配置，确保MySQL服务正在运行

#### Q: Telegram通知不工作
A: 检查 `.env` 中的Telegram配置，确保Bot Token和Chat ID正确

#### Q: 交易机器人不交易
A: 检查KuCoin API配置，确保API权限包含合约交易

## 📞 支持

如有问题，请查看以下文档：
- `QUICK_START.md` - 快速开始指南
- `WINDOWS_SERVER_DEPLOYMENT.md` - Windows服务器详细部署指南
- `FIXES_APPLIED.md` - 修复内容详情
- `scripts/README.md` - 脚本说明

## 📊 项目统计

- **核心Python文件：** 17个
- **配置文件：** 5个
- **文档文件：** 20+个
- **项目大小：** 2.1MB (不含node_modules)
- **完整大小：** 2.6GB (含node_modules)

## 🎯 下一步

1. 完成部署后，访问 `http://localhost:3000` 查看Dashboard
2. 检查所有服务状态：`pm2 list`
3. 查看实时日志：`pm2 logs`
4. 测试Telegram通知是否正常
5. 监控交易机器人运行状态

祝部署顺利！🎉

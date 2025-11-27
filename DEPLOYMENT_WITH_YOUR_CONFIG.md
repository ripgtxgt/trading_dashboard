# 🚀 Trading Dashboard 部署指南（使用您的正式配置）

## ✅ 您的配置信息

我已收到您的正式环境配置文件，包含以下信息：

### 数据库配置
- **主机:** localhost
- **端口:** 3306
- **用户:** trading  
- **密码:** Zdm351026
- **数据库:** trading_dashboard
- **连接字符串:** `mysql://trading:Zdm351026@localhost:3306/trading_dashboard`

### KuCoin API配置
- **API Key:** `6902f625f9a9a300014c3976`
- **API Secret:** `d71e4e3d-4369-4e77-94f8-fd456c5e0387`
- **API Passphrase:** `x5gU7dnL6bvrvbV!`

### Telegram配置
- **Bot Token:** `7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U`
- **Chat ID:** `5374455360`

### 交易参数
- **交易模式:** paper (模拟交易，安全)
- **最大仓位:** 100 USDT
- **止损:** 5%
- **止盈:** 10%

---

## 🚀 Windows Server 部署步骤

### 步骤1：解压项目
```cmd
# 解压到 C:\
tar -xzf trading_dashboard_with_deploy_tools.tar.gz -C C:\
cd C:\trading_dashboard_fixed
```

### 步骤2：创建配置文件

在项目根目录 `C:\trading_dashboard_fixed\` 创建 `.env` 文件：

**方式1：使用记事本创建**
```cmd
notepad .env
```

然后复制粘贴以下内容：

```env
# ===================================================================
# Trading Dashboard Environment Configuration
# ===================================================================

# Database Configuration
DATABASE_URL="mysql://trading:Zdm351026@localhost:3306/trading_dashboard"

# KuCoin API Configuration
KUCOIN_API_KEY="6902f625f9a9a300014c3976"
KUCOIN_API_SECRET="d71e4e3d-4369-4e77-94f8-fd456c5e0387"
KUCOIN_API_PASSPHRASE="x5gU7dnL6bvrvbV!"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U"
TELEGRAM_CHAT_ID="5374455360"

# JWT Secret (for session management)
JWT_SECRET="H2HcA2>(JYrp$IF2RP0Ktu>ZGwcioqFb,8h_>{nK7dX,YR4qnp-08jN_1yfj]>%C"

# ===================================================================
# Optional: Trading Bot Configuration
# ===================================================================

# Trading Mode (paper/live)
TRADING_MODE="paper"

# Risk Management
MAX_POSITION_SIZE="100"
STOP_LOSS_PERCENTAGE="5"
TAKE_PROFIT_PERCENTAGE="10"

# ===================================================================
# System Configuration (Do not modify unless necessary)
# ===================================================================

# Server Port
PORT="3000"

# WebSocket Port
WEBSOCKET_PORT="8765"

# Node Environment
NODE_ENV="production"
```

保存并关闭文件。

**方式2：使用PowerShell创建**
```powershell
@"
# ===================================================================
# Trading Dashboard Environment Configuration
# ===================================================================

# Database Configuration
DATABASE_URL="mysql://trading:Zdm351026@localhost:3306/trading_dashboard"

# KuCoin API Configuration
KUCOIN_API_KEY="6902f625f9a9a300014c3976"
KUCOIN_API_SECRET="d71e4e3d-4369-4e77-94f8-fd456c5e0387"
KUCOIN_API_PASSPHRASE="x5gU7dnL6bvrvbV!"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U"
TELEGRAM_CHAT_ID="5374455360"

# JWT Secret
JWT_SECRET="H2HcA2>(JYrp`$IF2RP0Ktu>ZGwcioqFb,8h_>{nK7dX,YR4qnp-08jN_1yfj]>%C"

# Trading Mode
TRADING_MODE="paper"

# Risk Management
MAX_POSITION_SIZE="100"
STOP_LOSS_PERCENTAGE="5"
TAKE_PROFIT_PERCENTAGE="10"

# System Configuration
PORT="3000"
WEBSOCKET_PORT="8765"
NODE_ENV="production"
"@ | Out-File -FilePath .env -Encoding UTF8
```

### 步骤3：准备MySQL数据库

#### 3.1 启动MySQL服务
```cmd
net start MySQL80
```

#### 3.2 创建数据库和用户
```cmd
# 登录MySQL（以管理员身份）
mysql -u root -p
```

执行以下SQL命令：
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS trading_dashboard;

-- 创建用户
CREATE USER IF NOT EXISTS 'trading'@'localhost' IDENTIFIED BY 'Zdm351026';

-- 授予权限
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;

-- 验证
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user='trading';

-- 退出
exit;
```

### 步骤4：一键部署

```cmd
# 双击运行或在命令行执行
DEPLOY.bat
```

**重要提示：**
- 当脚本询问是否覆盖.env文件时，选择 **n (不覆盖)**
- 首次运行可能需要3-5分钟（下载依赖）

---

## 📝 手动部署（如果自动部署失败）

### 1. 检查环境
```cmd
python --version    # 应显示 Python 3.11+
node --version      # 应显示 v20+
mysql --version     # 应显示 8.0+
```

### 2. 安装全局依赖
```cmd
npm install -g pnpm
npm install -g pm2
npm install -g pm2-windows-startup
pm2-startup install
```

### 3. 安装项目依赖
```cmd
# Node.js依赖（可能需要几分钟）
pnpm install

# Python依赖
pip install -r requirements.txt
```

### 4. 初始化数据库
```cmd
# 确保.env文件已创建
# 导入数据库Schema
mysql -u trading -pZdm351026 trading_dashboard < database\schema.sql
```

### 5. 启动服务
```cmd
pm2 start ecosystem.config.cjs
pm2 save
```

---

## ✅ 验证部署

### 1. 检查服务状态
```cmd
pm2 list
```

**预期输出：**
```
┌────┬────────────────────┬──────────┬──────┬───────────┐
│ id │ name               │ mode     │ ↺    │ status    │
├────┼────────────────────┼──────────┼──────┼───────────┤
│ 0  │ trading-dashboard  │ fork     │ 0    │ online    │
│ 1  │ trading-bot        │ fork     │ 0    │ online    │
│ 2  │ telegram-bot       │ fork     │ 0    │ online    │
│ 3  │ websocket-server   │ fork     │ 0    │ online    │
│ 4  │ daily-report       │ fork     │ 0    │ online    │
└────┴────────────────────┴──────────┴──────┴───────────┘
```

所有5个服务状态应该都是 `online` ✅

### 2. 查看日志
```cmd
# 查看所有日志
pm2 logs

# 查看trading-bot日志
pm2 logs trading-bot --lines 50
```

**预期日志内容：**
- ✅ `[DB] Connected to localhost:3306/trading_dashboard`
- ✅ `[Telegram] MessageSendSuccess`
- ✅ `[OK] KuCoinTradeInitializeSuccess`
- ✅ `InitializeComplete`
- ✅ `TradeStart`

### 3. 访问Dashboard
打开浏览器访问：**http://localhost:3000**

应该能看到Trading Dashboard界面

### 4. 检查Telegram通知
打开Telegram，查看是否收到Bot启动通知

---

## 🔧 故障排除

### 问题1：数据库连接失败
```
Error: ER_ACCESS_DENIED_ERROR: Access denied for user 'trading'@'localhost'
```

**解决方法：**
```sql
-- 重新登录MySQL
mysql -u root -p

-- 删除并重新创建用户
DROP USER IF EXISTS 'trading'@'localhost';
CREATE USER 'trading'@'localhost' IDENTIFIED BY 'Zdm351026';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;

-- 测试连接
exit;
mysql -u trading -pZdm351026 trading_dashboard
```

### 问题2：端口被占用
```
Error: listen EADDRINUSE: address already in use :::3000
```

**解决方法：**
```cmd
# 查找占用端口的进程
netstat -ano | findstr :3000

# 结束进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F

# 或者修改.env中的PORT
# PORT="3001"
```

### 问题3：Telegram通知失败
```
Error: 401 Unauthorized
```

**检查清单：**
1. ✓ Bot Token是否正确
2. ✓ 是否已与Bot对话（在Telegram中发送 `/start`）
3. ✓ Chat ID是否正确

**测试Telegram连接：**
```cmd
python scripts\telegram_notifier.py
```

### 问题4：Python依赖安装失败
```
error: Microsoft Visual C++ 14.0 is required
```

**解决方法：**
1. 下载并安装 Visual C++ Build Tools
2. 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
3. 安装后重新运行：`pip install -r requirements.txt`

### 问题5：pnpm install 失败
```
Error: EACCES: permission denied
```

**解决方法：**
```cmd
# 以管理员身份运行PowerShell或CMD
# 清理缓存
pnpm store prune

# 重新安装
pnpm install
```

---

## 📞 服务管理

### 常用命令
```cmd
# 查看服务状态
pm2 list

# 查看所有日志
pm2 logs

# 查看特定服务日志
pm2 logs trading-bot --lines 100

# 重启所有服务
pm2 restart all

# 重启单个服务
pm2 restart trading-bot

# 停止所有服务
pm2 stop all

# 删除所有服务
pm2 delete all

# 实时监控
pm2 monit

# 保存当前配置
pm2 save
```

### 日志文件位置
```
C:\trading_dashboard_fixed\logs\
├── dashboard-error.log
├── dashboard-out.log
├── trading-bot-error.log
├── trading-bot-out.log
├── telegram-bot-error.log
├── telegram-bot-out.log
├── websocket-error.log
├── websocket-out.log
├── daily-report-error.log
└── daily-report-out.log
```

---

## ⚠️ 重要提示

### 安全建议
1. ✅ **不要分享.env文件** - 包含敏感API密钥和密码
2. ✅ **当前为Paper Trading模式** - 不会进行真实交易
3. ✅ **定期备份数据库** - 保护交易数据
4. ✅ **监控服务日志** - 及时发现问题

### 关于Paper Trading模式
- ✅ 当前配置为 `TRADING_MODE="paper"`
- ✅ 所有交易都是模拟的，不会使用真实资金
- ✅ 可以安全测试所有功能
- ✅ 不会影响KuCoin账户余额

### 切换到真实交易（谨慎！）
如需切换到真实交易：

1. 编辑 `.env` 文件
2. 将 `TRADING_MODE="paper"` 改为 `TRADING_MODE="live"`
3. 重启服务：`pm2 restart all`

**⚠️ 警告：真实交易模式会使用真实资金，请确保充分测试后再切换！**

---

## 📊 部署检查清单

### 部署前
- [ ] MySQL 8.0+ 已安装并运行
- [ ] Python 3.11+ 已安装
- [ ] Node.js 20+ 已安装
- [ ] 已下载并解压项目文件

### 部署中
- [ ] .env 文件已创建并包含正确配置
- [ ] MySQL数据库和用户已创建
- [ ] pnpm 和 PM2 已安装
- [ ] Node.js依赖安装成功
- [ ] Python依赖安装成功
- [ ] 数据库Schema导入成功

### 部署后
- [ ] 所有5个服务状态为 online
- [ ] Dashboard可访问 (http://localhost:3000)
- [ ] Telegram收到启动通知
- [ ] 日志无严重错误
- [ ] 已保存PM2配置 (`pm2 save`)

---

## 🎯 下一步

部署成功后：

### 1. 监控服务
```cmd
pm2 monit
```

### 2. 查看实时日志
```cmd
pm2 logs
```

### 3. 访问Dashboard
http://localhost:3000

### 4. 测试功能
- 查看实时行情
- 查看交易记录
- 测试Telegram通知
- 查看风险管理

### 5. 定期维护
```cmd
# 每天查看日志
pm2 logs --lines 100

# 每周重启服务
pm2 restart all

# 定期备份数据库
mysqldump -u trading -pZdm351026 trading_dashboard > backup.sql
```

---

## 📚 相关文档

- `README_WINDOWS_DEPLOY.md` - 完整部署指南
- `DEPLOYMENT_TOOLS.md` - 部署工具说明
- `FIXES_APPLIED.md` - 修复内容详情
- `TEST_REPORT.md` - 测试报告

---

**祝部署顺利！** 🚀

如有问题，请：
1. 查看日志：`pm2 logs`
2. 参考故障排除章节
3. 查看其他文档

当前为Paper Trading模式，可以安全测试所有功能！

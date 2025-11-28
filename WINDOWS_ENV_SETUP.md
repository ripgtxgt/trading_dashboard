# Windows服务器环境变量配置指南

## 必需的环境变量

在Windows服务器上，请确保`.env`文件包含以下配置：

### 1. 数据库配置
```env
DATABASE_URL=mysql://trading:trading123@localhost:3306/trading_dashboard
```

**重要说明：**
- 用户名：`trading`
- 密码：`trading123`（您提供的密码）
- 数据库名：`trading_dashboard`

### 2. KuCoin API配置
```env
KUCOIN_API_KEY=6902f625f9a9a300014c3976
KUCOIN_API_SECRET=d71e4e3d-4369-4e77-94f8-fd456c5e0387
KUCOIN_API_PASSPHRASE=x5gU7dnL6bvrvbV!
```

### 3. Telegram配置
```env
TELEGRAM_BOT_TOKEN=7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U
TELEGRAM_CHAT_ID=5374455360
```

### 4. OAuth配置（可选，用于Dashboard登录）
```env
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://manus.im/oauth
```

**注意：** 如果不需要OAuth登录功能，可以忽略这些配置，Dashboard会显示警告但不影响核心功能。

### 5. 其他配置
```env
PORT=3000
WEBHOOK_SECRET=your-webhook-secret-here
NODE_ENV=production
```

---

## 完整的.env文件示例

```env
# Database
DATABASE_URL=mysql://trading:trading123@localhost:3306/trading_dashboard

# KuCoin API
KUCOIN_API_KEY=6902f625f9a9a300014c3976
KUCOIN_API_SECRET=d71e4e3d-4369-4e77-94f8-fd456c5e0387
KUCOIN_API_PASSPHRASE=x5gU7dnL6bvrvbV!

# Telegram
TELEGRAM_BOT_TOKEN=7965687699:AAHWCHsHPyJEuvaFVU8yLCvSPohT8kU3G4U
TELEGRAM_CHAT_ID=5374455360

# OAuth (Optional)
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://manus.im/oauth

# Server
PORT=3000
WEBHOOK_SECRET=your-webhook-secret-here
NODE_ENV=production
```

---

## 配置步骤

### 步骤1：创建或编辑.env文件
```powershell
cd C:\trading_dashboard_fixed
notepad .env
```

### 步骤2：复制上面的完整配置并保存

### 步骤3：验证数据库连接
```powershell
mysql -u trading -p
# 输入密码：trading123

# 在MySQL中执行：
USE trading_dashboard;
SHOW TABLES;
EXIT;
```

### 步骤4：重启所有服务
```powershell
pm2 restart all
pm2 logs --lines 20
```

---

## 故障排除

### 问题1：trading-bot不断重启
**原因：** 数据库连接失败

**解决方案：**
1. 检查MySQL服务是否运行：`Get-Service MySQL*`
2. 验证数据库密码是否正确
3. 重新创建数据库用户（见TRADING_BOT_FIX.md）

### 问题2：websocket-server报错"No module named 'test_mode'"
**原因：** 缺少test_mode.py模块

**解决方案：**
1. 确保从GitHub拉取最新代码：`git pull origin main`
2. 检查`scripts/test_mode.py`文件是否存在
3. 重启websocket-server：`pm2 restart websocket-server`

### 问题3：Dashboard显示OAuth错误
**原因：** 缺少OAuth环境变量

**解决方案：**
- 如果需要OAuth登录：添加上面的OAuth配置
- 如果不需要：忽略警告，不影响核心功能

---

## 验证配置

运行以下命令验证所有配置正确：

```powershell
# 1. 检查.env文件
cat .env

# 2. 测试数据库连接
mysql -u trading -ptrading123 -e "SELECT 1"

# 3. 测试Python脚本
python scripts/test_bot_simple.py

# 4. 查看服务状态
pm2 list
pm2 logs --lines 50
```

---

## 下一步

配置完成后：
1. 重启所有服务：`pm2 restart all`
2. 访问Dashboard：`http://localhost:3000` 或 `https://cryptoalpha.vip`
3. 检查所有服务状态：`pm2 list`（应该全部显示`online`）

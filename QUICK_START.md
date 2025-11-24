# 🚀 快速开始指南

## 适用场景

本指南适用于Windows Server 2022服务器，帮助您快速部署10U战神滚仓策略交易系统。

---

## 📦 第一步：上传项目文件

将整个 `trading_dashboard` 文件夹复制到服务器的 `C:\` 目录下

完整路径应该是：`C:\trading_dashboard`

---

## 🔍 第二步：检测环境

**双击运行**：`check_environment.bat`

这个脚本会自动检测：
- ✅ Node.js 是否安装（需要 v18+）
- ✅ Python 是否安装（需要 3.8+）
- ✅ MySQL 是否安装并运行
- ✅ PM2 是否安装
- ✅ 端口 3000 和 8765 是否可用

**如果检测未通过**，请按照提示安装缺失的软件。

---

## ⚙️ 第三步：配置环境变量

1. 找到项目根目录下的 `.env.example` 文件
2. 复制一份并重命名为 `.env`
3. 用记事本打开 `.env` 文件
4. 修改以下配置：

```env
# 数据库配置（必须）
DATABASE_URL="mysql://trading:你的密码@localhost:3306/trading_dashboard"

# KuCoin API 配置（必须）
KUCOIN_API_KEY="你的API密钥"
KUCOIN_API_SECRET="你的API密钥"
KUCOIN_API_PASSPHRASE="你的API密码短语"

# Telegram Bot 配置（可选）
TELEGRAM_BOT_TOKEN="你的Bot Token"
TELEGRAM_CHAT_ID="你的Chat ID"

# JWT 密钥（必须，随机字符串）
JWT_SECRET="随机生成的32位以上字符串"
```

**重要提示**：
- 数据库密码是您在安装MySQL时设置的
- KuCoin API密钥需要在KuCoin官网创建
- Telegram配置是可选的，但强烈建议配置（用于接收交易通知）

---

## 🚀 第四步：一键部署

**右键点击** `deploy.bat`，选择 **“以管理员身份运行”**

脚本会自动完成：
1. ✅ 安装所有依赖（Node.js + Python）
2. ✅ 自动安装 TA-Lib（技术指标库，预编译版本）
3. ✅ 执行数据库迁移
4. ✅ 构建前端
5. ✅ 配置PM2
6. ✅ 启动服务
7. ✅ 配置防火墙
8. ✅ 配置开机自启

**预计耗时**：5-10分钟（取决于网络速度）

---

## 🎉 第五步：访问系统

部署完成后，打开浏览器访问：

```
http://服务器IP:3000
```

或

```
http://localhost:3000
```

您应该能看到交易监控面板的主界面。

---

## 🤖 第六步：启动交易机器人（可选）

**警告**：在启动交易机器人前，请确保：
- ✅ 已充分测试策略参数
- ✅ 已设置合理的止损止盈
- ✅ 账户余额充足
- ✅ 已配置Telegram通知

**双击运行**：`start_trading_bot.bat`

按照提示输入 `YES` 确认启动。

---

## 📊 常用操作

### 查看服务状态

打开PowerShell或命令提示符：

```powershell
pm2 list
```

### 查看日志

```powershell
pm2 logs
```

### 重启服务

```powershell
pm2 restart all
```

### 停止服务

**双击运行**：`stop_all.bat`

或使用命令：

```powershell
pm2 stop all
```

### 启动所有服务

**双击运行**：`start_all.bat`

---

## ❓ 常见问题

### 1. 双击 .bat 文件闪退

**原因**：脚本执行过程中出现错误

**解决方案**：
1. 右键点击 .bat 文件
2. 选择 "编辑"
3. 在最后一行添加 `pause`
4. 保存后再次运行，查看错误信息

### 2. 提示 "PM2 未安装"

**解决方案**：

打开PowerShell（以管理员身份），运行：

```powershell
npm install -g pm2
npm install -g pm2-windows-startup
```

### 3. 数据库连接失败

**检查清单**：
1. MySQL 服务是否运行
2. `.env` 中的数据库密码是否正确
3. 数据库 `trading_dashboard` 是否已创建

**创建数据库**：

```powershell
mysql -u root -p
```

```sql
CREATE DATABASE trading_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 无法访问 Dashboard

**检查清单**：
1. 服务是否正常运行：`pm2 list`
2. 防火墙是否开放端口 3000
3. 查看服务日志：`pm2 logs trading-dashboard`

**开放防火墙**（以管理员身份运行PowerShell）：

```powershell
New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
```

---

## 📚 详细文档

- **完整部署指南**：`WINDOWS_SERVER_DEPLOYMENT.md`
- **Telegram配置**：`TELEGRAM_SETUP_GUIDE.md`
- **项目说明**：`README.md`

---

## 🆘 需要帮助？

如遇到问题：

1. **查看日志**：`pm2 logs`
2. **检查配置**：确认 `.env` 文件配置正确
3. **重启服务**：`pm2 restart all`
4. **查看文档**：参考详细部署指南

---

## ✅ 部署检查清单

部署完成后，请确认：

- [ ] 所有服务正常运行（`pm2 list` 显示 online）
- [ ] 可以访问 Dashboard（http://服务器IP:3000）
- [ ] 数据库连接正常（Dashboard 显示数据）
- [ ] WebSocket 连接正常（Dashboard 右上角显示"已连接"）
- [ ] 已修改所有默认密码
- [ ] 已配置防火墙规则
- [ ] 已配置 Telegram 通知（可选但推荐）
- [ ] 已设置定期备份

---

**祝您部署顺利！** 🎊

如有问题，请参考 `WINDOWS_SERVER_DEPLOYMENT.md` 获取更详细的帮助。

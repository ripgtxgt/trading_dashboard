# Windows Server 2022 部署指南

## 📋 目录

- [系统要求](#系统要求)
- [准备工作](#准备工作)
- [快速部署](#快速部署)
- [手动部署](#手动部署)
- [配置说明](#配置说明)
- [启动服务](#启动服务)
- [常见问题](#常见问题)
- [维护管理](#维护管理)

---

## 系统要求

### 硬件要求

- **CPU**: 2核心或以上
- **内存**: 4GB 或以上（推荐 8GB）
- **硬盘**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 软件要求

| 软件 | 版本要求 | 必需 | 说明 |
|------|---------|------|------|
| Windows Server | 2019/2022 | ✅ | 操作系统 |
| Node.js | 18.x 或更高 | ✅ | JavaScript 运行环境 |
| Python | 3.8 或更高 | ✅ | Python 运行环境 |
| MySQL | 5.7 或更高 | ✅ | 数据库 |
| PM2 | 最新版 | ✅ | 进程管理器 |
| Git | 最新版 | ⚪ | 版本控制（可选） |

---

## 准备工作

### 1. 安装 Node.js

1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载 **LTS 版本**（推荐 v20.x）
3. 运行安装程序，按默认选项安装
4. 验证安装：

```powershell
node -v
npm -v
```

### 2. 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 **Python 3.11** 或更高版本
3. **重要**: 安装时勾选 "Add Python to PATH"
4. 验证安装：

```powershell
python --version
pip --version
```

### 3. 安装 MySQL

1. 访问 [MySQL 官网](https://dev.mysql.com/downloads/mysql/)
2. 下载 **MySQL Community Server**
3. 运行安装程序，记住设置的 root 密码
4. 启动 MySQL 服务：

```powershell
Start-Service MySQL80
```

5. 创建数据库：

```powershell
mysql -u root -p
```

```sql
CREATE DATABASE trading_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'trading'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. 安装 PM2

```powershell
npm install -g pm2
npm install -g pm2-windows-startup
```

配置开机自启：

```powershell
pm2-startup install
```

---

## 快速部署

### 方式一：使用自动化脚本（推荐）

1. **上传项目文件到服务器**

   将整个项目文件夹复制到 `C:\trading_dashboard`

2. **运行环境检测**

   右键点击 `scripts\check_windows_environment.ps1`，选择 "使用 PowerShell 运行"

   或在 PowerShell 中执行：

   ```powershell
   cd C:\trading_dashboard
   powershell -ExecutionPolicy Bypass -File scripts\check_windows_environment.ps1
   ```

3. **配置环境变量**

   复制 `.env.example` 为 `.env`，编辑配置：

   ```powershell
   copy .env.example .env
   notepad .env
   ```

   **必须配置的项**：

   ```env
   # 数据库配置
   DATABASE_URL="mysql://trading:your_password@localhost:3306/trading_dashboard"

   # KuCoin API 配置
   KUCOIN_API_KEY="your_api_key"
   KUCOIN_API_SECRET="your_api_secret"
   KUCOIN_API_PASSPHRASE="your_passphrase"

   # Telegram Bot 配置（可选）
   TELEGRAM_BOT_TOKEN="your_bot_token"
   TELEGRAM_CHAT_ID="your_chat_id"

   # JWT 密钥（随机生成）
   JWT_SECRET="your_random_secret_key_here"
   ```

4. **运行自动化部署脚本**

   右键点击 `scripts\deploy_windows.ps1`，选择 "使用 PowerShell 运行"

   或在 PowerShell 中执行：

   ```powershell
   cd C:\trading_dashboard
   powershell -ExecutionPolicy Bypass -File scripts\deploy_windows.ps1
   ```

   脚本会自动完成：
   - ✅ 安装 Node.js 依赖
   - ✅ 安装 Python 依赖
   - ✅ 执行数据库迁移
   - ✅ 构建前端
   - ✅ 配置 PM2
   - ✅ 启动服务
   - ✅ 配置防火墙
   - ✅ 配置开机自启

5. **访问系统**

   打开浏览器，访问：`http://服务器IP:3000`

---

## 手动部署

如果自动化脚本失败，可以手动执行以下步骤：

### 1. 上传项目文件

将项目文件复制到 `C:\trading_dashboard`

### 2. 配置环境变量

```powershell
cd C:\trading_dashboard
copy .env.example .env
notepad .env
```

编辑 `.env` 文件，填入正确的配置信息。

### 3. 安装依赖

**安装 Node.js 依赖**：

```powershell
# 使用 pnpm（推荐）
npm install -g pnpm
pnpm install

# 或使用 npm
npm install
```

**安装 Python 依赖**：

```powershell
pip install -r scripts\requirements.txt
```

### 4. 数据库迁移

```powershell
# 使用 pnpm
pnpm db:push

# 或使用 npm
npm run db:push
```

### 5. 构建前端

```powershell
# 使用 pnpm
pnpm build

# 或使用 npm
npm run build
```

### 6. 创建日志目录

```powershell
mkdir logs
```

### 7. 启动服务

**使用 PM2 启动**：

```powershell
# 启动所有服务
pm2 start ecosystem.config.js

# 或单独启动
pm2 start pnpm --name "trading-dashboard" -- start
pm2 start python --name "websocket-server" -- scripts/websocket_pusher.py

# 保存配置
pm2 save
```

### 8. 配置防火墙

```powershell
# 以管理员身份运行 PowerShell
New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
```

### 9. 配置开机自启

```powershell
pm2-startup install
pm2 save
```

---

## 配置说明

### 环境变量详解

#### 数据库配置

```env
# MySQL 连接字符串
DATABASE_URL="mysql://用户名:密码@主机:端口/数据库名"

# 示例
DATABASE_URL="mysql://trading:password123@localhost:3306/trading_dashboard"
```

#### KuCoin API 配置

1. 登录 [KuCoin](https://www.kucoin.com/)
2. 进入 **API Management**
3. 创建新的 API Key
4. **权限设置**：
   - ✅ General（通用）
   - ✅ Trade（交易）
   - ❌ Transfer（转账）- 不建议开启
   - ❌ Withdraw（提现）- 不建议开启

```env
KUCOIN_API_KEY="your_api_key_here"
KUCOIN_API_SECRET="your_api_secret_here"
KUCOIN_API_PASSPHRASE="your_passphrase_here"
```

#### Telegram Bot 配置（可选）

详细配置请参考 `TELEGRAM_SETUP_GUIDE.md`

```env
TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TELEGRAM_CHAT_ID="123456789"
```

#### JWT 密钥

用于用户会话加密，必须是随机字符串：

```env
JWT_SECRET="your_random_secret_key_at_least_32_characters_long"
```

生成随机密钥：

```powershell
# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

---

## 启动服务

### 使用 PM2 管理服务

**查看服务状态**：

```powershell
pm2 list
```

**启动服务**：

```powershell
# 启动所有服务
pm2 start ecosystem.config.js

# 启动特定服务
pm2 start trading-dashboard
pm2 start websocket-server
pm2 start trading-bot
pm2 start telegram-bot
```

**停止服务**：

```powershell
# 停止所有服务
pm2 stop all

# 停止特定服务
pm2 stop trading-dashboard
```

**重启服务**：

```powershell
# 重启所有服务
pm2 restart all

# 重启特定服务
pm2 restart trading-dashboard
```

**查看日志**：

```powershell
# 查看所有日志
pm2 logs

# 查看特定服务日志
pm2 logs trading-dashboard
pm2 logs trading-bot

# 清空日志
pm2 flush
```

**删除服务**：

```powershell
# 删除所有服务
pm2 delete all

# 删除特定服务
pm2 delete trading-dashboard
```

---

## 常见问题

### 1. PowerShell 脚本无法运行

**问题**: 提示 "无法加载文件，因为在此系统上禁止运行脚本"

**解决方案**:

```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或临时绕过
powershell -ExecutionPolicy Bypass -File scripts\deploy_windows.ps1
```

### 2. 端口被占用

**问题**: 提示端口 3000 或 8765 已被占用

**解决方案**:

```powershell
# 查看占用端口的进程
netstat -ano | findstr :3000

# 结束进程（替换 PID 为实际进程 ID）
taskkill /PID 进程ID /F
```

### 3. 数据库连接失败

**问题**: 提示无法连接到数据库

**检查清单**:

1. MySQL 服务是否运行：

   ```powershell
   Get-Service MySQL*
   ```

2. 数据库是否存在：

   ```powershell
   mysql -u root -p
   SHOW DATABASES;
   ```

3. `.env` 中的 `DATABASE_URL` 是否正确

4. 用户权限是否正确：

   ```sql
   SHOW GRANTS FOR 'trading'@'localhost';
   ```

### 4. PM2 服务无法启动

**问题**: PM2 启动服务失败

**解决方案**:

```powershell
# 查看详细错误日志
pm2 logs trading-dashboard --lines 50

# 删除旧配置重新启动
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
```

### 5. Python 模块导入失败

**问题**: 提示 "No module named 'ccxt'" 等错误

**解决方案**:

```powershell
# 重新安装 Python 依赖
pip install -r scripts\requirements.txt --force-reinstall

# 或单独安装缺失的模块
pip install ccxt websocket-client requests pandas
```

### 6. 防火墙阻止访问

**问题**: 无法从其他电脑访问 Dashboard

**解决方案**:

```powershell
# 以管理员身份运行
New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow

# 检查防火墙规则
Get-NetFirewallRule -DisplayName "Trading Dashboard"
```

### 7. 前端构建失败

**问题**: `pnpm build` 或 `npm run build` 失败

**解决方案**:

```powershell
# 清理缓存重新安装
rm -r node_modules
rm pnpm-lock.yaml  # 或 package-lock.json
pnpm install       # 或 npm install
pnpm build         # 或 npm run build
```

### 8. WebSocket 连接失败

**问题**: Dashboard 显示 "WebSocket 未连接"

**检查清单**:

1. WebSocket 服务是否运行：

   ```powershell
   pm2 list
   ```

2. 端口 8765 是否开放：

   ```powershell
   Test-NetConnection -ComputerName localhost -Port 8765
   ```

3. 查看 WebSocket 日志：

   ```powershell
   pm2 logs websocket-server
   ```

---

## 维护管理

### 日常维护

**每日检查**:

```powershell
# 查看服务状态
pm2 list

# 查看系统资源使用
pm2 monit

# 查看最近日志
pm2 logs --lines 20
```

**每周维护**:

```powershell
# 清理日志
pm2 flush

# 重启服务
pm2 restart all

# 检查更新
cd C:\trading_dashboard
git pull  # 如果使用 Git
pnpm install
pnpm build
pm2 restart all
```

### 备份数据

**备份数据库**:

```powershell
# 创建备份目录
mkdir C:\backups

# 备份数据库
mysqldump -u trading -p trading_dashboard > C:\backups\trading_dashboard_backup.sql

# 恢复数据库
mysql -u trading -p trading_dashboard < C:\backups\trading_dashboard_backup.sql
```

**备份配置文件**:

```powershell
# 备份 .env 文件
copy C:\trading_dashboard\.env C:\backups\.env.backup

# 备份 PM2 配置
pm2 save
copy $env:USERPROFILE\.pm2\dump.pm2 C:\backups\dump.pm2.backup
```

### 更新系统

1. **停止服务**:

   ```powershell
   pm2 stop all
   ```

2. **备份数据**（参考上面的备份步骤）

3. **更新代码**:

   ```powershell
   cd C:\trading_dashboard
   git pull  # 或手动替换文件
   ```

4. **安装依赖**:

   ```powershell
   pnpm install
   pip install -r scripts\requirements.txt
   ```

5. **数据库迁移**:

   ```powershell
   pnpm db:push
   ```

6. **构建前端**:

   ```powershell
   pnpm build
   ```

7. **重启服务**:

   ```powershell
   pm2 restart all
   ```

### 监控和告警

**使用 PM2 监控**:

```powershell
# 实时监控
pm2 monit

# 查看进程信息
pm2 info trading-dashboard

# 查看资源使用
pm2 describe trading-dashboard
```

**配置 Telegram 告警**:

参考 `TELEGRAM_SETUP_GUIDE.md` 配置 Telegram Bot，系统会自动发送：

- 交易信号通知
- 风险警告
- 系统错误告警
- 每日报告

---

## 性能优化

### 1. 数据库优化

```sql
-- 添加索引
ALTER TABLE trades ADD INDEX idx_created_at (created_at);
ALTER TABLE trades ADD INDEX idx_symbol (symbol);

-- 清理旧数据（保留最近 3 个月）
DELETE FROM trades WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);
```

### 2. 日志管理

```powershell
# 配置日志轮转（在 ecosystem.config.js 中）
# 限制日志文件大小
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

### 3. 内存优化

```powershell
# 设置最大内存限制（在 ecosystem.config.js 中）
# max_memory_restart: '500M'

# 手动重启释放内存
pm2 restart all
```

---

## 安全建议

### 1. 防火墙配置

只开放必要的端口：

```powershell
# 仅允许特定 IP 访问
New-NetFirewallRule -DisplayName "Trading Dashboard - Specific IP" `
  -Direction Inbound `
  -LocalPort 3000 `
  -Protocol TCP `
  -Action Allow `
  -RemoteAddress "你的IP地址"
```

### 2. API 密钥安全

- ✅ 不要在 KuCoin API 中开启提现权限
- ✅ 设置 IP 白名单
- ✅ 定期更换 API 密钥
- ✅ 不要将 `.env` 文件提交到 Git

### 3. 数据库安全

```sql
-- 限制数据库用户权限
REVOKE ALL PRIVILEGES ON *.* FROM 'trading'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 系统更新

定期更新系统和依赖：

```powershell
# 更新 Node.js 包
pnpm update

# 更新 Python 包
pip list --outdated
pip install --upgrade 包名

# Windows 系统更新
sconfig  # Server Manager
```

---

## 技术支持

如遇到问题，请按以下顺序排查：

1. **查看日志**: `pm2 logs`
2. **检查配置**: 确认 `.env` 文件配置正确
3. **重启服务**: `pm2 restart all`
4. **查看文档**: 参考 `README.md` 和其他文档
5. **联系支持**: 提供详细的错误日志和配置信息

---

## 附录

### A. 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 3000 | Web Dashboard | 前端界面 |
| 8765 | WebSocket | 实时数据推送 |
| 3306 | MySQL | 数据库 |

### B. 目录结构

```
C:\trading_dashboard\
├── client/              # 前端代码
├── server/              # 后端代码
├── scripts/             # Python 脚本
│   ├── kucoin_api.py   # 交易机器人
│   ├── websocket_pusher.py  # WebSocket 服务
│   ├── telegram_bot.py # Telegram Bot
│   └── requirements.txt # Python 依赖
├── logs/                # 日志文件
├── .env                 # 环境变量配置
├── ecosystem.config.js  # PM2 配置
└── package.json         # Node.js 配置
```

### C. 常用命令速查

```powershell
# PM2 命令
pm2 list                 # 查看服务列表
pm2 logs                 # 查看日志
pm2 monit                # 实时监控
pm2 restart all          # 重启所有服务
pm2 stop all             # 停止所有服务
pm2 save                 # 保存配置

# 数据库命令
mysql -u trading -p      # 连接数据库
mysqldump -u trading -p trading_dashboard > backup.sql  # 备份

# 服务管理
Get-Service MySQL*       # 查看 MySQL 服务
Start-Service MySQL80    # 启动 MySQL
Stop-Service MySQL80     # 停止 MySQL

# 网络检查
Test-NetConnection -ComputerName localhost -Port 3000  # 测试端口
netstat -ano | findstr :3000  # 查看端口占用
```

---

**部署完成后，请务必**：

1. ✅ 修改所有默认密码
2. ✅ 配置防火墙规则
3. ✅ 设置定期备份
4. ✅ 启用 Telegram 告警
5. ✅ 测试所有功能

祝您部署顺利！🚀

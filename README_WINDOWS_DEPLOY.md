# Trading Dashboard - Windows一键部署指南

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [常见问题](#常见问题)
- [手动部署](#手动部署)

---

## 系统要求

### 必需组件

| 组件 | 最低版本 | 推荐版本 | 下载地址 |
|------|---------|---------|----------|
| Windows | Server 2019 | Server 2022 | - |
| Python | 3.11 | 3.12+ | https://www.python.org/downloads/ |
| Node.js | 20.0 | 22.0+ | https://nodejs.org/ |
| MySQL | 8.0 | 8.0+ | https://dev.mysql.com/downloads/mysql/ |

### 可选组件（自动安装）

- **pnpm** - Node.js包管理器（部署时自动安装）
- **PM2** - 进程管理器（部署时自动安装）
- **Git** - 版本控制（可选）

### 硬件要求

- **CPU:** 2核心或更多
- **内存:** 4GB或更多
- **磁盘:** 10GB可用空间（含依赖）
- **网络:** 稳定的互联网连接

---

## 快速开始

### 🚀 三步部署

#### 1. 检查环境

双击运行 `check-environment.ps1`

```powershell
# 或在PowerShell中运行
.\check-environment.ps1
```

#### 2. 配置参数

双击运行 `quick-config.ps1`

```powershell
# 或在PowerShell中运行
.\quick-config.ps1
```

按提示输入：
- KuCoin API密钥
- 数据库连接信息
- Telegram Bot配置
- 交易参数

#### 3. 一键部署

双击运行 `DEPLOY.bat`

```cmd
# 或在命令行中运行
DEPLOY.bat
```

等待部署完成，访问 http://localhost:3000

---

## 详细步骤

### 步骤1：准备环境

#### 1.1 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载Python 3.11或更高版本
3. 安装时勾选 **"Add Python to PATH"**
4. 验证安装：

```cmd
python --version
pip --version
```

#### 1.2 安装Node.js

1. 访问 https://nodejs.org/
2. 下载LTS版本（推荐v22）
3. 默认安装即可
4. 验证安装：

```cmd
node --version
npm --version
```

#### 1.3 安装MySQL

1. 访问 https://dev.mysql.com/downloads/mysql/
2. 下载MySQL 8.0
3. 安装时设置root密码
4. 创建数据库和用户：

```sql
CREATE DATABASE trading_dashboard;
CREATE USER 'trading'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
```

### 步骤2：环境检查

运行环境检查工具：

```powershell
.\check-environment.ps1
```

确保所有必需组件都显示 ✓

### 步骤3：配置应用

#### 方式1：使用配置向导（推荐）

```powershell
.\quick-config.ps1
```

#### 方式2：手动编辑.env

复制 `.env.example` 为 `.env`，然后编辑：

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

# 交易配置
LEVERAGE=100
INITIAL_CAPITAL=10
```

### 步骤4：一键部署

运行部署脚本：

```cmd
DEPLOY.bat
```

部署脚本会自动：
1. ✓ 检查管理员权限
2. ✓ 验证环境依赖
3. ✓ 安装pnpm和PM2
4. ✓ 安装Node.js依赖
5. ✓ 安装Python依赖
6. ✓ 初始化数据库
7. ✓ 启动所有服务

### 步骤5：验证部署

#### 5.1 检查服务状态

```cmd
pm2 list
```

应该看到5个服务都是 `online` 状态：
- trading-dashboard
- trading-bot
- telegram-bot
- websocket-server
- daily-report

#### 5.2 查看日志

```cmd
# 查看所有日志
pm2 logs

# 查看特定服务日志
pm2 logs trading-bot
```

#### 5.3 访问Dashboard

打开浏览器访问：http://localhost:3000

---

## 常见问题

### Q1: PowerShell脚本无法运行

**错误：** "无法加载文件，因为在此系统上禁止运行脚本"

**解决：** 以管理员身份运行PowerShell，执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q2: 端口被占用

**错误：** "Error: listen EADDRINUSE: address already in use :::3000"

**解决：** 

```cmd
# 查找占用端口的进程
netstat -ano | findstr :3000

# 结束进程（替换PID）
taskkill /PID <PID> /F
```

### Q3: MySQL连接失败

**错误：** "ER_ACCESS_DENIED_ERROR: Access denied for user"

**解决：** 

1. 检查.env中的数据库配置
2. 确认MySQL服务正在运行
3. 验证用户权限：

```sql
SHOW GRANTS FOR 'trading'@'localhost';
```

### Q4: Python依赖安装失败

**错误：** "error: Microsoft Visual C++ 14.0 is required"

**解决：** 

1. 安装Visual C++ Build Tools
2. 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Q5: PM2服务启动失败

**错误：** "PM2 error: spawn python ENOENT"

**解决：** 

确保Python在系统PATH中：

```cmd
# 查看Python路径
where python

# 如果没有输出，需要添加Python到PATH
```

### Q6: Telegram通知不工作

**检查：**

1. Bot Token是否正确
2. Chat ID是否正确
3. 是否已与Bot对话（发送/start）

**测试：**

```cmd
python scripts\telegram_notifier.py
```

---

## 手动部署

如果自动部署失败，可以手动执行以下步骤：

### 1. 安装pnpm

```cmd
npm install -g pnpm
```

### 2. 安装PM2

```cmd
npm install -g pm2
npm install -g pm2-windows-startup
pm2-startup install
```

### 3. 安装Node.js依赖

```cmd
pnpm install
```

### 4. 安装Python依赖

```cmd
pip install -r requirements.txt
```

### 5. 初始化数据库

```cmd
mysql -u trading -p trading_dashboard < database\schema.sql
```

### 6. 启动服务

```cmd
pm2 start ecosystem.config.cjs
pm2 save
```

---

## 服务管理

### 常用命令

```cmd
# 查看服务状态
pm2 list

# 查看日志
pm2 logs

# 重启所有服务
pm2 restart all

# 重启单个服务
pm2 restart trading-bot

# 停止所有服务
pm2 stop all

# 删除所有服务
pm2 delete all

# 监控服务
pm2 monit

# 保存当前服务列表
pm2 save

# 开机自启
pm2 startup
```

### 日志文件位置

```
logs/
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

## 卸载

### 停止并删除所有服务

```cmd
pm2 delete all
pm2 kill
```

### 卸载PM2

```cmd
npm uninstall -g pm2
npm uninstall -g pm2-windows-startup
```

### 删除项目文件

直接删除项目目录即可

---

## 技术支持

### 文档

- `DEPLOYMENT_INSTRUCTIONS.md` - 详细部署说明
- `FIXES_APPLIED.md` - 修复内容详情
- `TEST_REPORT.md` - 测试报告
- `scripts/README.md` - 脚本说明

### 日志调试

```cmd
# 实时查看日志
pm2 logs trading-bot --lines 100

# 清空日志
pm2 flush
```

### 重新部署

```cmd
# 停止所有服务
pm2 delete all

# 重新运行部署
DEPLOY.bat
```

---

## 更新日志

### v1.0 (2025-11-26)

- ✓ 初始版本
- ✓ 一键部署功能
- ✓ 环境检查工具
- ✓ 配置向导
- ✓ 自动依赖安装
- ✓ PM2服务管理

---

**祝部署顺利！** 🎉

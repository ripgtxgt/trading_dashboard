# 部署指南

本指南说明如何在Windows Server上部署Trading Dashboard应用。

## 部署概览

**服务器信息：**
- 服务器：Windows Server 2022
- IP地址：13.113.194.218
- 域名：cryptoalpha.vip
- 项目目录：`C:\trading_dashboard`

**服务架构：**
```
GitHub Actions (CI/CD)
    ↓ (webhook)
Windows Server
    ├── Nginx (端口80/443) → 反向代理
    ├── Webhook Server (端口9000) → 接收部署通知
    ├── Node.js App (端口3000) → 主应用
    ├── Trading Bot → 交易机器人
    └── Python Scripts → 策略脚本
```

## 前置条件

### 1. 安装必要软件

```powershell
# Node.js 22+
# 下载地址: https://nodejs.org/

# pnpm
npm install -g pnpm

# PM2 (进程管理器)
npm install -g pm2
pm2 install pm2-windows-startup
pm2-startup install

# Git
# 下载地址: https://git-scm.com/download/win

# Python 3.11+
# 下载地址: https://www.python.org/downloads/

# Nginx
# 下载地址: https://nginx.org/en/download.html
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# Database
DATABASE_URL=your_database_connection_string

# OAuth
JWT_SECRET=your_jwt_secret
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://portal.manus.im

# App Info
VITE_APP_ID=your_app_id
VITE_APP_TITLE=10U战神滚仓策略
VITE_APP_LOGO=your_logo_url
OWNER_OPEN_ID=your_open_id
OWNER_NAME=your_name

# Manus Built-in APIs
BUILT_IN_FORGE_API_URL=https://forge-api.manus.im
BUILT_IN_FORGE_API_KEY=your_api_key
VITE_FRONTEND_FORGE_API_KEY=your_frontend_api_key
VITE_FRONTEND_FORGE_API_URL=https://forge-api.manus.im

# Telegram Bot (可选)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# GitHub Webhook Secret
WEBHOOK_SECRET=your_webhook_secret
```

## 初始部署

### 1. 克隆代码

```powershell
# 进入工作目录
cd C:\

# 克隆仓库
git clone https://github.com/ripgtxgt/trading_dashboard.git
cd trading_dashboard

# 切换到main分支
git checkout main
```

### 2. 安装依赖

```powershell
# 安装Node.js依赖
pnpm install

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置数据库

```powershell
# 推送数据库schema
pnpm db:push
```

### 4. 构建应用

```powershell
# 构建前端和后端
pnpm build
```

### 5. 配置PM2

使用项目根目录的 `ecosystem.config.cjs` 文件：

```javascript
module.exports = {
  apps: [
    {
      name: "trading-dashboard",
      script: "dist/index.js",
      cwd: "C:/trading_dashboard",
      instances: 1,
      exec_mode: "fork",
      env: {
        NODE_ENV: "production",
        PORT: 3000,
      },
      error_file: "C:/trading_dashboard/logs/app-error.log",
      out_file: "C:/trading_dashboard/logs/app-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
    {
      name: "webhook-server",
      script: "deployment/webhook-deploy-server.cjs",
      cwd: "C:/trading_dashboard",
      instances: 1,
      exec_mode: "fork",
      env: {
        PORT: 9000,
        WEBHOOK_SECRET: process.env.WEBHOOK_SECRET,
      },
      error_file: "C:/trading_dashboard/logs/webhook-error.log",
      out_file: "C:/trading_dashboard/logs/webhook-out.log",
    },
    {
      name: "trading-bot",
      script: "scripts/trading_bot.py",
      cwd: "C:/trading_dashboard",
      interpreter: "python",
      instances: 1,
      exec_mode: "fork",
      error_file: "C:/trading_dashboard/logs/bot-error.log",
      out_file: "C:/trading_dashboard/logs/bot-out.log",
    },
  ],
};
```

### 6. 启动服务

```powershell
# 创建日志目录
New-Item -ItemType Directory -Force -Path C:\trading_dashboard\logs

# 启动所有服务
pm2 start ecosystem.config.cjs

# 保存PM2配置
pm2 save

# 查看服务状态
pm2 status
```

### 7. 配置Nginx

参考 `deployment/NGINX_SETUP.md` 配置Nginx反向代理。

```powershell
# 复制Nginx配置
Copy-Item deployment\nginx.conf C:\nginx\conf\nginx.conf

# 测试配置
C:\nginx\nginx.exe -t

# 启动Nginx
Start-Process C:\nginx\nginx.exe
```

### 8. 配置防火墙

```powershell
# 开放HTTP端口
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 开放HTTPS端口
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

## 自动部署（GitHub Actions）

### 1. 配置GitHub Secrets

在GitHub仓库设置中添加以下Secrets：

- `TELEGRAM_BOT_TOKEN` - Telegram机器人Token
- `TELEGRAM_CHAT_ID` - Telegram聊天ID

### 2. Webhook工作流程

```
1. 开发者推送代码到main分支
   ↓
2. GitHub Actions运行测试
   ↓
3. 测试通过后，触发Webhook
   ↓
4. Windows服务器接收Webhook通知
   ↓
5. 自动执行部署脚本
   ↓
6. 拉取最新代码、安装依赖、构建、重启服务
   ↓
7. 发送Telegram通知
```

### 3. Webhook部署脚本

`deployment/webhook-deploy-server.cjs` 会自动执行以下操作：

```powershell
cd C:\trading_dashboard
git pull origin main
pnpm install
pnpm build
pm2 restart all
```

## 手动部署

如果自动部署失败，可以手动执行以下步骤：

```powershell
# 1. 进入项目目录
cd C:\trading_dashboard

# 2. 拉取最新代码
git pull origin main

# 3. 安装依赖（如有更新）
pnpm install

# 4. 推送数据库更改（如有schema更新）
pnpm db:push

# 5. 构建项目
pnpm build

# 6. 重启所有服务
pm2 restart all

# 7. 查看服务状态
pm2 status

# 8. 查看日志（如有错误）
pm2 logs
```

## 监控和维护

### 1. 查看服务状态

```powershell
# PM2状态
pm2 status

# 详细信息
pm2 show trading-dashboard

# 实时日志
pm2 logs

# 特定服务日志
pm2 logs trading-dashboard
pm2 logs webhook-server
pm2 logs trading-bot
```

### 2. 重启服务

```powershell
# 重启所有服务
pm2 restart all

# 重启特定服务
pm2 restart trading-dashboard
pm2 restart webhook-server
pm2 restart trading-bot

# 重新加载（零停机）
pm2 reload trading-dashboard
```

### 3. 停止服务

```powershell
# 停止所有服务
pm2 stop all

# 停止特定服务
pm2 stop trading-dashboard
```

### 4. 查看日志

```powershell
# 应用日志
Get-Content C:\trading_dashboard\logs\app-out.log -Tail 100

# Webhook日志
Get-Content C:\trading_dashboard\logs\webhook-out.log -Tail 100

# 交易机器人日志
Get-Content C:\trading_dashboard\logs\bot-out.log -Tail 100

# Nginx访问日志
Get-Content C:\nginx\logs\cryptoalpha.vip.access.log -Tail 100

# Nginx错误日志
Get-Content C:\nginx\logs\cryptoalpha.vip.error.log -Tail 100
```

### 5. 数据库备份

```powershell
# 导出数据库
# 根据你的数据库类型使用相应的备份命令

# 例如MySQL:
mysqldump -u username -p database_name > backup.sql

# 定期备份（建议每天）
# 可以使用Windows任务计划程序设置自动备份
```

## 故障排查

### 问题1：服务无法启动

```powershell
# 查看PM2日志
pm2 logs trading-dashboard --lines 100

# 常见原因：
# - 端口被占用
# - 环境变量缺失
# - 数据库连接失败
# - 依赖未安装

# 解决方法：
# 1. 检查端口占用
netstat -ano | findstr :3000

# 2. 检查环境变量
Get-Content .env

# 3. 测试数据库连接
# 4. 重新安装依赖
pnpm install
```

### 问题2：Webhook部署失败

```powershell
# 查看webhook服务日志
pm2 logs webhook-server

# 检查webhook服务是否运行
pm2 status

# 如果未运行，启动它
pm2 start ecosystem.config.cjs --only webhook-server

# 测试webhook端点
curl http://localhost:9000

# 检查Nginx转发配置
# 确保 /webhook 路径正确转发到 localhost:9000
```

### 问题3：GitHub Actions部署失败

1. 查看GitHub Actions日志
2. 检查webhook服务是否运行
3. 检查Nginx配置是否正确
4. 检查防火墙规则
5. 检查webhook密钥是否匹配

### 问题4：网站无法访问

```powershell
# 检查Nginx是否运行
Get-Process nginx

# 如果未运行，启动Nginx
Start-Process C:\nginx\nginx.exe

# 检查应用是否运行
pm2 status

# 检查防火墙规则
Get-NetFirewallRule -DisplayName "Allow HTTPS"

# 测试本地访问
curl http://localhost:3000
curl https://cryptoalpha.vip
```

### 问题5：SSL证书过期

```powershell
# 续期Let's Encrypt证书
certbot renew

# 重启Nginx应用新证书
C:\nginx\nginx.exe -s reload
```

## 性能优化

### 1. PM2集群模式

对于高流量应用，可以启用PM2集群模式：

```javascript
// ecosystem.config.cjs
{
  name: "trading-dashboard",
  script: "dist/index.js",
  instances: 4, // 或 "max" 使用所有CPU核心
  exec_mode: "cluster",
}
```

### 2. Nginx缓存

在Nginx配置中启用缓存：

```nginx
proxy_cache_path C:/nginx/cache levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 1h;
    # ...
}
```

### 3. 数据库优化

- 定期清理旧数据
- 添加适当的索引
- 使用连接池

## 安全建议

1. **定期更新**：保持所有软件最新
2. **限制访问**：配置防火墙规则
3. **使用HTTPS**：强制所有流量使用HTTPS
4. **备份数据**：定期备份数据库和配置文件
5. **监控日志**：定期检查异常访问和错误
6. **环境变量**：不要将敏感信息提交到Git

## 回滚

如果部署出现问题，可以回滚到上一个版本：

```powershell
# 查看Git历史
git log --oneline

# 回滚到特定提交
git reset --hard <commit-hash>

# 重新构建和重启
pnpm install
pnpm build
pm2 restart all
```

## 监控面板

应用内置了服务监控面板，可以通过Dashboard页面查看：

- 所有PM2进程状态
- CPU和内存使用情况
- 运行时间和重启次数
- 一键重启服务功能

访问：https://cryptoalpha.vip/ → Dashboard → Service Monitor

## 联系支持

如遇到问题，请：

1. 查看日志文件
2. 检查GitHub Actions日志
3. 查看Nginx错误日志
4. 联系技术支持

## 检查清单

部署完成后，请确认：

- [ ] 所有PM2服务运行正常
- [ ] Nginx正确转发请求
- [ ] 网站可通过HTTPS访问
- [ ] Webhook端点可访问
- [ ] GitHub Actions部署测试成功
- [ ] SSL证书有效
- [ ] 数据库连接正常
- [ ] 日志文件正常写入
- [ ] 防火墙规则配置正确
- [ ] 自动备份已配置

## 相关文档

- [Nginx配置指南](./NGINX_SETUP.md)
- [测试策略文档](../TESTING.md)
- [PM2文档](https://pm2.keymetrics.io/)
- [GitHub Actions文档](https://docs.github.com/en/actions)

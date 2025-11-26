# 🌐 Trading Dashboard 域名部署指南

## 目标域名
**www.cryptoalpha.vip**

---

## 📋 部署方案概述

### 方案1：Manus平台内置发布（推荐）⭐

**优势：**
- ✅ 一键发布，无需手动配置
- ✅ 自动配置SSL证书（HTTPS）
- ✅ 自动CDN加速
- ✅ 自动备份和回滚
- ✅ 无需管理服务器

**步骤：**

#### 第1步：创建检查点
在Manus界面中：
1. 点击右上角蓝色"发布"按钮
2. 或者在管理面板中找到"Checkpoint"或"版本管理"
3. 确认当前版本已保存（版本号：fad8c00e）

#### 第2步：配置自定义域名
1. 在Manus管理界面找到"设置"或"Settings"
2. 找到"域名"或"Domains"选项
3. 点击"添加自定义域名"或"Add Custom Domain"
4. 输入：`www.cryptoalpha.vip`
5. 系统会提供一个CNAME记录值（类似：`xxx.manus.space`）

#### 第3步：配置DNS
在您的域名DNS管理面板（如Cloudflare、阿里云、腾讯云等）：

```
类型: CNAME
主机记录: www
记录值: [Manus提供的CNAME值]
TTL: 600（或默认）
```

#### 第4步：等待生效
- DNS传播时间：5-30分钟
- SSL证书自动配置：10-20分钟
- 完成后访问：https://www.cryptoalpha.vip

---

### 方案2：自主服务器部署

如果您有自己的Windows/Linux服务器，可以完全自主部署。

#### 前置要求

**服务器要求：**
- Windows Server 2016+ 或 Ubuntu 20.04+
- 至少2GB RAM
- 公网IP地址
- 开放端口：80（HTTP）和443（HTTPS）

**软件要求：**
- Node.js 18+
- MySQL 8.0+
- Python 3.11+
- Nginx（推荐）或 IIS
- PM2（进程管理）

#### 部署步骤

##### 1. 准备服务器

**Windows Server：**
```powershell
# 安装Nginx
# 下载：http://nginx.org/en/download.html
# 解压到：C:\nginx

# 或使用Chocolatey安装
choco install nginx
```

**Linux Server：**
```bash
# 安装Nginx
sudo apt update
sudo apt install nginx

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# 安装MySQL
sudo apt install mysql-server

# 安装Python
sudo apt install python3.11 python3-pip
```

##### 2. 上传项目文件

将完整的项目文件上传到服务器：
```
/var/www/trading_dashboard/  (Linux)
C:\inetpub\trading_dashboard\  (Windows)
```

##### 3. 安装依赖

```bash
# 进入项目目录
cd /var/www/trading_dashboard

# 安装Node.js依赖
npm install -g pnpm
pnpm install

# 安装Python依赖
cd scripts
pip3 install -r requirements.txt
```

##### 4. 配置环境变量

编辑 `.env` 文件，确保包含：
```env
# Database
DATABASE_URL="mysql://trading:trading123@localhost:3306/trading_dashboard"

# KuCoin API
KUCOIN_API_KEY="your_api_key"
KUCOIN_API_SECRET="your_api_secret"
KUCOIN_API_PASSPHRASE="your_passphrase"

# Telegram
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"

# Server
PORT="3000"
NODE_ENV="production"

# Trading Mode
TRADING_MODE="paper"  # or "live"
```

##### 5. 初始化数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE IF NOT EXISTS trading_dashboard;
CREATE USER IF NOT EXISTS 'trading'@'localhost' IDENTIFIED BY 'trading123';
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
exit;

# 运行数据库迁移
cd /var/www/trading_dashboard
pnpm db:push
```

##### 6. 构建前端

```bash
cd /var/www/trading_dashboard
pnpm run build
```

##### 7. 配置Nginx反向代理

**创建Nginx配置文件：**

**Linux:** `/etc/nginx/sites-available/trading_dashboard`
**Windows:** `C:\nginx\conf\trading_dashboard.conf`

```nginx
# HTTP配置（自动重定向到HTTPS）
server {
    listen 80;
    server_name www.cryptoalpha.vip cryptoalpha.vip;
    
    # 重定向到HTTPS
    return 301 https://www.cryptoalpha.vip$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name www.cryptoalpha.vip;
    
    # SSL证书配置（需要先获取证书）
    ssl_certificate /etc/ssl/certs/cryptoalpha.vip.crt;
    ssl_certificate_key /etc/ssl/private/cryptoalpha.vip.key;
    
    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 日志配置
    access_log /var/log/nginx/trading_dashboard_access.log;
    error_log /var/log/nginx/trading_dashboard_error.log;
    
    # 反向代理到Node.js应用
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        
        # WebSocket支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # 转发真实IP
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        proxy_pass http://localhost:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**启用配置（Linux）：**
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/trading_dashboard /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

**启用配置（Windows）：**
```powershell
# 编辑 C:\nginx\conf\nginx.conf
# 在http块中添加：
include trading_dashboard.conf;

# 重启Nginx
cd C:\nginx
nginx -s reload
```

##### 8. 获取SSL证书

**方法A：使用Let's Encrypt（免费，推荐）**

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 自动获取并配置证书
sudo certbot --nginx -d www.cryptoalpha.vip -d cryptoalpha.vip

# 自动续期
sudo certbot renew --dry-run
```

**方法B：使用付费证书**
- 从阿里云、腾讯云等购买SSL证书
- 下载证书文件（.crt和.key）
- 上传到服务器并配置Nginx

##### 9. 配置DNS

在域名DNS管理面板：

```
类型: A
主机记录: www
记录值: [您的服务器公网IP]
TTL: 600

类型: A
主机记录: @
记录值: [您的服务器公网IP]
TTL: 600
```

##### 10. 启动服务

```bash
# 使用PM2启动所有服务
cd /var/www/trading_dashboard
pm2 start ecosystem.config.cjs

# 保存PM2配置
pm2 save

# 设置开机自启
pm2 startup
```

##### 11. 配置防火墙

**Linux (UFW):**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**Windows Firewall:**
```powershell
# 允许HTTP
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# 允许HTTPS
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

##### 12. 测试访问

```bash
# 测试HTTP（应该重定向到HTTPS）
curl -I http://www.cryptoalpha.vip

# 测试HTTPS
curl -I https://www.cryptoalpha.vip

# 测试WebSocket
curl -I https://www.cryptoalpha.vip/socket.io/
```

---

## 🔍 验证部署

### 1. 检查服务状态
```bash
pm2 list
```

应该看到所有5个服务都是 `online`：
- trading-dashboard
- trading-bot
- telegram-bot
- websocket-server
- daily-report

### 2. 检查日志
```bash
pm2 logs
```

### 3. 访问Dashboard
```
https://www.cryptoalpha.vip
```

应该看到：
- ✅ 登录页面或Dashboard主页
- ✅ HTTPS绿色锁图标
- ✅ 所有数据正常加载
- ✅ WebSocket实时连接正常

---

## 🔧 故障排查

### 问题1：域名无法访问

**检查DNS：**
```bash
nslookup www.cryptoalpha.vip
dig www.cryptoalpha.vip
```

**检查Nginx：**
```bash
sudo nginx -t
sudo systemctl status nginx
```

### 问题2：SSL证书错误

**检查证书：**
```bash
sudo certbot certificates
openssl x509 -in /etc/ssl/certs/cryptoalpha.vip.crt -text -noout
```

### 问题3：WebSocket连接失败

**检查Nginx配置：**
确保包含WebSocket支持：
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection 'upgrade';
```

### 问题4：502 Bad Gateway

**检查Node.js服务：**
```bash
pm2 status
pm2 logs trading-dashboard
```

**检查端口占用：**
```bash
netstat -tulpn | grep 3000
```

---

## 📊 性能优化

### 1. 启用Gzip压缩

在Nginx配置中添加：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### 2. 配置缓存

```nginx
# 静态文件缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 限制请求速率

```nginx
# 在http块中
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# 在location块中
limit_req zone=api burst=20 nodelay;
```

---

## 🔒 安全加固

### 1. 隐藏Nginx版本
```nginx
server_tokens off;
```

### 2. 添加安全头
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### 3. 限制上传大小
```nginx
client_max_body_size 10M;
```

### 4. 配置fail2ban
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## 📝 维护建议

### 日常维护
```bash
# 查看服务状态
pm2 status

# 查看日志
pm2 logs

# 重启服务
pm2 restart all

# 更新代码后
cd /var/www/trading_dashboard
git pull
pnpm install
pnpm run build
pm2 restart trading-dashboard
```

### 备份策略
```bash
# 备份数据库
mysqldump -u trading -p trading_dashboard > backup_$(date +%Y%m%d).sql

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env ecosystem.config.cjs
```

### 监控
- 设置服务器监控（CPU、内存、磁盘）
- 配置日志轮转
- 设置告警通知

---

## 📞 需要的信息

如果选择方案2（自主部署），请提供：

1. **服务器信息：**
   - 公网IP地址
   - 操作系统类型和版本
   - 已安装的软件

2. **域名配置：**
   - DNS服务商（Cloudflare/阿里云/腾讯云等）
   - 是否有管理权限

3. **SSL证书：**
   - 是否需要HTTPS
   - 是否已有证书

4. **其他：**
   - 是否需要CDN加速
   - 是否需要负载均衡

---

## 🎯 推荐方案

**如果您使用Manus平台：**
→ **方案1**（一键发布，最简单）

**如果您有自己的服务器：**
→ **方案2**（完全自主控制）

---

**请告诉我您选择哪个方案，我会提供详细的操作步骤！** 🚀

# Windows云服务器部署指南

## 目录

1. [服务器准备](#%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%87%86%E5%A4%87)

1. [环境配置](#%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE)

1. [数据库安装](#%E6%95%B0%E6%8D%AE%E5%BA%93%E5%AE%89%E8%A3%85)

1. [项目部署](#%E9%A1%B9%E7%9B%AE%E9%83%A8%E7%BD%B2)

1. [后台运行配置](#%E5%90%8E%E5%8F%B0%E8%BF%90%E8%A1%8C%E9%85%8D%E7%BD%AE)

1. [域名和SSL配置](#%E5%9F%9F%E5%90%8D%E5%92%8Cssl%E9%85%8D%E7%BD%AE)

1. [监控和维护](#%E7%9B%91%E6%8E%A7%E5%92%8C%E7%BB%B4%E6%8A%A4)

1. [常见问题](#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)

---

## 服务器准备

### 1.1 云服务器购买建议

**推荐配置：**

- **CPU**: 2核或以上

- **内存**: 4GB或以上

- **硬盘**: 40GB SSD或以上

- **带宽**: 5Mbps或以上

- **操作系统**: Windows Server 2019/2022

**推荐云服务商：**

- 阿里云 (国内)

- 腾讯云 (国内)

- AWS (国际)

- Azure (国际)

### 1.2 初始化服务器

1. **登录云服务器控制台**
  - 进入云服务商管理后台
  - 找到"实例"或"云服务器"
  - 点击"远程连接"或"VNC连接"

1. **设置管理员密码**

1. **使用远程桌面连接**
  - Windows本地：按 `Win + R`，输入 `mstsc`
  - Mac：下载 Microsoft Remote Desktop
  - 输入服务器公网IP
  - 用户名：`Administrator`
  - 密码：刚才设置的密码

### 1.3 配置防火墙规则

在云服务商控制台配置安全组：

| 规则 | 协议 | 端口 | 源地址 | 说明 |
| --- | --- | --- | --- | --- |
| 入站 | TCP | 3389 | 0.0.0.0/0 | 远程桌面 |
| 入站 | TCP | 80 | 0.0.0.0/0 | HTTP |
| 入站 | TCP | 443 | 0.0.0.0/0 | HTTPS |
| 入站 | TCP | 3000 | 0.0.0.0/0 | 应用端口（可选） |
| 入站 | TCP | 3306 | 127.0.0.1/32 | MySQL（仅本地） |

---

## 环境配置

### 2.1 安装Node.js

1. **下载Node.js**
  - 打开浏览器访问：[https://nodejs.org/](https://nodejs.org/)
  - 下载 LTS 版本（推荐 v20.x ）
  - 选择 Windows Installer (.msi) 64-bit

1. **安装Node.js**

1. **验证安装**
  - 打开 PowerShell（管理员模式）
  - 运行以下命令：

1. **配置npm镜像（可选，加速下载）**

### 2.2 安装Python

1. **下载Python**
  - 访问：[https://www.python.org/downloads/](https://www.python.org/downloads/)
  - 下载 Python 3.11.x Windows installer (64-bit )

1. **安装Python**

1. **验证安装**

1. **安装Python依赖**

### 2.3 安装Git

1. **下载Git**
  - 访问：[https://git-scm.com/download/win](https://git-scm.com/download/win)
  - 下载 64-bit Git for Windows Setup

1. **安装Git**

1. **验证安装**

---

## 数据库安装

### 3.1 安装MySQL

1. **下载MySQL**
  - 访问：[https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
  - 下载 MySQL Installer for Windows
  - 选择 "mysql-installer-community-8.0.x.msi"

1. **安装MySQL**

1. **验证MySQL安装**

### 3.2 创建数据库和用户

```
# 登录MySQL
mysql -u root -p

# 在MySQL命令行中执行：
```

```sql
-- 创建数据库
CREATE DATABASE trading_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（替换为你自己的密码）
CREATE USER 'trading_user'@'localhost' IDENTIFIED BY 'TradingUser@2024!';

-- 授权
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证
SHOW DATABASES;
SELECT user, host FROM mysql.user;

-- 退出
EXIT;
```

### 3.3 测试数据库连接

```
# 使用新创建的用户登录
mysql -u trading_user -p trading_dashboard

# 成功登录说明配置正确
```

---

## 项目部署

### 4.1 上传项目文件

**方法一：使用Git（推荐）**

```
# 创建项目目录
cd C:\
mkdir Projects
cd Projects

# 如果项目在GitHub/GitLab
git clone https://your-repository-url.git trading_dashboard
cd trading_dashboard

# 如果没有Git仓库 ，跳到方法二
```

**方法二：手动上传**

1. 在本地电脑上压缩项目文件夹为 `trading_dashboard.zip`

1. 使用远程桌面的"本地资源"功能：

1. 在服务器上，打开"此电脑"，可以看到本地磁盘

1. 将 `trading_dashboard.zip` 复制到 `C:\Projects\`

1. 右键解压到 `C:\Projects\trading_dashboard\`

**方法三：使用FTP工具**

1. 下载 FileZilla Client：[https://filezilla-project.org/](https://filezilla-project.org/)

1. 在服务器上安装 FileZilla Server

1. 配置FTP服务器

1. 使用FileZilla Client上传文件

### 4.2 配置环境变量

1. **创建 .env 文件**

```
cd C:\Projects\trading_dashboard
notepad .env
```

1. **填写配置内容**

```
# 数据库配置
DATABASE_URL=mysql://trading_user:TradingUser@2024!@localhost:3306/trading_dashboard

# JWT密钥（生成随机字符串 ）
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Telegram配置（可选）
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# 应用配置
VITE_APP_TITLE=10U战神滚仓策略
NODE_ENV=production
PORT=3000

# KuCoin API（如果使用实盘交易）
KUCOIN_API_KEY=your_kucoin_api_key
KUCOIN_API_SECRET=your_kucoin_api_secret
KUCOIN_API_PASSPHRASE=your_kucoin_api_passphrase
```

1. **保存并关闭**
  - 按 `Ctrl + S` 保存
  - 关闭记事本

### 4.3 安装项目依赖

```
cd C:\Projects\trading_dashboard

# 安装Node.js依赖
npm install -g pnpm
pnpm install

# 如果遇到网络问题，使用国内镜像
pnpm config set registry https://registry.npmmirror.com
pnpm install
```

### 4.4 初始化数据库

```
# 推送数据库Schema
pnpm db:push

# 如果需要运行种子数据
pnpm db:seed
```

### 4.5 构建前端

```
# 构建生产版本
pnpm build

# 构建完成后 ，会在 dist 目录生成静态文件
```

### 4.6 测试运行

```
# 启动服务器
pnpm start

# 如果看到：
# Server running on http://localhost:3000/
# 说明启动成功
```

打开浏览器访问：`http://localhost:3000`

如果能看到Dashboard ，说明部署成功！

---

## 后台运行配置

### 5.1 使用PM2管理进程

1. **安装PM2**

```
npm install -g pm2
```

1. **创建PM2配置文件**

```
cd C:\Projects\trading_dashboard
notepad ecosystem.config.js
```

1. **填写配置**

```javascript
module.exports = {
  apps: [
    {
      name: 'trading-dashboard',
      script: 'server/index.js',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: 'logs/err.log',
      out_file: 'logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
```

1. **启动应用**

```
# 创建日志目录
mkdir logs

# 启动应用
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs

# 停止应用
pm2 stop trading-dashboard

# 重启应用
pm2 restart trading-dashboard

# 删除应用
pm2 delete trading-dashboard
```

### 5.2 配置PM2开机自启

```
# 生成启动脚本
pm2 startup

# 保存当前PM2进程列表
pm2 save

# 现在，即使服务器重启，应用也会自动启动
```

### 5.3 使用Windows服务（替代方案）

如果PM2在Windows上不稳定，可以使用NSSM：

1. **下载NSSM**
  - 访问：[https://nssm.cc/download](https://nssm.cc/download)
  - 下载 nssm-2.24.zip
  - 解压到 `C:\nssm\`

1. **安装服务**

```
# 打开PowerShell（管理员模式 ）
cd C:\nssm\win64

# 安装服务
.\nssm.exe install TradingDashboard

# 在弹出的窗口中配置：
# Path: C:\Program Files\nodejs\node.exe
# Startup directory: C:\Projects\trading_dashboard
# Arguments: server/index.js

# 点击 "Install service"
```

1. **启动服务**

```
# 启动服务
.\nssm.exe start TradingDashboard

# 查看状态
.\nssm.exe status TradingDashboard

# 停止服务
.\nssm.exe stop TradingDashboard

# 删除服务
.\nssm.exe remove TradingDashboard confirm
```

---

## 域名和SSL配置

### 6.1 配置反向代理（使用Nginx）

1. **下载Nginx for Windows**
  - 访问：[http://nginx.org/en/download.html](http://nginx.org/en/download.html)
  - 下载 nginx/Windows-x.x.x
  - 解压到 `C:\nginx\`

1. **配置Nginx**

```
cd C:\nginx
notepad conf\nginx.conf
```

1. **修改配置文件**

```
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;

    # HTTP服务器
    server {
        listen       80;
        server_name  your-domain.com;  # 替换为你的域名

        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    # HTTPS服务器
    server {
        listen       443 ssl;
        server_name  your-domain.com;  # 替换为你的域名

        # SSL证书路径（稍后配置 ）
        ssl_certificate      C:/nginx/ssl/cert.pem;
        ssl_certificate_key  C:/nginx/ssl/key.pem;

        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;
        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers  on;

        location / {
            proxy_pass http://localhost:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 6.2 申请SSL证书

**方法一：使用Let's Encrypt（免费 ）**

1. 下载 win-acme：[https://www.win-acme.com/](https://www.win-acme.com/)

1. 解压到 `C:\win-acme\`

1. 运行 `wacs.exe`

1. 按照提示申请证书

**方法二：使用云服务商提供的免费证书**

1. 登录云服务商控制台

1. 找到"SSL证书"服务

1. 申请免费证书（通常1年有效期 ）

1. 下载证书文件（Nginx格式）

1. 上传到服务器 `C:\nginx\ssl\`

### 6.3 启动Nginx

```
# 测试配置
cd C:\nginx
.\nginx.exe -t

# 启动Nginx
.\nginx.exe

# 重新加载配置
.\nginx.exe -s reload

# 停止Nginx
.\nginx.exe -s stop
```

### 6.4 配置Nginx为Windows服务

```
# 使用NSSM安装Nginx服务
cd C:\nssm\win64
.\nssm.exe install Nginx C:\nginx\nginx.exe

# 启动服务
.\nssm.exe start Nginx
```

---

## 监控和维护

### 7.1 日志管理

**应用日志位置：**

```
C:\Projects\trading_dashboard\logs\
├── err.log      # 错误日志
├── out.log      # 输出日志
└── combined.log # 综合日志
```

**查看日志：**

```
# 实时查看日志
pm2 logs trading-dashboard

# 查看最近100行
pm2 logs trading-dashboard --lines 100

# 清空日志
pm2 flush
```

**Nginx日志位置：**

```
C:\nginx\logs\
├── access.log   # 访问日志
└── error.log    # 错误日志
```

### 7.2 性能监控

**使用PM2监控：**

```
# 查看实时监控
pm2 monit

# 查看详细信息
pm2 show trading-dashboard
```

**Windows性能监视器：**

1. 按 `Win + R`，输入 `perfmon`

1. 添加监控指标：
  - CPU使用率
  - 内存使用率
  - 磁盘IO
  - 网络流量

### 7.3 定期备份

**创建备份脚本：**

```
# 创建备份脚本
notepad C:\Scripts\backup.ps1
```

```
# backup.ps1 内容
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups\$date"

# 创建备份目录
New-Item -ItemType Directory -Path $backupDir

# 备份数据库
mysqldump -u trading_user -p trading_dashboard > "$backupDir\database.sql"

# 备份项目文件
Copy-Item -Path "C:\Projects\trading_dashboard" -Destination "$backupDir\project" -Recurse

# 压缩备份
Compress-Archive -Path $backupDir -DestinationPath "C:\Backups\backup_$date.zip"

# 删除临时目录
Remove-Item -Path $backupDir -Recurse

# 删除30天前的备份
Get-ChildItem "C:\Backups" -Filter "backup_*.zip" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
    Remove-Item
```

**设置定时任务：**

1. 打开"任务计划程序"

1. 创建基本任务

1. 触发器：每天凌晨2点

1. 操作：启动程序 `powershell.exe`

1. 参数：`-File C:\Scripts\backup.ps1`

### 7.4 更新部署

```
# 1. 停止应用
pm2 stop trading-dashboard

# 2. 备份当前版本
cd C:\Projects
Copy-Item -Path trading_dashboard -Destination "trading_dashboard_backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse

# 3. 拉取最新代码（如果使用Git）
cd trading_dashboard
git pull origin main

# 4. 安装新依赖
pnpm install

# 5. 推送数据库变更
pnpm db:push

# 6. 重新构建
pnpm build

# 7. 重启应用
pm2 restart trading-dashboard

# 8. 查看日志确认
pm2 logs trading-dashboard --lines 50
```

---

## 常见问题

### 8.1 端口被占用

**问题：** `Error: listen EADDRINUSE: address already in use :::3000`

**解决方案：**

```
# 查找占用端口的进程
netstat -ano | findstr :3000

# 记下PID，然后结束进程
taskkill /PID <PID> /F

# 或者修改应用端口
# 编辑 .env 文件，修改 PORT=3001
```

### 8.2 数据库连接失败

**问题：** `Error: ER_ACCESS_DENIED_ERROR: Access denied for user`

**解决方案：**

```
# 1. 检查MySQL服务是否运行
Get-Service MySQL80

# 2. 如果未运行，启动服务
Start-Service MySQL80

# 3. 检查用户权限
mysql -u root -p
```

```sql
-- 查看用户
SELECT user, host FROM mysql.user;

-- 重新授权
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading_user'@'localhost';
FLUSH PRIVILEGES;
```

### 8.3 内存不足

**问题：** 应用频繁崩溃，日志显示内存错误

**解决方案：**

```
# 1. 增加Node.js内存限制
# 修改 ecosystem.config.js
max_memory_restart: '2G'  # 改为2GB

# 2. 重启应用
pm2 restart trading-dashboard

# 3. 如果仍然不够，考虑升级服务器配置
```

### 8.4 防火墙阻止访问

**问题：** 外网无法访问应用

**解决方案：**

```
# 1. 检查Windows防火墙
# 打开"Windows Defender 防火墙"
# 点击"高级设置"
# 添加入站规则：
#   - 规则类型：端口
#   - 协议：TCP
#   - 端口：3000, 80, 443
#   - 操作：允许连接

# 2. 检查云服务商安全组
# 在云服务商控制台确认已开放相应端口
```

### 8.5 SSL证书过期

**问题：** 浏览器显示证书过期警告

**解决方案：**

```
# 1. 重新申请证书
# 使用win-acme或云服务商控制台

# 2. 替换证书文件
# 上传新证书到 C:\nginx\ssl\

# 3. 重新加载Nginx
cd C:\nginx
.\nginx.exe -s reload
```

### 8.6 Python脚本无法运行

**问题：** 交易脚本报错 `ModuleNotFoundError`

**解决方案：**

```
# 1. 检查Python版本
python --version

# 2. 重新安装依赖
pip install -r requirements.txt

# 3. 如果某个包安装失败，单独安装
pip install package-name --upgrade

# 4. 检查Python路径
where python
# 确保使用正确的Python版本
```

---

## 附录

### A. 快速命令参考

```
# 服务管理
pm2 start ecosystem.config.js    # 启动应用
pm2 stop trading-dashboard        # 停止应用
pm2 restart trading-dashboard     # 重启应用
pm2 logs trading-dashboard        # 查看日志
pm2 monit                         # 监控面板

# 数据库
mysql -u trading_user -p          # 登录数据库
mysqldump -u root -p trading_dashboard > backup.sql  # 备份
mysql -u root -p trading_dashboard < backup.sql      # 恢复

# Nginx
cd C:\nginx
.\nginx.exe                       # 启动
.\nginx.exe -s reload             # 重载配置
.\nginx.exe -s stop               # 停止

# 项目
pnpm install                      # 安装依赖
pnpm build                        # 构建
pnpm db:push                      # 推送数据库
pnpm test                         # 运行测试
```

### B. 推荐工具

- **远程桌面**: Microsoft Remote Desktop

- **FTP工具**: FileZilla

- **文本编辑器**: Notepad++, VS Code

- **数据库管理**: MySQL Workbench, HeidiSQL

- **进程管理**: PM2, NSSM

- **监控工具**: Windows Performance Monitor

### C. 安全建议

1. **定期更新系统**
  - 启用Windows Update自动更新
  - 定期检查安全补丁

1. **强密码策略**
  - 数据库密码：至少16位
  - 管理员密码：定期更换
  - API密钥：使用环境变量，不要硬编码

1. **最小权限原则**
  - 不要使用root/Administrator运行应用
  - 创建专用用户运行服务

1. **备份策略**
  - 每日自动备份数据库
  - 每周备份完整项目
  - 异地备份重要数据

1. **监控告警**
  - 配置磁盘空间告警
  - 配置CPU/内存使用告警
  - 配置应用崩溃告警

---

## 总结

完成以上步骤后，您的交易监控系统应该已经成功部署在Windows云服务器上了！

**部署检查清单：**

- [ ] 服务器配置完成

- [ ] Node.js和Python环境安装

- [ ] MySQL数据库配置

- [ ] 项目文件上传

- [ ] 环境变量配置

- [ ] 数据库初始化

- [ ] 应用成功启动

- [ ] PM2/NSSM配置开机自启

- [ ] Nginx反向代理配置

- [ ] SSL证书安装

- [ ] 防火墙规则配置

- [ ] 备份脚本配置

- [ ] 监控告警配置

**遇到问题？**

1. 查看应用日志：`pm2 logs`

1. 查看Nginx日志：`C:\nginx\logs\error.log`

1. 检查Windows事件查看器

1. 参考本文档"常见问题"章节

祝您部署顺利！🎉


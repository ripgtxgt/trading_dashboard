# Nginx 安装和配置指南

## Windows Server 上安装 Nginx

### 方法1：使用Chocolatey（推荐）

```powershell
# 以管理员身份运行PowerShell
choco install nginx -y
```

### 方法2：手动下载安装

1. 访问 http://nginx.org/en/download.html
2. 下载最新稳定版（Windows版本）
3. 解压到 `C:\nginx`
4. 配置环境变量（可选）

## 配置 Nginx

### 1. 修改主配置文件

编辑 `C:\nginx\conf\nginx.conf`，在http块末尾添加：

```nginx
http {
    # ... 其他配置 ...
    
    # 包含sites-enabled目录下的所有配置
    include sites-enabled/*.conf;
}
```

### 2. 创建sites-enabled目录

```powershell
New-Item -ItemType Directory -Force -Path "C:\nginx\conf\sites-enabled"
```

### 3. 部署脚本会自动复制配置

`deploy-auto.ps1` 脚本会自动：
- 复制 `nginx.conf` 到 `C:\nginx\conf\sites-enabled\cryptoalpha.vip.conf`
- 测试配置是否正确
- 重启Nginx服务

## 配置域名解析

### 1. 添加DNS记录

在您的域名DNS管理面板添加A记录：

```
类型: A
主机记录: @
记录值: 13.113.194.218
TTL: 600
```

如果需要www子域名：

```
类型: A
主机记录: www
记录值: 13.113.194.218
TTL: 600
```

### 2. 配置SSL证书（可选但推荐）

#### 使用Let's Encrypt（免费）

Windows上可以使用 [win-acme](https://www.win-acme.com/)：

```powershell
# 下载win-acme
Invoke-WebRequest -Uri "https://github.com/win-acme/win-acme/releases/download/v2.2.7/win-acme.v2.2.7.1612.x64.pluggable.zip" -OutFile "win-acme.zip"

# 解压
Expand-Archive -Path "win-acme.zip" -DestinationPath "C:\win-acme"

# 运行win-acme
cd C:\win-acme
.\wacs.exe
```

按照提示选择：
1. N: Create certificate (full options)
2. 2: Manual input
3. 输入域名：`cryptoalpha.vip,www.cryptoalpha.vip`
4. 选择验证方式（推荐HTTP验证）
5. 选择Nginx作为目标

#### 手动配置SSL证书

如果您已有SSL证书，修改 `nginx.conf` 中的SSL配置：

```nginx
ssl_certificate C:/path/to/cert.pem;
ssl_certificate_key C:/path/to/key.pem;
```

## 启动和管理 Nginx

### 启动Nginx

```powershell
# 方法1：直接启动
cd C:\nginx
start nginx

# 方法2：使用NSSM创建Windows服务（推荐）
choco install nssm -y
nssm install nginx "C:\nginx\nginx.exe"
nssm start nginx
```

### 常用命令

```powershell
# 测试配置
nginx -t

# 重新加载配置
nginx -s reload

# 停止Nginx
nginx -s stop

# 快速停止
nginx -s quit
```

### 检查Nginx状态

```powershell
# 检查进程
Get-Process nginx

# 检查端口
netstat -ano | findstr :80
netstat -ano | findstr :443
```

## 防火墙配置

确保Windows防火墙允许HTTP和HTTPS流量：

```powershell
# 允许HTTP (80端口)
New-NetFirewallRule -DisplayName "Nginx HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 允许HTTPS (443端口)
New-NetFirewallRule -DisplayName "Nginx HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

## 验证部署

### 1. 本地测试

```powershell
# 测试HTTP
curl http://localhost

# 测试HTTPS（如果已配置SSL）
curl https://localhost
```

### 2. 远程测试

在浏览器中访问：
- http://cryptoalpha.vip
- https://cryptoalpha.vip（如果已配置SSL）

## 故障排查

### 问题1：Nginx无法启动

```powershell
# 查看错误日志
Get-Content C:\nginx\logs\error.log -Tail 50
```

### 问题2：502 Bad Gateway

检查Node.js应用是否在3000端口运行：

```powershell
pm2 list
netstat -ano | findstr :3000
```

### 问题3：域名无法访问

1. 检查DNS解析：`nslookup cryptoalpha.vip`
2. 检查防火墙规则
3. 检查Nginx配置：`nginx -t`
4. 查看Nginx日志：`Get-Content C:\nginx\logs\access.log -Tail 50`

## 自动部署流程

完整的自动部署流程：

1. **代码推送** → GitHub
2. **GitHub Actions** → SSH连接到Windows服务器
3. **deploy-auto.ps1** 自动执行：
   - ✅ 拉取最新代码
   - ✅ 安装依赖（pnpm install）
   - ✅ 构建项目（pnpm build）
   - ✅ 数据库迁移（pnpm drizzle-kit push）
   - ✅ 重启PM2服务
   - ✅ 更新Nginx配置
   - ✅ 重启Nginx
4. **Telegram通知** → 部署结果

## 注意事项

1. **首次部署**需要手动安装Nginx和配置SSL证书
2. **后续部署**会自动更新Nginx配置并重启
3. **SSL证书**需要定期续期（Let's Encrypt每90天）
4. **域名解析**生效可能需要几分钟到几小时

## 推荐配置

为了获得最佳性能和安全性，建议：

1. ✅ 使用HTTPS（配置SSL证书）
2. ✅ 启用Gzip压缩（已在nginx.conf中配置）
3. ✅ 配置静态文件缓存（已在nginx.conf中配置）
4. ✅ 设置合理的超时时间（已在nginx.conf中配置）
5. ✅ 启用HTTP/2（已在nginx.conf中配置）
6. ✅ 配置CORS代理（KuCoin API已配置）

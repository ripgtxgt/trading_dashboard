# Nginx配置部署指南

本指南说明如何在Windows Server上配置Nginx以支持GitHub自动部署和HTTPS访问。

## 前置条件

- Windows Server 2022
- Nginx已安装（推荐版本：1.24+）
- SSL证书已获取（Let's Encrypt或其他CA）
- 域名已解析到服务器IP（cryptoalpha.vip → 13.113.194.218）

## 配置步骤

### 1. 备份现有配置

```powershell
# 备份当前Nginx配置
Copy-Item C:\nginx\conf\nginx.conf C:\nginx\conf\nginx.conf.backup
```

### 2. 部署新配置

```powershell
# 复制新配置文件
Copy-Item .\deployment\nginx.conf C:\nginx\conf\nginx.conf

# 或者手动编辑 C:\nginx\conf\nginx.conf
# 将 deployment/nginx.conf 的内容复制进去
```

### 3. 配置SSL证书

**方法1：使用Let's Encrypt（推荐）**

```powershell
# 安装Certbot for Windows
# 下载地址: https://certbot.eff.org/instructions?ws=nginx&os=windows

# 申请证书
certbot certonly --standalone -d cryptoalpha.vip -d www.cryptoalpha.vip

# 证书将保存在: C:\Certbot\live\cryptoalpha.vip\
```

**方法2：使用现有证书**

将证书文件放置在以下位置：
- 证书文件：`C:\nginx\ssl\cryptoalpha.vip\fullchain.pem`
- 私钥文件：`C:\nginx\ssl\cryptoalpha.vip\privkey.pem`

### 4. 更新配置中的证书路径

编辑 `C:\nginx\conf\nginx.conf`，修改SSL证书路径：

```nginx
ssl_certificate C:/nginx/ssl/cryptoalpha.vip/fullchain.pem;
ssl_certificate_key C:/nginx/ssl/cryptoalpha.vip/privkey.pem;
```

如果使用Let's Encrypt，路径应为：

```nginx
ssl_certificate C:/Certbot/live/cryptoalpha.vip/fullchain.pem;
ssl_certificate_key C:/Certbot/live/cryptoalpha.vip/privkey.pem;
```

### 5. 创建日志目录

```powershell
# 创建日志目录
New-Item -ItemType Directory -Force -Path C:\nginx\logs
```

### 6. 测试配置

```powershell
# 测试Nginx配置是否正确
C:\nginx\nginx.exe -t

# 应该看到：
# nginx: the configuration file C:\nginx/conf/nginx.conf syntax is ok
# nginx: configuration file C:\nginx/conf/nginx.conf test is successful
```

### 7. 重启Nginx

```powershell
# 停止Nginx
C:\nginx\nginx.exe -s stop

# 启动Nginx
Start-Process C:\nginx\nginx.exe

# 或者使用PM2管理（如果已配置）
pm2 restart nginx
```

### 8. 配置防火墙

```powershell
# 开放HTTP端口（80）
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 开放HTTPS端口（443）
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 注意：不需要开放9000端口，webhook服务只在内部访问
```

### 9. 验证配置

**测试Webhook端点：**

```powershell
# 从本地测试
curl http://localhost:9000

# 从外部测试（需要webhook服务运行）
curl https://cryptoalpha.vip/webhook
```

**测试网站访问：**

```powershell
# 测试HTTP重定向到HTTPS
curl -I http://cryptoalpha.vip

# 测试HTTPS访问
curl -I https://cryptoalpha.vip
```

**测试GitHub Webhook：**

1. 访问 GitHub仓库 → Settings → Webhooks
2. 点击已配置的webhook
3. 点击 "Recent Deliveries"
4. 选择一个delivery，点击 "Redeliver"
5. 检查Response是否为200 OK

## 配置说明

### Webhook转发

```nginx
location /webhook {
    proxy_pass http://localhost:9000;
    # ...
}
```

- GitHub Actions推送到 `https://cryptoalpha.vip/webhook`
- Nginx转发到本地webhook服务 `http://localhost:9000`
- Webhook服务接收后自动执行部署脚本

### API和WebSocket

```nginx
location /api/ {
    proxy_pass http://localhost:3000;
    # ...
}

location /socket.io/ {
    proxy_pass http://localhost:3000;
    # WebSocket支持
}
```

- 所有API请求转发到Node.js服务（端口3000）
- WebSocket连接保持长连接（7天超时）

### 前端应用

```nginx
location / {
    proxy_pass http://localhost:3000;
    # ...
}
```

- 所有其他请求转发到Vite开发服务器或构建后的应用

## 故障排查

### 问题1：Nginx无法启动

```powershell
# 查看错误日志
Get-Content C:\nginx\logs\error.log -Tail 50

# 常见原因：
# - 端口80/443被占用
# - 配置文件语法错误
# - SSL证书路径错误
```

### 问题2：Webhook返回502 Bad Gateway

```powershell
# 检查webhook服务是否运行
pm2 status

# 如果webhook-server未运行，启动它
pm2 start ecosystem.config.cjs --only webhook-server

# 查看webhook服务日志
pm2 logs webhook-server
```

### 问题3：SSL证书错误

```powershell
# 检查证书文件是否存在
Test-Path C:\nginx\ssl\cryptoalpha.vip\fullchain.pem
Test-Path C:\nginx\ssl\cryptoalpha.vip\privkey.pem

# 检查证书有效期
# 使用浏览器访问 https://cryptoalpha.vip 查看证书详情
```

### 问题4：GitHub Webhook超时

```powershell
# 增加Nginx超时设置
# 在 location /webhook 块中添加：
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

## 自动续期SSL证书（Let's Encrypt）

Let's Encrypt证书有效期90天，需要定期续期。

### 创建续期任务

1. 打开"任务计划程序"（Task Scheduler）
2. 创建基本任务
   - 名称：Renew SSL Certificate
   - 触发器：每月
   - 操作：启动程序
   - 程序：`C:\Program Files\Certbot\certbot.exe`
   - 参数：`renew --quiet`
3. 保存任务

### 手动续期

```powershell
# 续期证书
certbot renew

# 重启Nginx应用新证书
C:\nginx\nginx.exe -s reload
```

## 监控和日志

### 访问日志

```powershell
# 查看访问日志
Get-Content C:\nginx\logs\cryptoalpha.vip.access.log -Tail 100

# 实时监控访问日志
Get-Content C:\nginx\logs\cryptoalpha.vip.access.log -Wait
```

### 错误日志

```powershell
# 查看错误日志
Get-Content C:\nginx\logs\cryptoalpha.vip.error.log -Tail 100

# 实时监控错误日志
Get-Content C:\nginx\logs\cryptoalpha.vip.error.log -Wait
```

## 性能优化

### 启用Gzip压缩

配置文件中已包含gzip设置：

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
```

### 静态文件缓存

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 安全建议

1. **定期更新Nginx**：保持Nginx版本最新
2. **限制访问**：配置IP白名单（如需要）
3. **监控日志**：定期检查异常访问
4. **备份配置**：定期备份nginx.conf
5. **SSL评级**：使用 [SSL Labs](https://www.ssllabs.com/ssltest/) 测试SSL配置

## 完成检查清单

- [ ] Nginx配置文件已部署
- [ ] SSL证书已配置
- [ ] 防火墙规则已添加
- [ ] Nginx配置测试通过
- [ ] Nginx已重启
- [ ] HTTP自动重定向到HTTPS
- [ ] Webhook端点可访问
- [ ] 网站HTTPS访问正常
- [ ] GitHub Webhook测试成功
- [ ] SSL证书自动续期已配置

## 相关文档

- [Nginx官方文档](https://nginx.org/en/docs/)
- [Let's Encrypt文档](https://letsencrypt.org/docs/)
- [GitHub Webhooks文档](https://docs.github.com/en/webhooks)

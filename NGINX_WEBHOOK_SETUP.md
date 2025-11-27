# Nginx Webhook反向代理配置指南

## 配置说明

本配置将GitHub Webhook服务通过Nginx反向代理，使用HTTPS安全连接。

**架构：**
```
GitHub Actions → HTTPS → Nginx (443) → HTTP → Webhook Service (9000)
```

**优势：**
- ✅ 只需开放80/443端口，无需额外开放9000端口
- ✅ 使用HTTPS加密传输
- ✅ 统一域名管理
- ✅ 更安全（内部端口不对外暴露）

## 部署步骤

### 1. 更新Nginx配置

在Windows服务器上，将项目中的`nginx.conf`复制到Nginx配置目录：

```powershell
# 假设Nginx安装在 C:\nginx
cd C:\trading_dashboard_fixed
copy nginx.conf C:\nginx\conf\sites-available\cryptoalpha.vip.conf

# 或者直接编辑Nginx主配置文件
notepad C:\nginx\conf\nginx.conf
```

**关键配置片段：**
```nginx
# GitHub Webhook代理（自动部署）
location /webhook {
    proxy_pass http://localhost:9000/webhook;
    proxy_http_version 1.1;
    
    # 代理头设置
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-GitHub-Event $http_x_github_event;
    
    # 超时设置（Webhook部署可能需要较长时间）
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
```

### 2. 测试Nginx配置

```powershell
# 测试配置文件语法
C:\nginx\nginx.exe -t

# 重新加载配置
C:\nginx\nginx.exe -s reload
```

### 3. 配置SSL证书

**方案A：使用Let's Encrypt（推荐）**

在Windows上可以使用`win-acme`工具：
1. 下载：https://github.com/win-acme/win-acme/releases
2. 运行`wacs.exe`
3. 选择域名：cryptoalpha.vip
4. 自动配置SSL证书

**方案B：使用云服务商SSL证书**

如果您的域名在阿里云/腾讯云，可以免费申请SSL证书，然后配置到Nginx。

### 4. 验证Webhook服务

确保Webhook服务正在运行：

```powershell
pm2 list
pm2 logs webhook-deploy-server
```

### 5. 测试完整流程

在本地测试Webhook是否可访问：

```powershell
# 测试本地连接
curl http://localhost:9000/webhook

# 测试Nginx代理
curl https://cryptoalpha.vip/webhook
```

### 6. 推送代码触发自动部署

配置完成后，推送代码到GitHub将自动触发部署：

```
GitHub Push → GitHub Actions → HTTPS POST → Nginx → Webhook Service → 自动部署
```

## 故障排查

### 问题1：502 Bad Gateway

**原因：** Webhook服务未启动

**解决：**
```powershell
pm2 restart webhook-deploy-server
pm2 logs webhook-deploy-server
```

### 问题2：504 Gateway Timeout

**原因：** 部署时间过长，Nginx超时

**解决：** 已在配置中设置300秒超时，通常足够

### 问题3：SSL证书错误

**原因：** SSL证书未配置或已过期

**解决：** 按照步骤3配置SSL证书

## 安全建议

1. **限制Webhook访问来源**（可选）

可以在Nginx中限制只允许GitHub IP访问：

```nginx
location /webhook {
    # GitHub Webhook IP ranges
    allow 192.30.252.0/22;
    allow 185.199.108.0/22;
    allow 140.82.112.0/20;
    deny all;
    
    proxy_pass http://localhost:9000/webhook;
    # ... 其他配置
}
```

2. **添加Webhook密钥验证**

在GitHub仓库设置中配置Webhook Secret，在webhook-deploy-server.cjs中验证签名。

3. **监控部署日志**

定期检查部署日志，及时发现异常：

```powershell
pm2 logs webhook-deploy-server --lines 100
```

## 相关文件

- `nginx.conf` - Nginx完整配置文件
- `webhook-deploy-server.cjs` - Webhook服务脚本
- `.github/workflows/deploy.yml` - GitHub Actions配置
- `deploy-auto.ps1` - 自动部署脚本

## 测试清单

- [ ] Nginx配置语法正确
- [ ] SSL证书已配置
- [ ] Webhook服务正在运行
- [ ] 本地可以访问 http://localhost:9000/webhook
- [ ] 公网可以访问 https://cryptoalpha.vip/webhook
- [ ] GitHub Actions可以成功触发Webhook
- [ ] 自动部署流程完整执行
- [ ] Telegram收到部署通知

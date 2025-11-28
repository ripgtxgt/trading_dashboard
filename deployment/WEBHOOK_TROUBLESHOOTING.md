# Webhook自动部署故障排查指南

## 问题现象

GitHub Actions部署失败，错误信息：
```
❌ 部署失败！
版本号: 810ddb7
提交信息: Checkpoint: 添加PM2开机自启动完整配置指南...
失败原因: 请检查 GitHub Actions 日志获取详细信息
```

从GitHub Actions日志可以看到：
- ✅ Run Tests: 28s (成功)
- ❌ Deploy to Server: 2m 24s (失败)
- 具体失败步骤：**Trigger Webhook Deployment** (2m 13s后超时)

## 根本原因

Webhook服务器（http://13.113.194.218:9000/webhook）没有正确响应GitHub Actions的POST请求，可能原因：

1. **Webhook服务未运行**
   - PM2进程`webhook-deploy-server`已停止
   - 服务启动失败

2. **端口未开放**
   - Windows防火墙阻止9000端口
   - Lightsail防火墙未开放9000端口

3. **服务器资源不足**
   - 内存不足导致服务无响应
   - CPU占用过高

4. **脚本执行错误**
   - deploy-auto.ps1脚本执行失败
   - PowerShell权限不足

5. **网络问题**
   - GitHub Actions无法访问服务器
   - DNS解析问题

## 快速诊断步骤

### 1. 检查Webhook服务状态

登录Windows服务器，运行：

```powershell
cd C:\trading_dashboard_fixed
pm2 list
```

查看`webhook-deploy-server`的状态：
- **online**: 服务正常运行
- **stopped**: 服务已停止 → 需要启动
- **errored**: 服务启动失败 → 查看日志

### 2. 查看Webhook服务日志

```powershell
pm2 logs webhook-deploy-server --lines 50
```

常见错误：
- `Error: listen EADDRINUSE: address already in use :::9000` → 端口被占用
- `SyntaxError: Cannot use import statement outside a module` → 文件扩展名错误
- `Error: spawn powershell ENOENT` → PowerShell路径问题

### 3. 测试Webhook端点

在服务器本地测试：

```powershell
# 测试Webhook是否响应
curl http://localhost:9000/webhook -Method POST -ContentType "application/json" -Body '{}'
```

预期响应：
```json
{"success": true, "message": "Deployment triggered"}
```

### 4. 测试外网访问

在本地电脑测试：

```bash
curl -X POST http://13.113.194.218:9000/webhook \
  -H "Content-Type: application/json" \
  -d '{}'
```

如果超时或连接失败 → 防火墙问题

### 5. 检查防火墙规则

**Windows防火墙：**
```powershell
# 检查9000端口规则
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*9000*"}

# 如果没有规则，添加：
New-NetFirewallRule -DisplayName "Allow Port 9000" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow
```

**Lightsail防火墙：**
1. 登录AWS Lightsail控制台
2. 选择实例 → 网络 → 防火墙
3. 确认有规则：**TCP 9000** (自定义)

### 6. 检查PM2进程数量

```powershell
pm2 list
```

如果有6个服务（trading-dashboard, trading-bot, telegram-bot, websocket-server, daily-report, webhook-deploy-server），说明配置正确。

### 7. 检查部署脚本

```powershell
# 手动测试部署脚本
cd C:\trading_dashboard_fixed\deployment
.\deploy-auto.ps1
```

观察是否有错误输出。

## 常见问题和解决方案

### 问题1：Webhook服务未运行

**症状：**
```
pm2 list
webhook-deploy-server │ stopped
```

**解决方案：**
```powershell
cd C:\trading_dashboard_fixed
pm2 start ecosystem.config.cjs --only webhook-deploy-server
pm2 save
```

### 问题2：端口被占用

**症状：**
```
Error: listen EADDRINUSE: address already in use :::9000
```

**解决方案：**
```powershell
# 查找占用9000端口的进程
netstat -ano | findstr :9000

# 终止进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F

# 重启Webhook服务
pm2 restart webhook-deploy-server
```

### 问题3：ES Module错误

**症状：**
```
SyntaxError: Cannot use import statement outside a module
```

**解决方案：**
确认文件名是`webhook-deploy-server.cjs`（不是.js）：
```powershell
cd C:\trading_dashboard_fixed\deployment
dir webhook-deploy-server.*
```

如果是.js，重命名为.cjs：
```powershell
ren webhook-deploy-server.js webhook-deploy-server.cjs
```

### 问题4：防火墙阻止

**症状：**
本地curl成功，外网curl失败

**解决方案：**
```powershell
# 添加Windows防火墙规则
New-NetFirewallRule -DisplayName "Trading Dashboard Webhook" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow

# 验证规则
Get-NetFirewallRule -DisplayName "Trading Dashboard Webhook"
```

同时检查Lightsail控制台防火墙设置。

### 问题5：PowerShell执行策略限制

**症状：**
```
deploy-auto.ps1 cannot be loaded because running scripts is disabled
```

**解决方案：**
```powershell
# 设置执行策略（以管理员身份运行）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

# 或者临时绕过
powershell -ExecutionPolicy Bypass -File .\deployment\deploy-auto.ps1
```

### 问题6：Git权限问题

**症状：**
```
fatal: could not read Username for 'https://github.com'
```

**解决方案：**
```powershell
# 配置Git凭证
cd C:\trading_dashboard_fixed
git config credential.helper store
git pull  # 输入用户名和密码，会被保存
```

### 问题7：PM2服务全部停止

**症状：**
部署后所有PM2服务都变成stopped

**原因：**
deploy-auto.ps1使用了`pm2 stop all && pm2 delete all`

**解决方案：**
已在v810ddb7修复，使用`pm2 restart`代替。如果仍然出现，手动启动：
```powershell
cd C:\trading_dashboard_fixed
pm2 start ecosystem.config.cjs
pm2 save
```

## 完整修复流程

如果Webhook部署失败，按以下顺序执行：

### 步骤1：诊断问题

```powershell
# 运行诊断脚本
cd C:\trading_dashboard_fixed\deployment
.\diagnose.ps1
```

### 步骤2：重启Webhook服务

```powershell
cd C:\trading_dashboard_fixed
pm2 restart webhook-deploy-server
pm2 logs webhook-deploy-server --lines 20
```

### 步骤3：测试Webhook响应

```powershell
# 本地测试
curl http://localhost:9000/webhook -Method POST -ContentType "application/json" -Body '{}'

# 如果成功，测试外网访问（在本地电脑运行）
curl -X POST http://13.113.194.218:9000/webhook -H "Content-Type: application/json" -d '{}'
```

### 步骤4：检查防火墙

```powershell
# Windows防火墙
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*9000*"}

# 如果没有规则
New-NetFirewallRule -DisplayName "Trading Dashboard Webhook" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow
```

同时检查Lightsail防火墙是否开放TCP 9000端口。

### 步骤5：手动部署测试

```powershell
cd C:\trading_dashboard_fixed
git pull origin main
pnpm install
pnpm build
pm2 restart all
```

### 步骤6：重新触发GitHub Actions

在GitHub仓库做一个小改动（如修改README），推送到main分支，观察GitHub Actions是否成功。

## 监控和维护

### 定期检查服务状态

创建定时任务每小时检查一次：

```powershell
# 创建检查脚本 check_services.ps1
$services = pm2 jlist | ConvertFrom-Json
$offline = $services | Where-Object { $_.pm2_env.status -ne "online" }

if ($offline.Count -gt 0) {
    Write-Host "WARNING: $($offline.Count) services are offline"
    pm2 restart all
}
```

### 查看部署历史

```powershell
# 查看最近5次部署
cd C:\trading_dashboard_fixed\deployment
Get-Content deploy-history.json | ConvertFrom-Json | Select-Object -Last 5
```

### 查看Webhook日志

```powershell
pm2 logs webhook-deploy-server --lines 100
```

## 紧急回滚

如果部署失败导致网站无法访问：

```powershell
cd C:\trading_dashboard_fixed

# 查看可用版本
git log --oneline -5

# 回滚到上一个版本（c4b6eaa）
git reset --hard c4b6eaa
pnpm install
pnpm build
pm2 restart all

# 或使用回滚脚本
.\deployment\rollback.ps1 -version c4b6eaa
```

## 获取帮助

如果以上方法都无法解决问题：

1. **查看完整日志：**
   ```powershell
   pm2 logs webhook-deploy-server --lines 200 > webhook.log
   pm2 logs trading-dashboard --lines 200 > dashboard.log
   ```

2. **导出诊断信息：**
   ```powershell
   .\deployment\diagnose.ps1 > diagnostic_report.txt
   ```

3. **检查GitHub Actions详细日志：**
   访问 https://github.com/ripgtxgt/trading_dashboard/actions
   点击失败的workflow → Deploy to Server → 查看详细错误

4. **联系技术支持：**
   提供以上日志文件和诊断报告

## 预防措施

### 1. 配置PM2自动重启

```powershell
pm2 startup
pm2 save
```

### 2. 配置Webhook服务监控

在`ecosystem.config.cjs`中已配置：
```javascript
{
  name: 'webhook-deploy-server',
  max_restarts: 10,
  min_uptime: '10s',
  autorestart: true
}
```

### 3. 定期备份

```powershell
# 每周备份一次
cd C:\
Compress-Archive -Path trading_dashboard_fixed -DestinationPath "backup_$(Get-Date -Format 'yyyyMMdd').zip"
```

### 4. 监控磁盘空间

```powershell
Get-PSDrive C | Select-Object Used,Free
```

确保至少有5GB可用空间。

## 总结

Webhook自动部署失败的最常见原因：
1. ✅ Webhook服务未运行 → `pm2 restart webhook-deploy-server`
2. ✅ 防火墙阻止9000端口 → 添加防火墙规则
3. ✅ 部署脚本执行失败 → 查看PM2日志
4. ✅ Git权限问题 → 配置凭证存储

按照本文档的诊断步骤，可以快速定位并解决问题。

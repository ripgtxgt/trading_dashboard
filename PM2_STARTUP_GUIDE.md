# PM2开机自启动配置指南

本文档说明如何配置PM2在Windows服务器重启后自动启动所有服务。

---

## 🎯 目标

确保Windows服务器重启后，以下服务自动启动：
- trading-dashboard (Web前端)
- trading-bot (交易机器人)
- telegram-bot (Telegram通知)
- websocket-server (实时数据推送)
- daily-report (每日报告)
- webhook-deploy-server (自动部署服务)

---

## 📋 配置步骤

### 方法1：使用PM2 Startup (推荐)

```powershell
# 1. 生成PM2启动脚本
pm2 startup

# 2. 按照输出的提示执行命令（通常需要管理员权限）
# 示例输出：
# [PM2] You have to run this command as administrator:
# pm2 startup windows -u Administrator --hp C:\Users\Administrator

# 3. 保存当前PM2进程列表
pm2 save

# 4. 验证配置
# 重启服务器后检查PM2服务是否自动启动
pm2 list
```

### 方法2：使用Windows任务计划程序

如果方法1不可用，可以使用Windows任务计划程序：

```powershell
# 1. 创建启动脚本
$startupScript = @"
@echo off
cd /d C:\trading_dashboard_fixed
pm2 resurrect
"@

# 保存到文件
$startupScript | Out-File -FilePath "C:\trading_dashboard_fixed\pm2-startup.bat" -Encoding ASCII

# 2. 创建任务计划
$action = New-ScheduledTaskAction -Execute "C:\trading_dashboard_fixed\pm2-startup.bat"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "Administrator" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "PM2 Startup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Start PM2 processes on system startup"

# 3. 测试任务
Start-ScheduledTask -TaskName "PM2 Startup"

# 4. 验证
pm2 list
```

### 方法3：使用pm2-windows-service (最稳定)

```powershell
# 1. 安装pm2-windows-service
npm install -g pm2-windows-service

# 2. 配置PM2服务
pm2-service-install -n PM2

# 3. 启动服务
Start-Service PM2

# 4. 设置服务自动启动
Set-Service -Name PM2 -StartupType Automatic

# 5. 保存PM2进程列表
pm2 save

# 6. 验证服务状态
Get-Service PM2
pm2 list
```

---

## ✅ 验证配置

### 1. 检查PM2服务状态

```powershell
pm2 list
```

应该看到所有6个服务都显示为`online`。

### 2. 测试重启

```powershell
# 重启服务器
Restart-Computer

# 重启后登录，检查服务
pm2 list
```

### 3. 检查服务日志

```powershell
pm2 logs --lines 20
```

---

## 🔧 故障排除

### 问题1：重启后PM2进程列表为空

**解决方案：**
```powershell
# 恢复保存的进程列表
pm2 resurrect

# 如果没有保存的进程列表，重新启动
pm2 start ecosystem.config.cjs
pm2 save
```

### 问题2：PM2服务未自动启动

**解决方案：**
```powershell
# 检查任务计划是否存在
Get-ScheduledTask -TaskName "PM2*"

# 或检查Windows服务
Get-Service PM2 -ErrorAction SilentlyContinue

# 重新配置启动脚本
pm2 startup
```

### 问题3：部分服务启动失败

**解决方案：**
```powershell
# 查看失败的服务日志
pm2 logs <service-name> --lines 50

# 重启失败的服务
pm2 restart <service-name>

# 或重启所有服务
pm2 restart all
```

---

## 📝 注意事项

1. **管理员权限**：配置PM2开机自启动需要管理员权限
2. **环境变量**：确保`.env`文件存在于`C:\trading_dashboard_fixed`目录
3. **依赖检查**：确保Node.js、Python和所有依赖已正确安装
4. **防火墙规则**：确保必要的端口（3000, 9000等）已开放
5. **定期测试**：建议每月测试一次服务器重启，确保自动启动正常工作

---

## 🚀 推荐配置

对于生产环境，推荐使用**方法3（pm2-windows-service）**，因为：
- ✅ 作为Windows服务运行，最稳定
- ✅ 自动处理用户登录/登出
- ✅ 系统级别的进程管理
- ✅ 更好的日志和错误处理

---

## 📞 获取帮助

如果遇到问题：
1. 查看PM2日志：`pm2 logs --lines 100`
2. 查看Windows事件查看器：`eventvwr.msc`
3. 检查PM2配置：`pm2 show <service-name>`
4. 重新安装PM2：`npm uninstall -g pm2 && npm install -g pm2`

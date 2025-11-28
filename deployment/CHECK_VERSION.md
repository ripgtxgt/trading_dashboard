# 服务器版本检查指南

## 方法1：通过Git命令查看（推荐）

登录Windows服务器后，在项目目录执行：

```powershell
cd C:\trading_dashboard_fixed
git log -1 --oneline
```

输出示例：
```
810ddb7 Checkpoint: 添加PM2开机自启动完整配置指南...
```

前面的 `810ddb7` 就是当前版本号（短SHA）。

## 方法2：查看部署历史文件

```powershell
cd C:\trading_dashboard_fixed\deployment
Get-Content deploy-history.json | ConvertFrom-Json | Select-Object -Last 1
```

这会显示最后一次成功部署的版本信息。

## 方法3：通过Webhook服务查询

在浏览器访问：
```
http://13.113.194.218:9000/history
```

会显示所有部署历史记录，包括版本号、时间戳、状态等。

## 方法4：查看PM2日志

```powershell
pm2 logs webhook-deploy-server --lines 50
```

查看最近的部署日志，可以看到部署的版本号和执行结果。

## 检查部署失败原因

### 1. 查看GitHub Actions日志

访问：https://github.com/ripgtxgt/trading_dashboard/actions

点击最新的workflow运行记录，查看详细错误信息。

### 2. 查看服务器Webhook日志

```powershell
pm2 logs webhook-deploy-server --lines 100
```

### 3. 查看部署脚本日志

```powershell
Get-Content C:\trading_dashboard_fixed\deployment\deploy.log -Tail 50
```

### 4. 检查所有服务状态

```powershell
pm2 list
```

查看哪些服务是online，哪些是stopped或errored。

### 5. 查看具体服务日志

```powershell
pm2 logs trading-dashboard --lines 50
pm2 logs trading-bot --lines 50
pm2 logs websocket-server --lines 50
pm2 logs telegram-bot --lines 50
```

## 常见部署失败原因

1. **依赖安装失败**
   - 检查：`pm2 logs webhook-deploy-server`
   - 解决：手动运行 `pnpm install`

2. **构建失败**
   - 检查：`pm2 logs webhook-deploy-server`
   - 解决：手动运行 `pnpm build`

3. **PM2重启失败**
   - 检查：`pm2 list`
   - 解决：手动运行 `pm2 restart all`

4. **Git拉取失败**
   - 检查：`git status`
   - 解决：手动运行 `git pull origin main`

5. **权限问题**
   - 检查：文件权限
   - 解决：以管理员身份运行PowerShell

## 快速诊断命令

在Windows服务器上运行以下命令进行全面诊断：

```powershell
# 检查当前版本
cd C:\trading_dashboard_fixed
Write-Host "=== Current Version ===" -ForegroundColor Cyan
git log -1 --oneline

# 检查Git状态
Write-Host "`n=== Git Status ===" -ForegroundColor Cyan
git status

# 检查PM2服务状态
Write-Host "`n=== PM2 Services ===" -ForegroundColor Cyan
pm2 list

# 检查最近的部署日志
Write-Host "`n=== Recent Deployment Logs ===" -ForegroundColor Cyan
pm2 logs webhook-deploy-server --lines 20 --nostream

# 检查Nginx状态
Write-Host "`n=== Nginx Status ===" -ForegroundColor Cyan
Get-Process nginx -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime
```

将以上命令保存为 `diagnose.ps1`，然后运行：
```powershell
.\diagnose.ps1
```

## 手动回滚到上一版本

如果部署失败，可以手动回滚：

```powershell
cd C:\trading_dashboard_fixed
git log --oneline -5  # 查看最近5个版本
git reset --hard c4b6eaa  # 回滚到上一个版本（c4b6eaa）
pnpm install
pnpm build
pm2 restart all
```

或使用回滚脚本：
```powershell
.\deployment\rollback.ps1 -version c4b6eaa
```

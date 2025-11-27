# Trading Dashboard 部署指南

## 自动部署系统

### 工作流程

1. **代码推送** → GitHub仓库
2. **自动测试** → GitHub Actions运行测试
3. **测试通过** → 触发Webhook部署
4. **自动部署** → 服务器拉取代码并重启
5. **验证检测** → 检查网站是否正常访问
6. **Telegram通知** → 发送部署结果

### 部署历史

所有部署记录保存在：`C:\trading_dashboard_fixed\deploy-history.json`

查看部署历史：
```powershell
# 方法1：直接查看JSON文件
type C:\trading_dashboard_fixed\deploy-history.json

# 方法2：通过HTTP接口查询
curl http://localhost:9000/history

# 方法3：通过Nginx代理查询
curl https://cryptoalpha.vip/webhook/history
```

部署历史包含：
- 时间戳
- 提交SHA
- 提交信息
- 作者
- 状态（success/failed）
- 耗时（秒）

---

## 一键回滚功能

### 快速回滚到上一版本

```powershell
cd C:\trading_dashboard_fixed
.\rollback.ps1
```

### 回滚到指定版本

```powershell
# 回滚到指定提交
.\rollback.ps1 -Version <commit-sha>

# 回滚到上上个版本
.\rollback.ps1 -Version HEAD~2

# 强制回滚（不需要确认）
.\rollback.ps1 -Version HEAD~1 -Force
```

### 回滚流程

1. 显示当前版本和目标版本
2. 确认回滚操作
3. 保存当前提交SHA（用于恢复）
4. 停止所有PM2服务
5. 回滚代码到目标版本
6. 安装依赖
7. 构建项目
8. 复制构建文件
9. 重启所有服务
10. 显示回滚结果

### 恢复回滚

如果回滚后发现问题，可以恢复到回滚前的版本：

```powershell
# 脚本会提示恢复命令，例如：
.\rollback.ps1 -Version <original-commit-sha> -Force
```

---

## Telegram通知

### 通知类型

**1. 测试失败通知**
```
❌ 测试失败，部署已取消！

仓库: ripgtxgt/trading_dashboard
分支: main
提交: abc123...
作者: username

请修复测试错误后重新提交。
```

**2. 部署成功通知**
```
✅ 部署成功！

📦 版本信息
• 版本号: abc123
• 提交信息: fix: 修复bug
• 作者: username

⏱️ 部署统计
• 触发耗时: 5秒
• 部署时间: 2025-11-27 20:00:00
• 验证状态: success

🌐 访问地址
https://cryptoalpha.vip
```

**3. 部署失败通知**
```
❌ 部署失败！

📦 版本信息
• 版本号: abc123
• 提交信息: feat: 新功能
• 作者: username

⚠️ 失败原因
请检查 GitHub Actions 日志获取详细信息。

🔄 建议操作
1. 查看错误日志
2. 修复问题后重新提交
3. 或执行回滚命令恢复上一版本
```

---

## 部署验证

### 自动验证检查

部署完成后，系统会自动执行以下验证：

1. **网站可访问性检查**
   - 访问 `https://cryptoalpha.vip/`
   - 检查HTTP状态码是否为200
   - 最多重试5次，每次间隔10秒

2. **服务健康检查**
   - PM2进程是否正常运行
   - 所有服务是否在线

### 手动验证

```powershell
# 检查PM2服务状态
pm2 list

# 查看服务日志
pm2 logs

# 检查网站访问
curl https://cryptoalpha.vip/

# 查看部署日志
type C:\trading_dashboard_fixed\webhook-deploy.log

# 查看部署历史
curl http://localhost:9000/history
```

---

## 故障排查

### 部署失败

**1. 查看GitHub Actions日志**
- 访问：https://github.com/ripgtxgt/trading_dashboard/actions
- 查看最新workflow运行详情
- 检查测试步骤或部署步骤的错误信息

**2. 查看服务器日志**
```powershell
# Webhook服务日志
pm2 logs webhook-deploy-server

# 部署日志
type C:\trading_dashboard_fixed\webhook-deploy.log

# 所有服务日志
pm2 logs
```

**3. 手动部署**
```powershell
cd C:\trading_dashboard_fixed
git pull github main
.\deploy-auto.ps1
```

### 回滚失败

**1. 检查错误信息**
- 回滚脚本会显示详细错误信息
- 根据提示进行修复

**2. 手动回滚**
```powershell
cd C:\trading_dashboard_fixed

# 停止服务
pm2 stop all

# 回滚代码
git reset --hard <commit-sha>

# 安装依赖
pnpm install

# 构建
pnpm build

# 复制文件
Copy-Item -Path "dist/public/*" -Destination "server/_core/public" -Recurse -Force

# 重启服务
pm2 restart all
```

### 服务无法启动

**1. 检查端口占用**
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :9000
```

**2. 检查依赖安装**
```powershell
cd C:\trading_dashboard_fixed
pnpm install
```

**3. 重启所有服务**
```powershell
pm2 delete all
pm2 start ecosystem.config.cjs
pm2 save
```

---

## 最佳实践

### 部署前

1. ✅ 在本地运行测试：`pnpm test`
2. ✅ 确保代码已提交并推送
3. ✅ 检查Telegram Bot是否在线

### 部署中

1. ✅ 关注Telegram通知
2. ✅ 查看GitHub Actions执行状态
3. ✅ 监控服务器日志

### 部署后

1. ✅ 验证网站是否正常访问
2. ✅ 检查核心功能是否正常
3. ✅ 查看部署历史记录
4. ✅ 如有问题，立即执行回滚

### 紧急情况

**快速回滚三步骤：**

```powershell
cd C:\trading_dashboard_fixed
.\rollback.ps1 -Force
pm2 logs
```

---

## 配置文件

### GitHub Actions配置

文件：`.github/workflows/deploy.yml`

关键配置：
- 测试步骤：运行`pnpm test`
- 部署触发：POST请求到Webhook
- 验证检查：检查网站可访问性
- Telegram通知：成功/失败通知

### Webhook服务配置

文件：`webhook-deploy-server.cjs`

关键配置：
- 端口：9000
- 项目路径：`C:\trading_dashboard_fixed`
- 日志文件：`webhook-deploy.log`
- 历史文件：`deploy-history.json`

### Nginx配置

文件：`C:\nginx\conf\nginx.conf`

关键配置：
```nginx
location /webhook {
    proxy_pass http://localhost:9000/webhook;
    # ... 其他配置
}
```

---

## 联系支持

如遇到无法解决的问题，请：

1. 收集日志信息
2. 记录错误截图
3. 联系技术支持

**日志收集命令：**

```powershell
# 导出所有日志
pm2 logs --lines 100 > C:\logs_export.txt
type C:\trading_dashboard_fixed\webhook-deploy.log >> C:\logs_export.txt
curl http://localhost:9000/history >> C:\logs_export.txt
```

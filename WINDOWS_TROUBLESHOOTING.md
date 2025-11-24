# Windows 部署故障排除指南

本文档列出了在Windows Server上部署时可能遇到的常见问题及解决方案。

---

## 目录

1. [Python依赖安装问题](#python依赖安装问题)
2. [数据库连接问题](#数据库连接问题)
3. [端口占用问题](#端口占用问题)
4. [权限问题](#权限问题)
5. [防火墙问题](#防火墙问题)

---

## Python依赖安装问题

### 问题：ta-lib 安装失败

**错误信息**：
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**原因**：ta-lib 需要 C++ 编译器来构建，Windows 上默认没有安装。

**解决方案（三选一）**：

#### 方案一：使用替代库（推荐）

ta-lib 已在 `requirements.txt` 中注释掉。如果需要技术指标分析，使用纯 Python 实现的替代库：

```powershell
pip install pandas-ta
```

pandas-ta 提供了与 ta-lib 类似的技术指标，但不需要编译。

#### 方案二：安装预编译版本

1. 访问 https://github.com/cgohlke/talib-build/releases
2. 下载对应 Python 版本的 `.whl` 文件（例如：`TA_Lib-0.4.28-cp311-cp311-win_amd64.whl` 对应 Python 3.11）
3. 安装：
```powershell
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

#### 方案三：安装 Visual Studio Build Tools

1. 下载 Visual Studio Build Tools：https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. 运行安装程序，选择 "Desktop development with C++"
3. 安装完成后重新运行：
```powershell
pip install ta-lib
```

---

## 数据库连接问题

### 问题：数据库访问权限被拒绝

**错误信息**：
```
Error: Access denied for user 'trading'@'localhost' (using password: YES)
```

**解决方案（推荐）**：

使用自动化初始化脚本：

1. **双击运行**：`init_database.bat`
2. **输入 MySQL root 密码**
3. **脚本会自动创建**：
   - 数据库：`trading_dashboard`
   - 用户：`trading`
   - 密码：`trading123`（默认）
4. **复制连接字符串到 .env 文件**

**手动解决方案**：

1. **检查 MySQL 服务是否运行**：
```powershell
Get-Service -Name "MySQL*"
```

如果状态为 Stopped，启动服务：
```powershell
Start-Service MySQL80  # 服务名可能不同，根据实际情况调整
```

2. **手动创建数据库和用户**：

登录 MySQL：
```powershell
mysql -u root -p
```

执行以下 SQL 命令：
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS trading_dashboard
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'trading'@'localhost' IDENTIFIED BY 'trading123';

-- 授权
GRANT ALL PRIVILEGES ON trading_dashboard.* TO 'trading'@'localhost';
FLUSH PRIVILEGES;
```

3. **更新 .env 文件**：

打开 `C:\trading_dashboard\.env`，修改为：
```
DATABASE_URL="mysql://trading:trading123@localhost:3306/trading_dashboard"
```

4. **测试连接**：
```powershell
mysql -u trading -p"trading123" -e "USE trading_dashboard; SELECT 1;"
```

### 问题：数据库迁移失败

**错误信息**：
```
[ERROR] Database migration failed
Please check if DATABASE_URL configuration is correct
```

**解决步骤**：

1. 先运行 `init_database.bat` 初始化数据库
2. 确认 .env 文件中的 DATABASE_URL 配置正确
3. 重新运行 `deploy.bat`

---

## 端口占用问题

### 问题：端口 3000 或 8765 被占用

**错误信息**：
```
[WARNING] Port 3000 is in use
Process: PID 1234
```

**解决步骤**：

1. **查看占用端口的进程**：
```powershell
Get-NetTCPConnection -LocalPort 3000 | Select-Object OwningProcess
```

2. **停止占用进程**：
```powershell
Stop-Process -Id 1234 -Force  # 替换为实际 PID
```

3. **或者修改端口**：

编辑 `.env` 文件，修改端口：
```
PORT=3001  # 使用其他端口
```

---

## 权限问题

### 问题：防火墙规则添加失败

**错误信息**：
```
[WARNING] Firewall configuration failed (may need administrator privileges)
```

**解决方案**：

右键点击 `deploy.bat`，选择 **"以管理员身份运行"**。

或者手动添加防火墙规则：

```powershell
# 以管理员身份运行 PowerShell
New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
```

---

## 防火墙问题

### 问题：无法从外部访问 Web 界面

**检查步骤**：

1. **确认服务正在运行**：
```powershell
pm2 list
```

2. **检查本地访问**：

在服务器浏览器中访问 `http://localhost:3000`，如果可以访问，说明服务正常。

3. **检查防火墙规则**：
```powershell
Get-NetFirewallRule -DisplayName "Trading Dashboard"
```

如果没有规则，添加：
```powershell
New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
```

4. **检查 Windows Defender 防火墙**：

- 打开 "Windows Defender 防火墙"
- 点击 "高级设置"
- 检查 "入站规则" 中是否有 "Trading Dashboard" 规则
- 确保规则状态为 "已启用"

5. **检查云服务器安全组**（如果使用云服务器）：

- 登录云服务商控制台（阿里云、腾讯云、AWS 等）
- 找到 "安全组" 设置
- 添加入站规则：允许 TCP 端口 3000 和 8765

---

## PM2 问题

### 问题：PM2 服务无法启动

**常见错误**：
```
[ERROR] PM2 not installed
```

**解决方案**：

1. **安装 PM2**：
```powershell
npm install -g pm2
npm install -g pm2-windows-startup
```

2. **配置开机自启**：
```powershell
pm2-startup install
```

3. **检查 PM2 服务状态**：
```powershell
pm2 list
pm2 logs
```

---

## Node.js 版本问题

### 问题：Node.js 版本过低

**错误信息**：
```
[WARNING] Node.js version is too old, recommend v18 or higher
```

**解决方案**：

1. 卸载旧版本 Node.js（可选）
2. 下载并安装 Node.js 18 或更高版本：https://nodejs.org/
3. 验证版本：
```powershell
node -v
```

---

## 常用调试命令

### 查看服务日志

```powershell
# 查看所有服务日志
pm2 logs

# 查看特定服务日志
pm2 logs trading-dashboard
pm2 logs websocket-server

# 查看最近 100 行日志
pm2 logs --lines 100
```

### 重启服务

```powershell
# 重启所有服务
pm2 restart all

# 重启特定服务
pm2 restart trading-dashboard
```

### 停止服务

```powershell
# 停止所有服务
pm2 stop all

# 停止特定服务
pm2 stop trading-dashboard
```

### 删除服务

```powershell
# 删除所有服务
pm2 delete all

# 删除特定服务
pm2 delete trading-dashboard
```

---

## 获取帮助

如果以上方案无法解决您的问题，请：

1. 查看详细错误日志：`pm2 logs --err`
2. 检查 `.env` 配置文件
3. 确认所有依赖已正确安装
4. 联系技术支持并提供错误日志

---

**提示**：大部分问题都可以通过 **以管理员身份运行** 和 **检查配置文件** 来解决。

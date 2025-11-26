# Dashboard SQLite集成 - 完整部署指南

## 🚨 问题诊断

您遇到的问题是：**PM2进程列表为空，所有服务都被停止了**

这是因为 `stop_all.bat` 使用了 `pm2 stop all`，但是之前的PM2配置可能不完整或丢失。

---

## 📦 部署文件清单

### 新增文件

#### Python脚本（`C:\trading_dashboard\scripts\`）
- `init_database.py` - 数据库初始化脚本
- `insert_test_data.py` - 测试数据插入脚本

#### Node.js后端（`C:\trading_dashboard\server\`）
- `dashboardRouter.ts` - Dashboard API路由
- `dashboard.test.ts` - API测试文件

#### PM2配置（`C:\trading_dashboard\`）
- `ecosystem.config.js` - PM2进程配置文件（**新增**）
- `start_services.bat` - 启动所有服务（**新增**）
- `stop_services.bat` - 停止所有服务（**新增**）
- `restart_services.bat` - 重启所有服务（**新增**）

### 修改文件

#### Node.js后端
- `server/db.ts` - 添加SQLite数据库支持
- `server/routers.ts` - 注册dashboard路由

---

## 🚀 完整部署步骤

### 步骤1：备份现有文件
```cmd
cd C:\trading_dashboard
copy server\db.ts server\db.ts.backup
copy server\routers.ts server\routers.ts.backup
```

### 步骤2：解压部署文件包
将 `deployment_files.tar.gz` 解压到临时目录，然后复制文件到对应位置：

```cmd
REM 复制Python脚本
copy deployment_files\init_database.py C:\trading_dashboard\scripts\
copy deployment_files\insert_test_data.py C:\trading_dashboard\scripts\

REM 复制Node.js文件
copy deployment_files\dashboardRouter.ts C:\trading_dashboard\server\
copy deployment_files\dashboard.test.ts C:\trading_dashboard\server\
copy deployment_files\db.ts C:\trading_dashboard\server\
copy deployment_files\routers.ts C:\trading_dashboard\server\

REM 复制PM2配置和启动脚本
copy deployment_files\ecosystem.config.js C:\trading_dashboard\
copy deployment_files\start_services.bat C:\trading_dashboard\
copy deployment_files\stop_services.bat C:\trading_dashboard\
copy deployment_files\restart_services.bat C:\trading_dashboard\
```

### 步骤3：安装Node.js依赖
```cmd
cd C:\trading_dashboard
pnpm add better-sqlite3 @types/better-sqlite3
```

### 步骤4：初始化SQLite数据库
```cmd
cd C:\trading_dashboard\scripts
python init_database.py
python insert_test_data.py
```

### 步骤5：启动所有服务
```cmd
cd C:\trading_dashboard
start_services.bat
```

这个脚本会：
1. 检查PM2是否安装
2. 检查配置文件是否存在
3. 创建logs目录
4. 使用 `ecosystem.config.js` 启动所有5个服务：
   - `trading-dashboard` (Node.js Dashboard)
   - `trading-bot` (Python交易机器人)
   - `telegram-bot` (Telegram通知机器人)
   - `websocket-server` (WebSocket服务器)
   - `daily-report` (每日报告生成器)

### 步骤6：验证服务状态
```cmd
pm2 list
```

应该看到5个服务都在运行（status: online）

### 步骤7：检查Dashboard
访问以下任一地址：
- http://localhost:3000
- https://cryptoalpha.vip

应该能看到Dashboard正确显示数据。

---

## 📋 PM2常用命令

### 查看服务状态
```cmd
pm2 list
```

### 查看日志
```cmd
REM 查看所有日志
pm2 logs

REM 查看特定服务日志
pm2 logs trading-dashboard
pm2 logs trading-bot
pm2 logs telegram-bot
pm2 logs websocket-server
pm2 logs daily-report
```

### 重启服务
```cmd
REM 重启所有服务
pm2 restart all

REM 重启特定服务
pm2 restart trading-dashboard
pm2 restart trading-bot
```

### 停止服务
```cmd
REM 停止所有服务
pm2 stop all

REM 停止特定服务
pm2 stop trading-dashboard
```

### 删除服务（完全移除）
```cmd
REM 删除所有服务
pm2 delete all

REM 删除特定服务
pm2 delete trading-dashboard
```

### 保存PM2配置（开机自启）
```cmd
pm2 save
pm2 startup
```

---

## 🔍 故障排查

### 问题1：PM2进程列表为空
**症状：** 运行 `pm2 list` 显示空列表

**解决方案：**
```cmd
cd C:\trading_dashboard
start_services.bat
```

### 问题2：Dashboard显示"数据加载失败"
**症状：** Dashboard打开但显示错误信息

**检查步骤：**
1. 确认SQLite数据库文件存在：
   ```cmd
   dir C:\trading_dashboard\scripts\trading_data.db
   ```

2. 检查Dashboard日志：
   ```cmd
   pm2 logs trading-dashboard
   ```

3. 运行测试：
   ```cmd
   cd C:\trading_dashboard
   pnpm test server/dashboard.test.ts
   ```

### 问题3：Python交易机器人无法启动
**症状：** `pm2 list` 显示 trading-bot 状态为 errored

**检查步骤：**
1. 查看错误日志：
   ```cmd
   pm2 logs trading-bot --err
   ```

2. 检查Python环境：
   ```cmd
   python --version
   pip list | findstr kucoin
   ```

3. 手动运行测试：
   ```cmd
   cd C:\trading_dashboard\scripts
   python v24_strategy.py
   ```

### 问题4：端口被占用
**症状：** Dashboard启动失败，提示端口3000被占用

**解决方案：**
```cmd
REM 查找占用端口的进程
netstat -ano | findstr :3000

REM 结束进程（替换PID为实际进程ID）
taskkill /PID <PID> /F

REM 重新启动服务
pm2 restart trading-dashboard
```

### 问题5：better-sqlite3安装失败
**症状：** `pnpm add better-sqlite3` 报错

**解决方案：**
```cmd
REM 确保安装了Python和Visual Studio Build Tools
REM 使用npm安装（有时比pnpm更稳定）
npm install better-sqlite3 @types/better-sqlite3

REM 或者使用预编译版本
npm install better-sqlite3 --build-from-source=false
```

---

## 📊 服务架构说明

### 服务依赖关系
```
trading-bot (Python)
    ↓ 写入数据
SQLite Database (trading_data.db)
    ↓ 读取数据
trading-dashboard (Node.js)
    ↓ 提供API
Frontend (React)
```

### 数据流向
1. **Python交易机器人** → 执行交易策略 → 写入SQLite数据库
2. **SQLite数据库** → 存储所有交易数据
3. **Node.js Dashboard** → 读取SQLite数据 → 提供tRPC API
4. **React前端** → 调用tRPC API → 显示Dashboard

### 端口使用
- `3000` - Node.js Dashboard (HTTP)
- `8765` - WebSocket服务器
- Telegram Bot - 无端口（使用Telegram API）

---

## ✅ 验证清单

部署完成后，请逐项检查：

- [ ] PM2显示5个服务都在运行（status: online）
- [ ] SQLite数据库文件存在（`C:\trading_dashboard\scripts\trading_data.db`）
- [ ] Dashboard能正常访问（http://localhost:3000）
- [ ] Dashboard显示正确的数据（余额、交易、持仓）
- [ ] 没有错误日志（`pm2 logs` 无ERROR信息）
- [ ] Python交易机器人正常运行（`pm2 logs trading-bot`）
- [ ] Telegram机器人能收到通知

---

## 📞 需要帮助？

如果遇到问题，请提供以下信息：

1. PM2服务状态：`pm2 list`
2. 错误日志：`pm2 logs trading-dashboard --err --lines 50`
3. 数据库文件是否存在：`dir C:\trading_dashboard\scripts\trading_data.db`
4. Node.js版本：`node --version`
5. Python版本：`python --version`

---

## 🎉 部署成功后

恭喜！您的Trading Dashboard现在已经完全集成了SQLite数据库。

**下一步建议：**

1. **配置HTTPS** - 运行 `upgrade_to_https.bat` 为域名配置SSL证书
2. **设置开机自启** - 运行 `pm2 save` 和 `pm2 startup` 保存PM2配置
3. **监控运行状态** - 定期检查 `pm2 logs` 和Dashboard数据显示
4. **备份数据库** - 定期备份 `trading_data.db` 文件

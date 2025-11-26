# Dashboard SQLite集成 - 部署文件清单

## 📦 需要部署到Windows服务器的文件

### 1. 新增文件

#### Python脚本（放到 `C:\trading_dashboard\scripts\`）
- `scripts/init_database.py` - 数据库初始化脚本（创建6个表）
- `scripts/insert_test_data.py` - 测试数据插入脚本

#### Node.js后端（放到 `C:\trading_dashboard\server\`）
- `server/dashboardRouter.ts` - Dashboard API路由（新增）
- `server/dashboard.test.ts` - Dashboard API测试文件（新增）

### 2. 修改的文件

#### Node.js后端
- `server/db.ts` - 添加SQLite数据库支持，修改所有trading函数从SQLite读取
- `server/routers.ts` - 注册dashboardRouter

#### 依赖配置
- `package.json` - 添加better-sqlite3和@types/better-sqlite3依赖

---

## 🚀 部署步骤

### 步骤1：备份现有文件
```powershell
cd C:\trading_dashboard
# 备份现有的db.ts和routers.ts
copy server\db.ts server\db.ts.backup
copy server\routers.ts server\routers.ts.backup
```

### 步骤2：上传新文件
将以下文件上传到Windows服务器：
- `scripts/init_database.py`
- `scripts/insert_test_data.py`
- `server/dashboardRouter.ts`
- `server/dashboard.test.ts`

### 步骤3：替换修改的文件
- 替换 `server/db.ts`
- 替换 `server/routers.ts`

### 步骤4：安装依赖
```powershell
cd C:\trading_dashboard
pnpm add better-sqlite3 @types/better-sqlite3
```

### 步骤5：初始化数据库
```powershell
cd C:\trading_dashboard\scripts
python init_database.py
python insert_test_data.py
```

### 步骤6：重启服务
```cmd
cd C:\trading_dashboard
stop_all.bat
start_all.bat
```

### 步骤7：验证部署
访问 http://localhost:3000 或 https://cryptoalpha.vip 检查Dashboard是否正常显示数据

---

## 📝 文件说明

### scripts/init_database.py
创建SQLite数据库和6个表：
- bot_state（机器人状态）
- positions（持仓信息）
- trades（交易记录）
- balance_snapshots（余额快照）
- klines（K线数据）
- signals（交易信号）

### scripts/insert_test_data.py
插入测试数据用于验证Dashboard显示：
- 1条机器人状态
- 1个当前持仓
- 5笔交易历史
- 24个余额快照
- 100根K线
- 3个交易信号

### server/dashboardRouter.ts
提供完整的Dashboard API：
- getBotState() - 获取机器人状态
- getPositions() - 获取持仓列表
- getTrades() - 获取交易历史
- getBalanceSnapshots() - 获取余额快照
- getKlines() - 获取K线数据
- getSignals() - 获取交易信号
- getStatistics() - 获取统计数据

### server/db.ts（修改）
添加SQLite数据库支持：
- 导入better-sqlite3
- 创建getSqliteDb()函数
- 修改getBotState()从SQLite读取
- 修改getCurrentPosition()从SQLite读取
- 修改getRecentTrades()从SQLite读取
- 修改getBalanceSnapshots()从SQLite读取

### server/routers.ts（修改）
- 导入dashboardRouter
- 注册dashboard路由到appRouter

---

## ⚠️ 注意事项

1. **数据库路径**：SQLite数据库文件位于 `C:\trading_dashboard\scripts\trading_data.db`
2. **Python机器人**：确保Python交易机器人使用 `db_sync.py` 写入同一个SQLite数据库
3. **权限问题**：确保Node.js进程有权限读取SQLite数据库文件
4. **测试数据**：首次部署使用测试数据，实际运行后会被Python机器人的真实数据覆盖

---

## 🔍 故障排查

### Dashboard显示"数据加载失败"
1. 检查SQLite数据库文件是否存在：`C:\trading_dashboard\scripts\trading_data.db`
2. 检查Node.js日志：`pm2 logs trading-dashboard`
3. 运行测试：`pnpm test server/dashboard.test.ts`

### Python机器人无法写入数据库
1. 检查db_sync.py是否正确导入
2. 检查数据库文件权限
3. 查看Python机器人日志：`pm2 logs trading-bot`


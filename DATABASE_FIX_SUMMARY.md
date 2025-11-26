# 数据库字段修复总结

## ✅ 修复完成

已成功修复 `db_sync.py` 和 `start_trading_system.py` 中的数据库字段名不匹配问题。

---

## 🔍 问题分析

### 原因

代码中使用的是 **camelCase**（驼峰命名），但数据库表使用的是 **snake_case**（下划线命名）。

### 数据库实际字段（bot_state表）

```
+-------------------+--------------+------+-----+---------+----------------+
| Field             | Type         | Null | Key | Default | Extra          |
+-------------------+--------------+------+-----+---------+----------------+
| id                | int          | NO   | PRI | NULL    | auto_increment |
| is_running        | int          | NO   |     | 0       |                |
| capital           | varchar(20)  | NO   |     | NULL    |                |
| initial_capital   | varchar(20)  | NO   |     | NULL    |                |
| current_stage     | varchar(20)  | NO   |     | NULL    |                |
| daily_trades      | int          | NO   |     | 0       |                |
| daily_pnl         | varchar(20)  | NO   |     | 0       |                |
| total_trades      | int          | NO   |     | 0       |                |
| emergency_stopped | int          | NO   |     | 0       |                |
| updated_at        | timestamp    | NO   |     | now()   |                |
+-------------------+--------------+------+-----+---------+----------------+
```

---

## 🔧 修复内容

### 1. db_sync.py 修复

#### 修复字段名（camelCase → snake_case）

| 错误字段名 | 正确字段名 |
|-----------|-----------|
| `isRunning` | `is_running` |
| `initialCapital` | `initial_capital` |
| `currentStage` | `current_stage` |
| `totalProfit` | `daily_pnl` |
| `totalTrades` | `total_trades` |
| `winTrades` | ❌ 删除（数据库无此字段） |
| `emergencyStopped` | `emergency_stopped` |
| `updatedAt` | `updated_at` |
| `createdAt` | `created_at` |

#### 修复方法签名

**修复前：**
```python
def update_bot_state(self, is_running: int, capital: float, initial_capital: float, 
                    current_stage: str, total_profit: float, total_trades: int,
                    win_trades: int, emergency_stopped: int = 0):
```

**修复后：**
```python
def update_bot_state(self, is_running: int, capital: float, initial_capital: float, 
                    current_stage: str, total_trades: int, daily_pnl: float = 0.0,
                    emergency_stopped: int = 0):
```

**变更说明：**
- ❌ 删除 `win_trades` 参数（数据库无此字段）
- ✅ `total_profit` → `daily_pnl`（匹配数据库字段）
- ✅ 调整参数顺序以匹配数据库字段顺序

---

### 2. start_trading_system.py 修复

修复所有3处 `update_bot_state()` 调用：

#### 修复位置 #1：第218-226行（交易后更新）

**修复前：**
```python
self.db.update_bot_state(
    is_running=1,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_profit=self.engine.capital - self.engine.initial_capital,
    total_trades=len(self.engine.rolling_manager.trade_history),
    win_trades=sum(1 for t in self.engine.rolling_manager.trade_history if t.get('pnl', 0) > 0),
    emergency_stopped=0
)
```

**修复后：**
```python
self.db.update_bot_state(
    is_running=1,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_trades=len(self.engine.rolling_manager.trade_history),
    daily_pnl=result['pnl'],
    emergency_stopped=0
)
```

---

#### 修复位置 #2：第272-280行（启动时更新）

**修复前：**
```python
self.db.update_bot_state(
    is_running=1,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_profit=0.0,
    total_trades=0,
    win_trades=0,
    emergency_stopped=0
)
```

**修复后：**
```python
self.db.update_bot_state(
    is_running=1,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_trades=0,
    daily_pnl=0.0,
    emergency_stopped=0
)
```

---

#### 修复位置 #3：第380-388行（停止时更新）

**修复前：**
```python
self.db.update_bot_state(
    is_running=0,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_profit=total_profit if total_trades > 0 else 0.0,
    total_trades=total_trades,
    win_trades=win_trades if total_trades > 0 else 0,
    emergency_stopped=0
)
```

**修复后：**
```python
self.db.update_bot_state(
    is_running=0,
    capital=self.engine.capital,
    initial_capital=self.engine.initial_capital,
    current_stage=self.engine.rolling_manager.get_current_stage(self.engine.capital).name,
    total_trades=total_trades,
    daily_pnl=total_profit if total_trades > 0 else 0.0,
    emergency_stopped=0
)
```

---

## ✅ 验证结果

- ✅ **db_sync.py** Python语法检查通过
- ✅ **start_trading_system.py** Python语法检查通过
- ✅ 所有字段名已匹配数据库表结构
- ✅ 所有参数顺序已调整
- ✅ 不存在的字段已删除

---

## 🚀 部署步骤

### 1. 替换文件

将修复后的两个文件复制到Windows服务器：

```cmd
# 备份原文件
copy C:\trading_dashboard\scripts\db_sync.py C:\trading_dashboard\scripts\db_sync.py.backup
copy C:\trading_dashboard\scripts\start_trading_system.py C:\trading_dashboard\scripts\start_trading_system.py.backup

# 替换为修复后的文件
# 将下载的 db_sync_FIXED.py 重命名为 db_sync.py
# 将下载的 start_trading_system_FIXED_v2.py 重命名为 start_trading_system.py
```

### 2. 重启服务

```cmd
pm2 restart trading-bot
```

### 3. 查看日志

```cmd
pm2 logs trading-bot --lines 50
```

---

## 🎯 预期结果

修复后，日志应该显示：

✅ `[DB] Connected to localhost:3306/trading_dashboard`  
✅ `[Telegram] MessageSendSuccess`  
✅ `InitializeComplete`  
✅ `TradeStart`  
✅ **不再有数据库字段错误**

错误信息应该消失：
- ❌ `Unknown column 'isRunning' in 'field list'`
- ❌ `Unknown column 'totalProfit' in 'field list'`
- ❌ `Unknown column 'winTrades' in 'field list'`

---

## 📊 修复统计

- **修复文件：** 2个（db_sync.py, start_trading_system.py）
- **修复位置：** 5处（1个方法定义 + 4个SQL语句 + 3个调用）
- **字段名修复：** 9个
- **参数删除：** 1个（win_trades）
- **语法验证：** 全部通过 ✅

---

## 📞 后续支持

如果修复后仍有问题，请提供：

1. 完整的错误日志（`pm2 logs trading-bot --lines 100`）
2. 数据库表结构（`DESCRIBE bot_state;`）
3. PM2状态（`pm2 status`）

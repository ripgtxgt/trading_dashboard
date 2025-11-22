# Python交易脚本集成说明

## 概述

本文档说明如何将你的Python交易脚本与Web Dashboard集成，实现数据自动同步。

## 数据库同步模块

已创建 `scripts/db_sync.py` 模块，提供以下功能：

### 1. 初始化

```python
from db_sync import DatabaseSync

# 创建数据库连接（自动从环境变量读取DATABASE_URL）
db = DatabaseSync()
if db.connect():
    # 执行数据库操作
    pass
    db.disconnect()
```

### 2. 更新机器人状态

```python
db.update_bot_state(
    is_running=1,          # 1=运行中, 0=已停止
    capital=11.41,         # 当前资金
    initial_capital=10.0,  # 初始资金
    current_stage="stage1",# 当前阶段
    total_profit=1.41,     # 总盈利
    total_trades=5,        # 总交易次数
    win_trades=3,          # 盈利交易次数
    emergency_stopped=0    # 是否紧急停止
)
```

### 3. 创建交易记录

```python
# 开仓时调用
trade_id = db.create_trade(
    symbol="XBTUSDTM",
    side="long",           # "long" 或 "short"
    entry_price=50000.0,
    quantity=0.001,
    leverage=10,
    stage="stage1"
)
```

### 4. 关闭交易记录

```python
# 平仓时调用
db.close_trade(
    trade_id=trade_id,
    exit_price=51000.0,
    pnl=10.0,              # 盈亏金额
    pnl_pct=0.02           # 盈亏百分比 (2%)
)
```

### 5. 更新当前持仓

```python
db.update_position(
    symbol="XBTUSDTM",
    side="long",           # 有持仓时填"long"或"short"，无持仓时填None
    entry_price=50000.0,   # 有持仓时填入场价，无持仓时填None
    quantity=0.001,        # 有持仓时填数量，无持仓时填None
    leverage=10,           # 有持仓时填杠杆，无持仓时填None
    stage="stage1",
    unrealized_pnl=10.0,   # 未实现盈亏
    stop_loss_pct=0.05,    # 止损百分比
    take_profit_pct=0.10   # 止盈百分比
)
```

### 6. 添加余额快照

```python
# 建议每小时或每次交易后调用
db.add_balance_snapshot(balance=11.41)
```

## 集成到你的交易脚本

### 方法1: 修改现有脚本

在 `trading_rolling.py` 中添加：

```python
import os
import sys

# 添加scripts目录到Python路径
sys.path.append(os.path.dirname(__file__))

from db_sync import DatabaseSync

# 在脚本开始时初始化
db = DatabaseSync()
db.connect()

# 在主循环中更新状态
while True:
    # ... 你的交易逻辑 ...
    
    # 更新机器人状态
    db.update_bot_state(
        is_running=1,
        capital=current_balance,
        initial_capital=INITIAL_CAPITAL,
        current_stage=current_stage,
        total_profit=current_balance - INITIAL_CAPITAL,
        total_trades=total_trades_count,
        win_trades=win_trades_count
    )
    
    # 开仓时
    if should_open_position:
        trade_id = db.create_trade(...)
        # 保存trade_id用于后续平仓
    
    # 平仓时
    if should_close_position:
        db.close_trade(trade_id, exit_price, pnl, pnl_pct)
    
    # 更新持仓
    db.update_position(...)
    
    # 添加余额快照（每小时一次）
    if should_snapshot:
        db.add_balance_snapshot(current_balance)
    
    time.sleep(60)

# 脚本结束时
db.disconnect()
```

### 方法2: 使用环境变量

确保运行脚本时设置了 `DATABASE_URL` 环境变量：

```bash
# 从Web项目获取DATABASE_URL
cd /home/ubuntu/trading_dashboard
export DATABASE_URL=$(grep DATABASE_URL .env | cut -d '=' -f2)

# 运行交易脚本
python3 /home/ubuntu/upload/trading_rolling.py
```

## 测试数据同步

运行测试脚本验证连接：

```bash
cd /home/ubuntu/trading_dashboard
export DATABASE_URL=$(grep DATABASE_URL .env | cut -d '=' -f2)
python3 scripts/db_sync.py
```

成功后应该看到：
```
[DB] Connected to xxx.xxx.xxx.xxx:3306/database_name
[DB] Disconnected
```

## 注意事项

1. **数据库连接**：`db_sync.py` 会自动从环境变量 `DATABASE_URL` 读取数据库配置
2. **错误处理**：所有数据库操作都有异常处理，失败不会导致交易脚本崩溃
3. **性能影响**：数据库操作是同步的，建议在交易逻辑之外的时间执行
4. **连接管理**：建议在脚本开始时连接一次，结束时断开，避免频繁连接

## 常见问题

### Q: 如何获取DATABASE_URL?

A: 在Web项目目录执行：
```bash
cd /home/ubuntu/trading_dashboard
cat .env | grep DATABASE_URL
```

### Q: 数据库连接失败怎么办?

A: 检查：
1. DATABASE_URL格式是否正确
2. 数据库服务是否运行
3. 网络连接是否正常

### Q: 需要安装额外的Python包吗?

A: 需要安装 `mysql-connector-python`：
```bash
pip3 install mysql-connector-python
```

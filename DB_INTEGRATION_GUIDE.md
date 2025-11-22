# 数据库集成指南

## 概述

本指南说明如何将Python交易脚本的实时数据同步到MySQL数据库，让Web Dashboard能够显示真实的交易数据。

---

## 核心模块

### db_integration.py

数据库集成模块，提供三个核心功能：

1. **save_trade()** - 保存交易记录
2. **update_position()** - 更新持仓信息
3. **update_account_state()** - 更新账户状态

---

## 快速开始

### 1. 配置数据库连接

数据库连接信息从环境变量`DATABASE_URL`读取，格式：

```
mysql://user:password@host:port/database
```

在Manus平台上，这个环境变量已经自动配置，无需手动设置。

### 2. 在交易脚本中集成

```python
from db_integration import DatabaseIntegration

# 初始化数据库集成
db = DatabaseIntegration()

# 在交易逻辑中调用相应方法
# ...

# 脚本结束时关闭连接
db.close()
```

---

## 使用示例

### 保存交易记录

每次平仓后，调用`save_trade()`保存交易记录：

```python
db.save_trade(
    symbol="XBTUSDTM",          # 交易对
    direction="long",            # 方向：long 或 short
    entry_price=50000.0,         # 入场价格
    exit_price=51000.0,          # 出场价格
    quantity=0.01,               # 交易数量
    pnl=10.0,                    # 盈亏金额（扣除手续费后）
    pnl_pct=2.0,                 # 盈亏百分比
    fee=0.5,                     # 手续费
    entry_time=datetime.now(),   # 入场时间（可选）
    exit_time=datetime.now(),    # 出场时间（可选）
)
```

### 更新持仓信息

开仓或更新持仓时调用：

```python
# 开仓
db.update_position(
    symbol="XBTUSDTM",
    direction="long",            # long/short
    entry_price=50000.0,
    quantity=0.01,
    current_price=50000.0,       # 当前价格（可选）
)

# 平仓（设置为空仓）
db.update_position(
    symbol="XBTUSDTM",
    direction=None,
    entry_price=None,
    quantity=None,
)
```

### 更新账户状态

余额或阶段变化时调用：

```python
db.update_account_state(
    balance=11.0,                # 当前余额
    profit_rate=10.0,            # 盈利率（百分比）
    stage="stage1",              # 当前阶段
    symbol="XBTUSDTM",           # 交易对
)
```

---

## 完整示例

参考`scripts/trading_with_db.py`，这是一个完整的集成示例：

```python
#!/usr/bin/env python3
from db_integration import DatabaseIntegration

class TradingBot:
    def __init__(self):
        self.db = DatabaseIntegration()
        self.balance = 10.0
        self.position = None
    
    def open_position(self, direction, price, quantity):
        """开仓"""
        self.position = {
            "direction": direction,
            "entry_price": price,
            "quantity": quantity,
        }
        
        # 更新数据库
        self.db.update_position(
            symbol="XBTUSDTM",
            direction=direction,
            entry_price=price,
            quantity=quantity,
            current_price=price,
        )
    
    def close_position(self, price):
        """平仓"""
        # 计算盈亏
        if self.position["direction"] == "long":
            pnl = (price - self.position["entry_price"]) * self.position["quantity"]
        else:
            pnl = (self.position["entry_price"] - price) * self.position["quantity"]
        
        fee = abs(pnl) * 0.001
        net_pnl = pnl - fee
        self.balance += net_pnl
        
        # 保存交易记录
        self.db.save_trade(
            symbol="XBTUSDTM",
            direction=self.position["direction"],
            entry_price=self.position["entry_price"],
            exit_price=price,
            quantity=self.position["quantity"],
            pnl=net_pnl,
            pnl_pct=(net_pnl / self.balance) * 100,
            fee=fee,
        )
        
        # 更新持仓为空
        self.db.update_position(
            symbol="XBTUSDTM",
            direction=None,
            entry_price=None,
            quantity=None,
        )
        
        # 更新账户状态
        profit_rate = ((self.balance - 10.0) / 10.0) * 100
        self.db.update_account_state(
            balance=self.balance,
            profit_rate=profit_rate,
            stage="stage1",
        )
        
        self.position = None
    
    def run(self):
        """运行交易逻辑"""
        # 你的交易策略代码
        pass

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
    bot.db.close()
```

---

## 测试数据库集成

运行演示脚本测试数据库集成：

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 trading_with_db.py
```

这将执行3笔模拟交易并写入数据库，然后你可以在Web Dashboard的交易历史和性能报告页面看到这些数据。

---

## 数据库表结构

### trades表

存储所有交易记录：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| symbol | VARCHAR(20) | 交易对 |
| direction | VARCHAR(10) | 方向（long/short） |
| entryPrice | VARCHAR(20) | 入场价格 |
| exitPrice | VARCHAR(20) | 出场价格 |
| quantity | VARCHAR(20) | 交易数量 |
| pnl | VARCHAR(20) | 盈亏金额 |
| pnlPct | VARCHAR(20) | 盈亏百分比 |
| fee | VARCHAR(20) | 手续费 |
| entryTime | TIMESTAMP | 入场时间 |
| exitTime | TIMESTAMP | 出场时间 |

### positions表

存储当前持仓：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| symbol | VARCHAR(20) | 交易对 |
| direction | VARCHAR(10) | 方向（long/short/NULL） |
| entryPrice | VARCHAR(20) | 入场价格 |
| quantity | VARCHAR(20) | 持仓数量 |
| currentPrice | VARCHAR(20) | 当前价格 |
| updatedAt | TIMESTAMP | 更新时间 |

### trading_state表

存储账户状态：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| balance | VARCHAR(20) | 当前余额 |
| profitRate | VARCHAR(20) | 盈利率 |
| stage | VARCHAR(20) | 当前阶段 |
| symbol | VARCHAR(20) | 交易对 |
| updatedAt | TIMESTAMP | 更新时间 |

---

## 注意事项

1. **连接管理**
   - 脚本开始时初始化`DatabaseIntegration()`
   - 脚本结束时调用`db.close()`关闭连接
   - 长期运行的脚本应处理连接断开重连

2. **错误处理**
   - 所有数据库操作都有try-except保护
   - 失败时会打印错误信息但不会中断交易
   - 返回值为True/False表示操作是否成功

3. **数据类型**
   - 价格、数量、盈亏等使用字符串存储，避免浮点精度问题
   - 时间使用datetime对象，自动转换为TIMESTAMP

4. **并发安全**
   - 每个交易脚本实例应有独立的数据库连接
   - 避免多个进程同时写入同一条记录

---

## 集成到现有交易脚本

如果你已经有运行中的交易脚本，按以下步骤集成：

### 步骤1：导入模块

```python
from db_integration import DatabaseIntegration
```

### 步骤2：初始化

在脚本开始处：

```python
db = DatabaseIntegration()
```

### 步骤3：在关键位置添加调用

- **开仓后** → `db.update_position()`
- **平仓后** → `db.save_trade()` + `db.update_position()` + `db.update_account_state()`
- **余额变化** → `db.update_account_state()`

### 步骤4：清理

在脚本结束或异常处理中：

```python
db.close()
```

---

## 故障排查

### 问题：数据库连接失败

**检查**：
- 环境变量`DATABASE_URL`是否正确设置
- 数据库服务是否运行
- 网络连接是否正常

**解决**：
- 在Manus平台上，环境变量自动配置
- 本地开发需要手动设置DATABASE_URL

### 问题：数据未显示在Dashboard

**检查**：
- 交易记录是否成功保存（查看日志）
- 数据库中是否有数据（使用Database管理面板）
- Dashboard是否正确查询数据

**解决**：
- 运行`trading_with_db.py`测试数据写入
- 刷新Dashboard页面
- 检查浏览器控制台错误

---

## 下一步

1. **集成到实盘脚本** - 将数据库集成添加到你的实际交易脚本
2. **监控数据流** - 观察Dashboard实时更新
3. **分析历史数据** - 使用交易历史和性能报告分析策略表现

---

## 支持

如有问题，请查看：
- `scripts/db_integration.py` - 核心模块代码
- `scripts/trading_with_db.py` - 完整示例
- Web Dashboard的Database管理面板 - 查看数据库内容

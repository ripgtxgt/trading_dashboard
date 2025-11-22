# v27.0 功能指南

## 📋 新增功能概览

v27.0版本完成系统最后的完善工作：

1. **统一导航菜单** - 所有页面顶部的导航栏，快速访问各个功能
2. **图表可视化** - 性能报告中的收益曲线、回撤曲线和盈亏柱状图
3. **实盘数据集成** - Python交易脚本实时写入数据库的完整方案

---

## 1. 统一导航菜单

### 功能特性

- ✅ **顶部导航栏** - 固定在页面顶部，始终可见
- ✅ **页面链接** - 控制台、交易历史、性能报告
- ✅ **当前页高亮** - 自动高亮当前所在页面
- ✅ **响应式设计** - 桌面端和移动端自适应
- ✅ **移动端菜单** - 移动设备上的折叠菜单

### 使用方式

导航栏已集成到所有页面：

- **控制台** (`/`) - 主Dashboard，查看实时交易状态
- **交易历史** (`/history`) - 查看历史交易记录
- **性能报告** (`/report`) - 查看日报/周报/月报

点击导航栏中的任意链接即可快速切换页面。

### 技术实现

导航组件位于`client/src/components/Navigation.tsx`，使用wouter进行路由管理，自动检测当前路径并高亮对应菜单项。

---

## 2. 图表可视化

### 功能特性

- ✅ **收益曲线图** - 显示累计盈亏的变化趋势
- ✅ **回撤曲线图** - 分析最大回撤情况
- ✅ **盈亏柱状图** - 每日/每周盈亏分布
- ✅ **交互功能** - 鼠标悬停显示详细数据
- ✅ **响应式布局** - 自适应不同屏幕尺寸

### 访问方式

在性能报告页面（`/report`）中，选择"周报"或"月报"标签，即可看到三个图表：

1. **收益曲线** - 展示累计盈亏如何随时间变化
2. **回撤曲线** - 显示从最高点回撤的百分比
3. **盈亏分布** - 柱状图展示每个时间段的盈亏情况

### 图表说明

#### 收益曲线

- **X轴**：日期或周数
- **Y轴**：累计盈亏（USDT）
- **用途**：观察整体盈利趋势，识别增长阶段和回撤阶段

#### 回撤曲线

- **X轴**：日期或周数
- **Y轴**：回撤百分比（负值）
- **用途**：评估策略的风险，最大回撤越小越好

#### 盈亏柱状图

- **X轴**：日期或周数
- **Y轴**：盈亏金额（USDT）
- **绿色柱**：盈利
- **红色柱**：亏损
- **用途**：识别盈亏分布模式，找出表现最好和最差的时期

### 技术实现

使用recharts图表库，组件位于：

- `client/src/components/ProfitCurveChart.tsx` - 收益曲线
- `client/src/components/DrawdownChart.tsx` - 回撤曲线
- `client/src/components/DailyPnlChart.tsx` - 盈亏柱状图

---

## 3. 实盘数据集成

### 功能特性

- ✅ **数据库写入模块** - `db_integration.py`
- ✅ **交易记录保存** - 每笔交易自动存入数据库
- ✅ **持仓信息同步** - 实时更新持仓状态
- ✅ **账户状态同步** - 余额和盈利率自动更新
- ✅ **错误处理** - 完善的异常处理机制
- ✅ **完整示例** - `trading_with_db.py`

### 核心模块

#### db_integration.py

提供三个核心方法：

```python
from db_integration import DatabaseIntegration

db = DatabaseIntegration()

# 1. 保存交易记录
db.save_trade(
    symbol="XBTUSDTM",
    direction="long",
    entry_price=50000.0,
    exit_price=51000.0,
    quantity=0.01,
    pnl=10.0,
    pnl_pct=2.0,
    fee=0.5,
)

# 2. 更新持仓
db.update_position(
    symbol="XBTUSDTM",
    direction="long",
    entry_price=50000.0,
    quantity=0.01,
    current_price=50500.0,
)

# 3. 更新账户状态
db.update_account_state(
    balance=11.0,
    profit_rate=10.0,
    stage="stage1",
)

db.close()
```

### 集成步骤

#### 步骤1：导入模块

```python
from db_integration import DatabaseIntegration
```

#### 步骤2：初始化

```python
db = DatabaseIntegration()
```

#### 步骤3：在交易逻辑中调用

- **开仓时** → `db.update_position()`
- **平仓时** → `db.save_trade()` + `db.update_position()` + `db.update_account_state()`
- **余额变化** → `db.update_account_state()`

#### 步骤4：清理

```python
db.close()
```

### 完整示例

参考`scripts/trading_with_db.py`：

```python
#!/usr/bin/env python3
from db_integration import DatabaseIntegration

class TradingBot:
    def __init__(self):
        self.db = DatabaseIntegration()
        self.balance = 10.0
    
    def open_position(self, direction, price, quantity):
        self.position = {"direction": direction, "entry_price": price, "quantity": quantity}
        self.db.update_position("XBTUSDTM", direction, price, quantity, price)
    
    def close_position(self, price):
        # 计算盈亏
        pnl = (price - self.position["entry_price"]) * self.position["quantity"]
        self.balance += pnl
        
        # 保存交易
        self.db.save_trade("XBTUSDTM", self.position["direction"], 
                          self.position["entry_price"], price, 
                          self.position["quantity"], pnl, (pnl/self.balance)*100, 0.5)
        
        # 更新持仓为空
        self.db.update_position("XBTUSDTM", None, None, None)
        
        # 更新账户
        self.db.update_account_state(self.balance, ((self.balance-10)/10)*100, "stage1")
    
    def run(self):
        # 你的交易策略
        pass

bot = TradingBot()
bot.run()
bot.db.close()
```

### 测试数据集成

运行演示脚本：

```bash
cd /home/ubuntu/trading_dashboard/scripts
python3 trading_with_db.py
```

这将执行3笔模拟交易并写入数据库，然后在Dashboard中查看结果。

### 数据库配置

数据库连接从环境变量`DATABASE_URL`读取，在Manus平台上自动配置，无需手动设置。

格式：`mysql://user:password@host:port/database`

---

## 数据流程

### 完整数据流

```
Python交易脚本
    ↓
db_integration.py
    ↓
MySQL数据库
    ↓
tRPC API
    ↓
Web Dashboard
```

### 实时更新

1. **交易发生** - Python脚本执行交易
2. **写入数据库** - 调用`db_integration.py`保存数据
3. **Dashboard查询** - tRPC API从数据库读取
4. **页面显示** - React组件渲染数据

---

## 技术栈

### 前端

- **框架**: React 19 + TypeScript
- **样式**: Tailwind CSS 4 + shadcn/ui
- **路由**: wouter
- **图表**: recharts
- **API**: tRPC 11

### 后端

- **框架**: Express 4
- **API**: tRPC 11
- **数据库**: MySQL/TiDB (Drizzle ORM)

### Python集成

- **数据库驱动**: mysql-connector-python
- **集成模块**: db_integration.py

---

## 测试结果

所有20个单元测试通过：

- ✅ 认证测试 (1个)
- ✅ v24功能测试 (11个)
- ✅ 策略参数测试 (5个)
- ✅ 策略回测测试 (3个)

---

## 文档

完整文档请查看：

- `PROJECT_README.md` - 项目总体说明
- `V24_FEATURES_GUIDE.md` - v24.0功能指南
- `V26_FEATURES_GUIDE.md` - v26.0功能指南
- `DB_INTEGRATION_GUIDE.md` - 数据库集成详细指南
- `RISK_MANAGEMENT_GUIDE.md` - 风险管理使用指南

---

## 更新日志

### v27.0 (2024-11-22)

**新增功能**
- 统一导航菜单（顶部导航栏）
- 图表可视化（收益曲线、回撤曲线、盈亏柱状图）
- 实盘数据集成（db_integration.py + trading_with_db.py）

**优化改进**
- 所有页面统一导航体验
- 性能报告增加可视化图表
- 完整的数据库集成方案和文档

**测试**
- 20个单元测试全部通过

---

## 下一步建议

1. **运行演示脚本** - 执行`python3 scripts/trading_with_db.py`测试数据集成
2. **集成到实盘** - 将数据库集成添加到实际交易脚本
3. **监控Dashboard** - 观察实时数据更新和图表变化

---

## 支持

详细使用说明请参考：
- `DB_INTEGRATION_GUIDE.md` - 数据库集成完整指南
- `scripts/db_integration.py` - 核心模块源码
- `scripts/trading_with_db.py` - 完整集成示例
